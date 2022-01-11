from infra.storage.topology import RivSharedDataStores
from infra.userportal.functions.definitions import RivUserPortalCompareFaces, RivUserPortalDetectFaces, RivUserPortalExtractIdCard, RivUserPortalIndexFaces, RivUserPortalSearchFacesByImage
from infra.interfaces import IVpcRivStack
import aws_cdk as core
from constructs import Construct

class RivUserPortalFunctionSet(Construct):
  def __init__(self, scope: Construct, id:str, riv_stack:IVpcRivStack,sharedStorage:RivSharedDataStores,subnet_group_name:str='Default', **kwargs) -> None:
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
      riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=default_environment_var)

    self.detect_faces = RivUserPortalDetectFaces(self,'DetectFaces',
      riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=default_environment_var)

    self.search_faces_by_image = RivUserPortalSearchFacesByImage(self,'SearchFaces',
      riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=default_environment_var)

    self.extract_id_card = RivUserPortalExtractIdCard(self,'ExtractIdCard',
      riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=default_environment_var)
    
    '''
    Configure the Index Faces
    '''
    env = dict(default_environment_var)
    env['ENABLE_IMAGE_BUCKET'] = str(False),
    env['IMAGE_BUCKET_PREFIX'] = 'indexed'
    self.index_faces = RivUserPortalIndexFaces(self,'IndexFaces',
      riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=default_environment_var)    

    '''
    Grant additional permissions...
    '''
    sharedStorage.face_metadata.face_table.grant_read_data(self.compare_faces.function.role)
    sharedStorage.face_metadata.face_table.grant_read_write_data(self.index_faces.function.role)
    sharedStorage.face_metadata.face_table.grant_read_write_data(self.index_faces.function.role)
    sharedStorage.images.image_bucket.grant_put(self.index_faces.function.role)

