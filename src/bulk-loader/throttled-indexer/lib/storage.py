from typing import List, Mapping
import boto3
from lib.models import Payload
from base64 import b64encode
#from aws_xray_sdk.core import xray_recorder

class StorageClient:
  '''
  Represents a utility for interacting with various storage services.
  '''
  def __init__(self, region_name:str) -> None:
    assert region_name is not None, "No region_name available"

    self.s3 = boto3.client('s3', region_name=region_name)
    
  #@xray_recorder.capture('attach_image')
  def attach_image(self, payload:Payload)->Payload:
    '''
    Downloads the image referenced by the payload.
    Persists the content into the payload.input_request structure.
    :param payload:  The body from most the SQSMessageRecord
    '''
    assert payload is not None, "No payload is available"

    response = self.s3.get_object(
      Bucket = payload.bucket_name,
      Key= payload.object_key
    )

    image = response['Body'].read()
    payload.input_request['Image'] = str(b64encode(image), 'utf-8')
    return payload

  #@xray_recorder.capture('write_index_complete')
  def write_index_complete(self, payload:Payload)->None:
    '''
    Updates the Import History Table to record this file is complete.
    :param payload:  The body from most the SQSMessageRecord
    '''
    assert payload is not None, "No payload is available"

    '''
    Get the previous tags...
    '''
    response = self.s3.get_object_tagging(
      Bucket=payload.bucket_name,
      Key=payload.object_key)

    tagSet:Mapping[str,dict] = {}
    for tag in response['TagSet']:
      tagSet[tag['Key']] = tag

    '''
    Upsert the Indexed marker...
    '''
    tagSet['Indexed'] = {'Key':'Indexed', 'Value':'True'}

    self.s3.put_object_tagging(
      Bucket=payload.bucket_name,
      Key=payload.object_key,
      Tagging={ 'TagSet': list(tagSet.values()) })
