import builtins
from infra.storage.face_images import RivStorageImageStore
from infra.storage.face_metadata import RivStorageFaceMetadata
from infra.interfaces import IVpcRivStack
from constructs import Construct

class RivSharedDataStores(Construct):
  '''
  Represents the root construct for deploying shared data stores.
  '''
  def __init__(self, scope: Construct, id: builtins.str, riv_stack:IVpcRivStack) -> None:
    super().__init__(scope, id)

    '''
    Declare the data stores...
    '''
    self.face_metadata = RivStorageFaceMetadata(self,'Metadata', riv_stack=riv_stack)
    self.images = RivStorageImageStore(self,'Images', riv_stack=riv_stack)
    
    '''
    Include any VPC-endpoints required for Isolated Networking
    '''
    riv_stack.networking.endpoints.add_gateways()
