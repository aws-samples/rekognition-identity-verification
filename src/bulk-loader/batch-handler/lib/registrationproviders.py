import boto3
from json import loads
from json.decoder import JSONDecodeError
from logging import Logger
from urllib.parse import  urlparse
from lib.models import BatchTask, IRegistrationDataProvider, UserRegistrationInfo
#from aws_xray_sdk.core import xray_recorder

class PropertyFileLoadError(Exception):
  '''
  Represents an error while fetching the user's properties file.
  '''

logger = Logger('S3TagUserRegistrationInfo')
class S3TagUserRegistrationInfo(IRegistrationDataProvider):
  '''
  Represents a Registration Data Provider that extracts data from Amazon S3 Tagging data.
  '''
  def __init__(self, region_name:str) -> None:
    super().__init__()
    assert region_name is not None, "No region_name available"
    self.s3 = boto3.client('s3', region_name=region_name)
  
  #@xray_recorder.capture('S3TagUserRegistrationInfo::get_registration_data')
  def get_registration_data(self, task:BatchTask)->UserRegistrationInfo:
    assert task is not None, "No task available."

    response = self.s3.get_object_tagging(
      Bucket = task.bucket_name,
      Key= task.s3Key
    )

    '''
    Convert the Object Tags into Registration metadata.
    '''
    registration = UserRegistrationInfo()
    for tag in response['TagSet']:
      key:str = tag['Key']
      compare_key = key.lower()
      value:str = tag['Value']

      if compare_key == "userid":
        registration.user_id = value
      elif compare_key in ['indexed', 'ignore']:
        continue
      elif compare_key == 'properties':
        registration.properties = self.get_property_bag(value)

    return registration

  def get_property_bag(self, object_path:str)->dict:
    '''
    Gets the user's property bag from an existing Amazon S3 Object.
    '''
    if not object_path.startswith('s3://'):
      raise PropertyFileLoadError('Invalid Path %s ' % object_path)

    if not object_path.endswith('.json'):
      raise PropertyFileLoadError('Invalid Path %s ' % object_path)

    parsed = urlparse(object_path)
    bucket = parsed.hostname
    key = parsed.path.lstrip('/')
    try:
      response = self.s3.get_object(Bucket=bucket,Key=key)
      content = response['Body'].read()
      return loads(content)
    except self.s3.exceptions.NoSuchKey as error:
      logger.error('Unable to fetch %s due to %s' % object_path, str(error))
      raise PropertyFileLoadError('Unable to fetch %s ' % object_path)
    except JSONDecodeError as error:
      logger.error('Unable to deserialize %s' % object_path)
      raise PropertyFileLoadError('Unable to deserialize %s' % object_path)
    except Exception as error:
      raise NotImplementedError('Unknown Error %s' % error.__class__.__name__)
