import builtins
from infra.interfaces import IVpcRivStack
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
  aws_s3 as s3,
  aws_sqs as sqs,
  aws_sns as sns,
  aws_s3_notifications as s3n,
  aws_sns_subscriptions as subs,
)
from infra.configsettings import ConfigManager

config_mgr = ConfigManager()

class RivStorageImageStore(Construct):
  '''
  Represents the ImageStore construct.
  '''
  @property
  def image_bucket(self)->s3.IBucket:
    '''
    Gets the bucket holding the images.
    '''
    return self.__image_bucket

  @image_bucket.setter
  def image_bucket(self,value:s3.IBucket)->None:
    self.__image_bucket = value

  if config_mgr.use_inventory_bucket:
    @property
    def inventory_bucket(self)->s3.IBucket:
      '''
      Gets the inventory bucket associated with the image bucket
      '''
      return self.__inventory_bucket

    @inventory_bucket.setter
    def inventory_bucket(self,value:s3.IBucket)->None:
      self.__inventory_bucket = value

    @property
    def inventory_created(self)->sns.ITopic:
      '''
      Gets the notification topic that an Amazon S3 Inventory finished.
      '''
      return self.__inventory_created

    @inventory_created.setter
    def inventory_created(self,value:sns.ITopic)->None:
      self.__inventory_created = value

  def __init__(self, scope: Construct, id: builtins.str, riv_stack:IVpcRivStack) -> None:
    super().__init__(scope, id)

    self.image_bucket = s3.Bucket(self,'ImageBucket',
      removal_policy= core.RemovalPolicy.RETAIN)
    
    if config_mgr.use_inventory_bucket:

      # Create the inventory bucket...
      self.inventory_bucket = s3.Bucket(self,'InventoryBucket',
        removal_policy= core.RemovalPolicy.DESTROY)

      self.image_bucket.add_inventory(
        #objects_prefix='images/',
        inventory_id='{}-InventoryReport'.format('Full'),
        format =s3.InventoryFormat.CSV,
        frequency= s3.InventoryFrequency.DAILY,
        include_object_versions= s3.InventoryObjectVersion.CURRENT,
        destination= s3.InventoryDestination(
          bucket=self.inventory_bucket,
          bucket_owner= core.Aws.ACCOUNT_ID,
          prefix=None))

      # Broadcast inventory creation events...
      self.inventory_created = sns.Topic(self,'InventoryCreated',
        display_name='{}-ImageStore-InventoryCreated'.format(riv_stack.riv_stack_name),
        topic_name='{}-ImageStore-InventoryCreated'.format(riv_stack.riv_stack_name))

      self.inventory_bucket.add_event_notification(
        s3.EventType.OBJECT_CREATED,
        s3n.SnsDestination(topic=self.inventory_created),
        s3.NotificationKeyFilter(suffix='manifest.json'))

      # Persist the notification in an SQS topic to simplify debugging.
      self.inventory_created_debug_queue:sqs.IQueue = sqs.Queue(self,'InventoryCreatedDebugQueue',
        retention_period=core.Duration.days(14))

      self.inventory_created.add_subscription(subs.SqsSubscription(
        queue=self.inventory_created_debug_queue,
        raw_message_delivery=True))
