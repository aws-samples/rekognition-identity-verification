import builtins
from infra.userportal.functions.topology import RivUserPortalFunctionSet
from infra.userportal.states.interfaces import RivStateMachineConstruct
from infra.interfaces import IVpcLandingZone
from aws_cdk import (
  core,
  aws_stepfunctions as sf,
  aws_stepfunctions_tasks as sft,
)

class UpdateStateMachine(RivStateMachineConstruct):
  def __init__(self, scope: core.Construct, id: builtins.str, landing_zone: IVpcLandingZone, functions:RivUserPortalFunctionSet, state_machine_type:sf.StateMachineType) -> None:
    super().__init__(scope, id, landing_zone, functions, state_machine_type=state_machine_type)

    '''
    Check if this is a valid image...
    '''
    detect = sft.LambdaInvoke(self,'Check-ImageQuality',
      lambda_function=functions.detect_faces.function,
      input_path='$.inputRequest',
      result_path='$.detection',
      output_path='$',
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE) 

    '''
    Check if the user exists already within DynamoDB table
    '''
    compare = sft.LambdaInvoke(self,'Compare-CachedFaces',
      input_path='$.inputRequest',   
      result_path='$.compare',
      output_path='$',
      lambda_function=functions.compare_faces.function,
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    detect.next(compare)

    '''
    Update user's profile
    '''
    index = sft.LambdaInvoke(self,'Index-FaceInfo',
      input_path='$.inputRequest',
      output_path='$',
      result_path='$.index',
      lambda_function=functions.index_faces.function,
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)
   
    '''
    Use output of compare as Match/No-Match. 
    '''
    user_exists = sf.Choice(self,'CompareFaces-IsMatches')
    user_exists.when(
      condition= sf.Condition.boolean_equals('$.compare.Payload.IsMatch', True),
      next=index)

    compare.next(user_exists)

    '''
    If not in Dynamo, Search collection to authenticate the users
    '''
    search = sft.LambdaInvoke(self,'Search-ExistingFaces',
      input_path='$.inputRequest',   
      result_path='$.search',
      output_path='$',
      lambda_function=functions.search_faces_by_image.function,
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    user_exists.otherwise(search)

    '''
    Confirm the caller's has the correct picture
    '''
    is_calleruser = sf.Choice(self,'Check-SearchResults')
    is_calleruser.when(
      condition= sf.Condition.boolean_equals('$.compare.Payload.TopMatch.IsCallerUser',False),
      next= sf.Fail(self,'InvalidCredentials',
        error='UserAccessDenied',
        cause='The wrong person is in the photo.'))
    
    is_calleruser.otherwise(index)
    search.next(is_calleruser)

    # Format the message into API Gateway Model
    index.next(sf.Pass(self,'Update-Complete',
      parameters={
        'UserId.$': '$.inputRequest.UserId',
        'ImageId.$': '$.index.Payload.FaceRecord.Face.ImageId',
        'Status': 'Updated'
      }))

    '''
    And we're finished.
    '''
    self.set_state_machine(
      definition=detect,
      state_machine_name='Riv{}-UserPortal-Update'.format(
        self.landing_zone.zone_name))
