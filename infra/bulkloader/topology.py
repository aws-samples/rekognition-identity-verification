import builtins

from infra.bulkloader.batch_handler import RivBulkLoaderBatchHandler
from infra.bulkloader.throttled_indexer import RivBulkLoaderThrottledIndexer
from infra.storage.topology import RivSharedDataStores
from infra.bulkloader.inventory_created import RivBulkLoaderInventoryCreatedHandler
from infra.interfaces import IVpcLandingZone
from aws_cdk import (
  core,
  aws_iam as iam,
  #aws_dynamodb as ddb,
  #aws_ssm as ssm,
)

class RivBulkLoader(core.Construct):
  '''
  Represents the root construct for the Bulk Loader Service.
  '''
  def __init__(self, scope: core.Construct, id: builtins.str, landing_zone:IVpcLandingZone, sharedStorage:RivSharedDataStores, subnet_group_name:str='Default', **kwargs) -> None:
    super().__init__(scope, id)

    '''
    Configure the Amazon S3 Batch Service role.
    '''
    self.batch_service_role = iam.Role(self,'BatchServiceRole',
      assumed_by= iam.ServicePrincipal(service='batchoperations.s3.amazonaws.com'))
    
    sharedStorage.images.image_bucket.grant_read(self.batch_service_role)
    sharedStorage.images.inventory_bucket.grant_read_write(self.batch_service_role)

    # '''
    # Configure this Import History table.
    # '''
    # self.import_history_table = ddb.Table(self,'ImportTable',
    #   billing_mode= ddb.BillingMode.PAY_PER_REQUEST,
    #   removal_policy= core.RemovalPolicy.DESTROY,
    #   partition_key= ddb.Attribute(
    #     name='PartitionKey',
    #     type=ddb.AttributeType.STRING),
    #   sort_key=ddb.Attribute(
    #     name='SortKey',
    #     type=ddb.AttributeType.STRING),
    #   point_in_time_recovery=True)

    '''
    The batch job will determine which images qualify for processing.
    Only applicable items are put into an SQS queue that throttles data loading speeds.
    '''
    self.throttled_indexer = RivBulkLoaderThrottledIndexer(self,'BatchIndexer',
      landing_zone=landing_zone,
      sharedStorage=sharedStorage,
      subnet_group_name=subnet_group_name,
      env={
        # 'IMPORT_TABLE_NAME': self.import_history_table.table_name,
        'ZONE_NAME': landing_zone.zone_name,
        'USER_PORTAL_PARAM': '/riv/{}/userportal/url'.format(
          landing_zone.zone_name),
      })

    '''
    S3 Batch iterates through the inventory list and passes the items to a lambda.
    This lambda will determine if the S3 object (aka the image); qualifies for RIV indexing.
    Reasons for skipping images include: already processed, incomplete information, etc. 
    '''
    self.batch_handler = RivBulkLoaderBatchHandler(self,'BatchHandler',
      landing_zone=landing_zone,
      sharedStorage=sharedStorage,
      subnet_group_name=subnet_group_name,
      env={
        'THROTTLED_QUEUE_URL': self.throttled_indexer.input_queue.queue_url,
        # 'IMPORT_TABLE_NAME': self.import_history_table.table_name,
      })

    self.batch_handler.function.grant_invoke(self.batch_service_role)

    '''
    When the S3 inventory completes it raises an ObjectCreatedNotification in the inventory bucket.
    This message forwards to an SNS Topic then into this function.  After light-filtering and creates the S3 Batch job. 
    '''
    self.inventory_created_handler = RivBulkLoaderInventoryCreatedHandler(self,'InventoryCreatedHandler',
      landing_zone=landing_zone,
      sharedStorage=sharedStorage,
      subnet_group_name=subnet_group_name,
      env={
        'ACCOUNT_ID': core.Stack.of(self).account,
        'BATCH_FUNCTION_ARN': self.batch_handler.function.function_arn,
        'BATCH_ROLE_ARN': self.batch_service_role.role_arn,
        'ZONE_NAME': landing_zone.zone_name,
      })
