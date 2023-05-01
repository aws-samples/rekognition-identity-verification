from typing import Optional
from boto3 import client
from models import FaceMetadata
from logging import Logger
from errors import NonRecoverableError, TransientError
from base64 import b64encode

logger = Logger(name='StorageProvider')

class IStorageWriter:
  def persist(self, face_metadata:FaceMetadata, face_id:str)->None:
    assert face_metadata is not None, "faceMetadata not specified"
    assert face_id is not None, "face_id not specified"
    raise NotImplementedError()

class StorageWriter(IStorageWriter):
  '''
  Represents an IStorageWriter that persists all information in Amazon DynamoDB.
  '''
  def __init__(self, ddb_client:client, face_table_name:str) -> None:
    super().__init__()
    assert ddb_client is not None, "ddb_client not specified"
    assert face_table_name is not None, "face_table_name not specified"

    self.ddb_client = ddb_client
    self.face_table_name = face_table_name
    self.image_bucket_enabled = False 

  def enable_image_bucket(self, s3_client:client, bucket_name:str, prefix:Optional[str]=None)->None:
    '''
    Configure this writer to place image payloads into an Amazon S3 bucket.
    '''
    assert s3_client is not None, "s3_client not specified"
    assert bucket_name is not None, "bucket_name is not specified"
    assert not self.image_bucket_enabled, "multiple calls to enable_image_bucket detected"

    self.s3_client = s3_client
    self.bucket_name = bucket_name
    
    if prefix is None:
      self.prefix = ''
    elif prefix.endswith('/'):
      self.prefix = prefix
    else:
      self.prefix = prefix + '/'

    self.image_bucket_enabled = True

  def persist(self, face_metadata: FaceMetadata, face_id:str)->None:
    '''
    Writes 
    '''
    assert face_metadata is not None, "faceMetadata not specified"
    assert face_id is not None, "face_id not specified"
    
    try:
      item = self.convert_to_item(face_metadata, face_id)
      self.ddb_client.put_item(TableName= self.face_table_name, Item= item)
    except (
      self.ddb_client.exceptions.ConditionalCheckFailedException,
      self.ddb_client.exceptions.ResourceNotFoundException,
      self.ddb_client.exceptions.ItemCollectionSizeLimitExceededException) as error:
        logger.error(str(error))
        raise NonRecoverableError(error.__class__.__name__)
    except (
      self.ddb_client.exceptions.ProvisionedThroughputExceededException,
      self.ddb_client.exceptions.TransactionConflictException,
      self.ddb_client.exceptions.RequestLimitExceeded,
      self.ddb_client.exceptions.InternalServerError) as error:
        logger.error(str(error))
        raise TransientError(error.__class__.__name__)
    except Exception as error:
        logger.error(str(error))
        raise NotImplementedError(error.__class__.__name__)
      
  def convert_to_item(self, face_metadata:FaceMetadata, face_id:str) -> dict:
    '''
    Encodes this object as Amazon DyanmoDB Item.
    '''
    assert face_metadata is not None, "faceMetadata not specified"
    assert face_id is not None, "face_id not specified"

    item = {
      'PartitionKey': {'S': 'User::{}'.format(face_metadata.user_id.lower())},
      'SortKey': {'S': 'Face::{}'.format(face_id.lower()) },
      #'image': {'B': str(b64encode(face_metadata.image_bytes),encoding='utf-8') },
      'property_bag': {'M': FaceMetadata.ddb_encode_dict(face_metadata.property_bag) }
    }

    '''
    Default behavior is to store all data in DynamoDB.
      This strategy provides more consistent response times to end-users. 
    '''
    if not self.image_bucket_enabled and face_metadata.image_bytes is not None:
      item['image'] = {'B': str(b64encode(face_metadata.image_bytes),encoding='utf-8') }
      return item

    '''
    Alternatively customers can place the images into an S3 bucket
      This strategy is potentially more cost-efficient with longer latest byte retrieval times
    '''
    # key = '{}{}/{}.bin'.format(self.prefix, face_metadata.user_id, face_id)
    # self.s3_client.put_object(
    #   Bucket=self.bucket_name,
    #   Key=key,
    #   Body = face_metadata.image_bytes,
    #   Tagging="Indexed=True")

    '''
    Update the item to point at the key
    '''
    item['bucket'] = { 'S' :face_metadata.bucket }
    item['name'] =  { 'S' :face_metadata.name }
    return item
