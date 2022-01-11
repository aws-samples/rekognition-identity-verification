import builtins
from constructs import Construct
from aws_cdk import (
  custom_resources as cr,
)

class RekognitionCollectionConstruct(Construct):
  def __init__(self, scope: Construct, id: builtins.str, collection_id:str) -> None:
    super().__init__(scope, id)
    assert not collection_id is None, "CollectionId is missing"

    '''
    AwsSdkCall expects JavaScript naming conventions. 
    https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/Rekognition.html#createCollection-property
    '''
    _ = cr.AwsCustomResource(self,'RekognitionCollection',
      policy= cr.AwsCustomResourcePolicy.from_sdk_calls(
        resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
      on_create= cr.AwsSdkCall(
        service='Rekognition',
        action='createCollection',
        physical_resource_id= cr.PhysicalResourceId.of('RekogitionCollection:'+collection_id),
        parameters={
          'CollectionId': collection_id,
        }),
      on_delete= cr.AwsSdkCall(
        service='Rekognition',
        action='deleteCollection',
        physical_resource_id= cr.PhysicalResourceId.of('RekogitionCollection:'+collection_id),
        parameters={
          'CollectionId': collection_id,
        })
      )