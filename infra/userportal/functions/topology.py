from infra.storage.topology import RivSharedDataStores
from infra.userportal.functions.definitions import RivUserPortalCompareFaces, RivUserPortalDetectFaces, RivUserPortalExtractIdCard, RivUserPortalIndexFaces, RivUserPortalSearchFacesByImage,RivUserPortalCompareFacesWithIDCard,RivUserPortalResetUser,RivUserPortalLivenessSesstionResult,RivUserPortalStartLivenessSesstion,RivUserPortalCheckUserID
from infra.interfaces import IRivStack
import aws_cdk as core
from constructs import Construct

class RivUserPortalFunctionSet(Construct):
  def __init__(self, scope: Construct, id:str, riv_stack:IRivStack,sharedStorage:RivSharedDataStores, **kwargs) -> None:
    super().__init__(scope, id)

    '''
    Define the functions...
    '''
    default_environment_var = {
      'REGION': core.Stack.of(self).region,
      'RIV_STACK_NAME': riv_stack.riv_stack_name,
      'FACE_TABLE_NAME': sharedStorage.face_metadata.face_table.table_name,
      'IMAGE_BUCKET_NAME': sharedStorage.images.image_bucket.bucket_name,
    }

    self.compare_faces = RivUserPortalCompareFaces(self,'CompareFaces',
      riv_stack=riv_stack, env=default_environment_var)

    self.detect_faces = RivUserPortalDetectFaces(self,'DetectFaces',
      riv_stack=riv_stack, env=default_environment_var)

    self.search_faces_by_image = RivUserPortalSearchFacesByImage(self,'SearchFaces',
      riv_stack=riv_stack, env=default_environment_var)

    self.extract_id_card = RivUserPortalExtractIdCard(self,'ExtractIdCard',
      riv_stack=riv_stack, env=default_environment_var)
    
    self.compare_face_with_idcard = RivUserPortalCompareFacesWithIDCard(self,'CompareFacesWithIDCard',
      riv_stack=riv_stack, env=default_environment_var)
    
    self.start_liveness_session = RivUserPortalStartLivenessSesstion(self,'StartLivenessSesstion',
      riv_stack=riv_stack,  env=default_environment_var)
    
    self.reset_user = RivUserPortalResetUser(self,'ResetUser',
      riv_stack=riv_stack,  env=default_environment_var)

    self.liveness_session_result = RivUserPortalLivenessSesstionResult(self,'LivenessSesstionResult',
      riv_stack=riv_stack,  env=default_environment_var)
    
    self.check_userid = RivUserPortalCheckUserID(self,'CheckUserID',
      riv_stack=riv_stack,  env=default_environment_var)
    
    '''
    Configure the Index Faces
    '''
    env = dict(default_environment_var)
    env['ENABLE_IMAGE_BUCKET'] = str(False),
    env['IMAGE_BUCKET_PREFIX'] = 'indexed'
    self.index_faces = RivUserPortalIndexFaces(self,'IndexFaces',
      riv_stack=riv_stack,  env=default_environment_var)    

    '''
    Grant additional permissions...
    '''
    sharedStorage.face_metadata.face_table.grant_read_data(self.compare_faces.function.role)
    sharedStorage.face_metadata.face_table.grant_read_write_data(self.index_faces.function.role)
    sharedStorage.face_metadata.face_table.grant_read_write_data(self.index_faces.function.role)
    sharedStorage.face_metadata.face_table.grant_read_write_data(self.reset_user.function.role)
    sharedStorage.face_metadata.face_table.grant_read_write_data(self.check_userid.function.role)
    sharedStorage.images.image_bucket.grant_put(self.index_faces.function.role)
    sharedStorage.images.image_bucket.grant_put(self.start_liveness_session.function.role)
    sharedStorage.images.image_bucket.grant_put(self.liveness_session_result.function.role)
    sharedStorage.images.image_bucket.grant_read(self.start_liveness_session.function.role)
    sharedStorage.images.image_bucket.grant_read(self.liveness_session_result.function.role)
    sharedStorage.images.image_bucket.grant_read(self.detect_faces.function.role)
    sharedStorage.images.image_bucket.grant_read(self.compare_face_with_idcard.function.role)
    sharedStorage.images.image_bucket.grant_read(self.compare_faces.function.role)
    sharedStorage.images.image_bucket.grant_read(self.search_faces_by_image.function.role)
    sharedStorage.images.image_bucket.grant_read(self.index_faces.function.role)
    sharedStorage.images.image_bucket.grant_read_write(self.extract_id_card.function.role)
   

  

