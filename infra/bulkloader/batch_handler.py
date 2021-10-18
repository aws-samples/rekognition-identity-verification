from typing import Mapping
from infra.default_lambda import RivDefaultFunction
from infra.storage.topology import RivSharedDataStores
from infra.interfaces import IVpcLandingZone
from aws_cdk import (
  core,
)

class RivBulkLoaderBatchHandler(RivDefaultFunction):
  '''
  Represents a function handler for the Amazon S3 Batch.
  ''' 
  @property
  def source_directory(self)->str:
    return 'src/bulk-loader/batch-handler'

  @property
  def component_name(self)->str:
    return 'BatchHandler'

  @property
  def function_timeout(self)->core.Duration:
    return core.Duration.minutes(5)

  @property
  def function_name(self) -> str:
    return 'Riv{}-BulkLoading-{}'.format(
      self.landing_zone.zone_name,
      self.component_name)
  
  def __init__(self, scope: core.Construct, id: str, landing_zone:IVpcLandingZone, sharedStorage:RivSharedDataStores, subnet_group_name:str='Default', env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, **kwargs, landing_zone=landing_zone, subnet_group_name=subnet_group_name, env=env)

    '''
    Grant additional permissions
    '''    
    sharedStorage.images.image_bucket.grant_read(self.function.role)
    # self.function.role.add_to_policy(statement=iam.PolicyStatement(
    #   effect= iam.Effect.ALLOW,
    #   actions=['s3:GetObjectTagging'],
    #   resources=[
    #     sharedStorage.images.image_bucket.bucket_arn,
    #     sharedStorage.images.image_bucket.bucket_arn+'/*'
    #   ]))
