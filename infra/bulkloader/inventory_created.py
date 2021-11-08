from typing import Mapping
from infra.default_lambda import RivDefaultFunction
from infra.storage.topology import RivSharedDataStores
from infra.interfaces import IVpcRivStack
from aws_cdk import (
  core,
  aws_lambda_event_sources as events,
)

class RivBulkLoaderInventoryCreatedHandler(RivDefaultFunction):
  '''
  Represents a lambda for processing Image Bucket Manifests.
  ''' 
  @property
  def source_directory(self)->str:
    return 'src/bulk-loader/inventory-created-handler'

  @property
  def component_name(self)->str:
    return 'LoaderInvCreatedHndlr'

  @property
  def function_timeout(self)->core.Duration:
    return core.Duration.minutes(5)

  @property
  def function_name(self) -> str:
    return 'Riv{}-BulkLoading-{}'.format(
        self.landing_zone.zone_name,
        self.component_name)
  
  def __init__(self, scope: core.Construct, id: str, landing_zone:IVpcRivStack, sharedStorage:RivSharedDataStores, subnet_group_name:str='Default', env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, **kwargs, landing_zone=landing_zone, subnet_group_name=subnet_group_name, env=env)

    '''
    When the Amazon S3 Inventory Report completes, it raises the ObjectCreatedNotification.
    This message forwards into the Inventory Created topic, and this function responds to those request. 
    '''
    self.function.add_event_source(events.SnsEventSource(
      topic= sharedStorage.images.inventory_created))

    '''
    Grant additional permissions here.
    '''
    sharedStorage.images.inventory_bucket.grant_read_write(self.function.role)
    # self.function.role.attach_inline_policy(policy= iam.Policy(self,'S3Batch',
    #   statements=[
    #     iam.PolicyStatement(
    #     effect= iam.Effect.ALLOW,
    #     resource
    #     actions=[
    #       's3:CreateJob',
    #       'iam:PassRole'
    #     ])
    #   ]))
