from json import loads
from typing import List, Mapping

class Payload:
  def __init__(self, props:dict) -> None:
    self.bucket_arn:str = props['BucketArn']
    self.object_key:str = props['ObjectKey']
    self.input_request:dict = props['InputRequest']

  @property
  def bucket_name(self)->str:
    '''
    Gets the name of the bucket holding the image.
    '''
    if self.bucket_arn.startswith('arn'):
      return self.bucket_arn.split(':')[-1]
    else:
      return self.bucket_arn

class SQSMessageRecord:
  '''
  Represents an individual SQS message.
  '''
  def __init__(self, props:dict) -> None:
    self.body:str = props['body']
    self.messageId:str = props['messageId']
    self.attributes:Mapping[str,str] = props['attributes']
    self.message_attributes = props['messageAttributes']

    self.payload:Payload = Payload(loads(self.body))


class SQSMessage:
  '''
  Represents a batch of SQSMessageRecords 
  '''
  def __init__(self, event:dict) -> None:
    self.records:List[SQSMessageRecord] = [SQSMessageRecord(x) for x in event['Records']]
