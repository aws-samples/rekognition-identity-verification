from infra.storage.topology import RivSharedDataStores
from infra.userportal.functions.definitions import RivUserPortalCompareFaces, RivUserPortalDetectFaces, RivUserPortalExtractIdCard, RivUserPortalIndexFaces, RivUserPortalSearchFacesByImage
from infra.interfaces import IVpcLandingZone
from aws_cdk import (
  core,  
)

class RivUserPortalFunctionSet(core.Construct):
  def __init__(self, scope: core.Construct, id:str, landing_zone:IVpcLandingZone,sharedStorage:RivSharedDataStores,subnet_group_name:str='Default', **kwargs) -> None:
    super().__init__(scope, id)

    '''
    Define the functions...
    '''
    default_environment_var = {
      'REGION': core.Stack.of(self).region,
      'ZONE_NAME': landing_zone.zone_name,
      'FACE_TABLE_NAME': sharedStorage.face_metadata.face_table.table_name,
      'IMAGE_BUCKET_NAME': sharedStorage.images.image_bucket.bucket_name,
    }

    self.compare_faces = RivUserPortalCompareFaces(self,'CompareFaces',
      landing_zone=landing_zone, subnet_group_name=subnet_group_name, env=default_environment_var)

    self.detect_faces = RivUserPortalDetectFaces(self,'DetectFaces',
      landing_zone=landing_zone, subnet_group_name=subnet_group_name, env=default_environment_var)

    self.search_faces_by_image = RivUserPortalSearchFacesByImage(self,'SearchFaces',
      landing_zone=landing_zone, subnet_group_name=subnet_group_name, env=default_environment_var)

    self.extract_id_card = RivUserPortalExtractIdCard(self,'ExtractIdCard',
      landing_zone=landing_zone, subnet_group_name=subnet_group_name, env=default_environment_var)
    
    '''
    Configure the Index Faces
    '''
    env = dict(default_environment_var)
    env['ENABLE_IMAGE_BUCKET'] = str(False),
    env['IMAGE_BUCKET_PREFIX'] = 'indexed'
    self.index_faces = RivUserPortalIndexFaces(self,'IndexFaces',
      landing_zone=landing_zone, subnet_group_name=subnet_group_name, env=default_environment_var)    

    '''
    Grant additional permissions...
    '''
    sharedStorage.face_metadata.face_table.grant_read_data(self.compare_faces.function.role)
    sharedStorage.face_metadata.face_table.grant_read_write_data(self.index_faces.function.role)
    sharedStorage.face_metadata.face_table.grant_read_write_data(self.index_faces.function.role)
    sharedStorage.images.image_bucket.grant_put(self.index_faces.function.role)

