import builtins
from infra.interfaces import IRivStack
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
  aws_s3 as s3,
  aws_sqs as sqs,
  aws_sns as sns,
  aws_s3_notifications as s3n,
  aws_sns_subscriptions as subs,
)

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

  def __init__(self, scope: Construct, id: builtins.str, riv_stack:IRivStack) -> None:
    super().__init__(scope, id)

    self.image_bucket = s3.Bucket(self,'ImageBucket',
      removal_policy= core.RemovalPolicy.RETAIN)


  