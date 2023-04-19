import builtins
from infra.userportal.functions.topology import RivUserPortalFunctionSet
from infra.userportal.states.interfaces import RivStateMachineConstruct
from infra.interfaces import IRivStack
from constructs import Construct
from aws_cdk import (
  aws_stepfunctions as sf,
  aws_stepfunctions_tasks as sft,
)

class RegisterStateMachine(RivStateMachineConstruct):

  def __init__(self, scope: Construct, id: builtins.str, riv_stack: IRivStack, functions: RivUserPortalFunctionSet, state_machine_type:sf.StateMachineType) -> None:
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
    Check if the user already exists...
    '''
    search = sft.LambdaInvoke(self,'Search-ExistingFaces',
      lambda_function=functions.search_faces_by_image.function,
      input_path='$.inputRequest',
      result_path='$.search',
      output_path='$',
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    detect.next(search)

    '''
    Index the user and complete the operation...
    '''
    index = sft.LambdaInvoke(self,'Index-FaceInfo',
      lambda_function=functions.index_faces.function,
      input_path='$.inputRequest',
      output_path='$',
      result_path='$.index',
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    '''
    Stitch everything together...
    '''
    user_exists = sf.Choice(self,'Check-SearchResults')
    user_exists.when(
      condition= sf.Condition.string_equals('$.search.Payload.TopMatch.Face.ExternalImageId',"Special:RIV_NO_FACE_MATCH"),
      next=index)
    user_exists.when(
      condition= sf.Condition.boolean_equals('$.search.Payload.TopMatch.Face.IsCallerUser',True),
      next=index)
    user_exists.otherwise(
      sf.Fail(self,'UserAlreadyExistsError',
        error='UserAlreadyExists',
        cause='Cannot register double faces in same collections.'))

    search.next(user_exists)

    # Format the message into API Gateway Model
    index.next(sf.Pass(self,'Registration-Complete',
      parameters={
        'UserId.$': '$.inputRequest.UserId',
        'ImageId.$': '$.index.Payload.FaceRecord.Face.ImageId',
        'Status': 'Registered'
      }))

    self.set_state_machine(
      state_machine_name='{}-UserPortal-Register_User'.format(self.riv_stack.riv_stack_name),
      definition=detect)
