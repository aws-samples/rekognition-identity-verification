import builtins
from infra.userportal.functions.topology import RivUserPortalFunctionSet
from infra.userportal.states.interfaces import RivStateMachineConstruct
from infra.interfaces import IVpcRivStack
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
  aws_stepfunctions as sf,
  aws_stepfunctions_tasks as sft,
)

class AuthStateMachine(RivStateMachineConstruct):
  def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack, functions: RivUserPortalFunctionSet,state_machine_type:sf.StateMachineType) -> None:
    super().__init__(scope, id, riv_stack, functions, state_machine_type=state_machine_type)

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
    Format response
    '''
    auth_completed = sf.Pass(self,'Auth-Complete',
      parameters={
        'UserId.$': '$.inputRequest.UserId',
        'Status': 'Verified'
      })
   
    '''
    Use output of compare as Match/No-Match. 
    '''
    user_exists = sf.Choice(self,'CompareFaces-IsMatches')
    user_exists.when(
      condition= sf.Condition.boolean_equals('$.compare.Payload.IsMatch', True),
      next=auth_completed)

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
      condition= sf.Condition.boolean_equals('$.compare.Payload.IsMatch',False),
      next= sf.Fail(self,'InvalidCredentials',
        error='UserAccessDenied',
        cause='The wrong person is in the photo.'))
    
    is_calleruser.otherwise(auth_completed)
    search.next(is_calleruser)

    '''
    Definition is complete, route it.
    '''
    self.set_state_machine(
        state_machine_name='{}-UserPortal-Auth'.format(self.riv_stack.riv_stack_name),
        definition=detect)
