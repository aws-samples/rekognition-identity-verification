from typing import Mapping
from infra.default_lambda import RivDefaultFunction
from infra.storage.topology import RivSharedDataStores
from infra.interfaces import IVpcLandingZone
from aws_cdk import (
  core,
  aws_lambda_event_sources as events,
  aws_sqs as sqs,
  aws_iam as iam,
)

class RivBulkLoaderThrottledIndexer(RivDefaultFunction):
  '''
  Represents a function that reads from SQS and writes into RiV.
  ''' 
  @property
  def source_directory(self)->str:
    return 'src/bulk-loader/throttled-indexer'

  @property
  def component_name(self)->str:
    return 'ThrottledIndexer'

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
    Configure the Input Queue with redrive policy into a DLQ 
    '''
    self.dead_letter_queue = sqs.Queue(self,'DeadLetterQueue')

    self.input_queue = sqs.Queue(self,'InputQueue',
      retention_period= core.Duration.days(7),
      visibility_timeout= self.function_timeout,
      dead_letter_queue=sqs.DeadLetterQueue(
        max_receive_count=3,
        queue=self.dead_letter_queue))

    '''
    Configure the lambda to trigger from the queue.
    '''
    self.function.add_event_source(events.SqsEventSource(
      queue= self.input_queue,
      batch_size = 1))

    '''
    Grant additional permissions on the image bucket...
    '''
    #sharedStorage.images.image_bucket.grant_read(self.function.role)
    self.function.role.add_to_policy(statement=iam.PolicyStatement(
      effect= iam.Effect.ALLOW,
      actions=[
        's3:GetObject*',
        's3:GetBucket*',
        's3:List*',
        's3:PutObjectTagging',
      ],
      resources=[
        sharedStorage.images.image_bucket.bucket_arn,
        sharedStorage.images.image_bucket.bucket_arn+'/*'
      ]))

    '''
    Grant read access to the SSM Parameters...
    '''
    self.function.role.add_to_policy(statement=iam.PolicyStatement(
      effect= iam.Effect.ALLOW,
      actions=['ssm:GetParameter*'],
      resources=['arn:aws:ssm:{}:{}:parameter/riv/{}/userportal/url'.format(
        core.Stack.of(self).region, core.Aws.ACCOUNT_ID, landing_zone.zone_name)]
    ))
