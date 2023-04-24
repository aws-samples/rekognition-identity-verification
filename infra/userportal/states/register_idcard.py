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

class RegisterIdCardStateMachine(RivStateMachineConstruct):

  def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack, functions: RivUserPortalFunctionSet, state_machine_type:sf.StateMachineType) -> None:
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
    Confirm the ID Card and Live Image match
    '''
    compare = sft.LambdaInvoke(self,'Compare-Documents',
      #input_path='$.inputRequest',   
      result_path='$.compare',
      output_path='$',
      payload= sf.TaskInput.from_object({
        'ReferenceImage.%': '$.inputRequest.IdCard',
        'ComparisonImage.%': '$.inputRequest.',
        'FailOnMismatch': True
      }),
      lambda_function=functions.search_faces_by_image.function,
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    # detect.next(compare)

    '''
    Check if the user already exists...
    '''
    search = sft.LambdaInvoke(self,'Search-ExistingFaces',
      lambda_function=functions.search_faces_by_image.function,
      input_path='$.inputRequest',
      result_path='$.search',
      output_path='$',
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    #compare.next(search)
    detect.next(search)

    '''
    Compare Faces with ID CARD
    '''
    check_face_with_id_card = sft.LambdaInvoke(self,'CompareFacesWithIDCard',
      lambda_function=functions.compare_face_with_idcard.function,
      input_path='$.inputRequest',
      result_path='$.search',
      output_path='$',
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)   

    
    '''
    Extract properties from id card
    '''
    # extract_id_card = sft.LambdaInvoke(self,'Extract-IDCard',
    #   lambda_function=functions.extract_id_card.function,
    #   input_path='$.inputRequest',
    #   result_path='$.idcard',
    #   output_path='$',
    #   invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)    

    # '''
    # Index the user and complete the operation...
    # '''
    # combine_arguments = sf.Pass(self,'Merge-Properties',
    #   result_path='$.inputRequest',
    #   output_path='$',
    #   parameters={
    #     'UserId.$': '$.inputRequest.UserId',
    #     'Image.$': '$.inputRequest.Image',
    #     'Properties.$': '$.idcard.Payload.Properties'
    #   })

    index = sft.LambdaInvoke(self,'Index-FaceInfo',
      lambda_function=functions.index_faces.function,
      input_path='$.inputRequest',
      output_path='$',
      result_path='$.index',
      invocation_type= sft.LambdaInvocationType.REQUEST_RESPONSE)

    # extract_id_card.next(combine_arguments).next(index)

    '''
    Stitch everything together...
    '''
    user_exists = sf.Choice(self,'Check-SearchResults')
    user_exists.when(
      next=check_face_with_id_card,
      condition=sf.Condition.or_(
        sf.Condition.string_equals(
          '$.search.Payload.TopMatch.Face.ExternalImageId',
          'Special:RIV_NO_FACE_MATCH'),
        sf.Condition.boolean_equals(
        '$.search.Payload.TopMatch.Face.IsCallerUser',
        True)))

    user_exists.otherwise(
      sf.Fail(self,'UserAlreadyExistsError',
        error='UserAlreadyExists',
        cause='Cannot register double faces in same collections.'))

    search.next(user_exists)

    '''
    Stitch everything together...
    '''
    compare_face = sf.Choice(self,'Check-FaceCompareWithIDCard')
    compare_face.when(
      next=index,
      condition=sf.Condition.or_(
        sf.Condition.boolean_equals(
        '$.search.Payload.IsMatch',
        True)))

    compare_face.otherwise(
      sf.Fail(self,'FaceNotMatchWithIDCardError',
        error='FaceNotMatchWithIDCard',
        cause='User face not match with the provided ID Card.'))

    check_face_with_id_card.next(compare_face)

    # Format the message into API Gateway Model
    index.next(sf.Pass(self,'Registration-Complete',
      parameters={
        'UserId.$': '$.inputRequest.UserId',
        'ImageId.$': '$.index.Payload.FaceRecord.Face.ImageId',
        'Status': 'Registered'
      }))

    self.set_state_machine(
      state_machine_name='{}-UserPortal-Register_IdCard'.format(self.riv_stack.riv_stack_name),
      definition=detect)
