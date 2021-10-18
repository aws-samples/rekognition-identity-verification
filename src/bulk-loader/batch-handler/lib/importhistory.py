import boto3
from lib.models import BatchTask
#from aws_xray_sdk.core import xray_recorder

class ImportHistoryManager:
  '''
  Represents a client for the Import History metadata.
  '''

  def __init__(self, region_name:str) -> None:
    assert region_name is not None, "No region_name available"

    self.s3 = boto3.client('s3', region_name=region_name)

  #@xray_recorder.capture('qualifies_for_processing')
  def qualifies_for_processing(self, user_id:str, task:BatchTask)->bool:
    '''
    Checks if the task requires RIV processing.
    :param user_id: The desired user identity.
    :param task:  The current Amazon S3 Batch Task.
    '''
    assert user_id is not None, "No user_id is available"
    assert task is not None, "No task is available"

    '''
    Get the Object TagSet with case for this object
    '''
    response = self.s3.get_object_tagging(
      Bucket=task.bucket_name,
      Key=task.s3Key)

    '''
    Enumerate through tags and attempt to disqualify processing
    '''
    for tag in response['TagSet']:
      key = str(tag['Key']).lower()
      value = str(tag['Value']).lower()

      if 'indexed' == key and value == 'true':
        return False

      if 'ignore' == key and value == 'true':
        return False

    return True
