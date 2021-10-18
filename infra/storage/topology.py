import builtins
from infra.storage.face_images import RivStorageImageStore
from infra.storage.face_metadata import RivStorageFaceMetadata
from infra.interfaces import IVpcLandingZone
from aws_cdk import (
  core,
)

class RivSharedDataStores(core.Construct):
  '''
  Represents the root construct for deploying shared data stores.
  '''
  def __init__(self, scope: core.Construct, id: builtins.str, landing_zone:IVpcLandingZone) -> None:
    super().__init__(scope, id)

    '''
    Declare the data stores...
    '''
    self.face_metadata = RivStorageFaceMetadata(self,'Metadata', landing_zone=landing_zone)
    self.images = RivStorageImageStore(self,'Images', landing_zone=landing_zone)
    
    '''
    Include any VPC-endpoints required for Isolated Networking
    '''
    landing_zone.networking.endpoints.add_gateways()
