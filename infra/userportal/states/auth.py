import builtins
from infra.userportal.functions.topology import RivUserPortalFunctionSet
from infra.userportal.states.interfaces import RivStateMachineConstruct
from infra.interfaces import IVpcLandingZone
from aws_cdk import (
  core,
  aws_iam as iam,
  aws_stepfunctions as sf,
  aws_stepfunctions_tasks as sft,
)

class AuthStateMachine(RivStateMachineConstruct):
  def __init__(self, scope: core.Construct, id: builtins.str, landing_zone: IVpcLandingZone, functions: RivUserPortalFunctionSet,state_machine_type:sf.StateMachineType) -> None:
    super().__init__(scope, id, landing_zone, functions, state_machine_type=state_machine_type)

    '''
    Check if this is a valid image...
    '''
    detect = sft.LambdaInvoke(self,'Detect',
      input_path='$.inputRequest',
      result_path='$.detection',
      output_path='$',
      lambda_function=functions.detect_faces.function,
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)    

    '''
    Check if the user exists already within DynamoDB table
    '''
    compare = sft.LambdaInvoke(self,'Compare',
      input_path='$.inputRequest',   
      result_path='$.compare',
      output_path='$',
      lambda_function=functions.search_faces_by_image.function,
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    detect.next(compare)

    '''
    Use output of compare as Match/No-Match. If match -> Return success
    '''
    user_exists = sf.Choice(self,'UserExists')
    user_exists.when(
        condition= sf.Condition.boolean_equals('$.search.Payload.TopMatch.IsCallerUser',True),
        next=sf.Pass(self,'Authentication-Complete',
          parameters={
            'UserId.$': '$.inputRequest.UserId',
            'Status': 'Verified'
          }))

    compare.next(user_exists)
    
    '''
    If not in Dynamo, Search collection to authenticate the users
    '''
    search = sft.LambdaInvoke(self,'Search',
      input_path='$.inputRequest',   
      result_path='$.search',
      output_path='$',
      lambda_function=functions.search_faces_by_image.function,
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    user_exists.otherwise(search)

    '''
    Confirm the caller's has the correct picture
    '''
    is_authenticated = sf.Choice(self,'IsAuthenticated')
    is_authenticated.when(
      condition= sf.Condition.boolean_equals('$.compare.Payload.IsMatch',False),
      next= sf.Fail(self,'InvalidCredentials',
        error='UserAccessDenied',
        cause='The wrong person is in the photo.'))
    
    # Format the message into API Gateway Model
    is_authenticated.otherwise(sf.Pass(self,'Auth-Complete',
      parameters={
        'UserId.$': '$.inputRequest.UserId',
        'Status': 'Verified'
      }))

    '''
    Definition is complete, route it.
    '''
    self.set_state_machine(
        state_machine_name='Riv{}-UserPortal-Auth'.format(self.landing_zone.zone_name),
        definition=detect)
