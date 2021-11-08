from sys import prefix
from storage import StorageWriter
import boto3
from models import FaceMetadata
from base64 import b64decode
from os import environ, path
from typing import Any, Mapping
from json import loads
from logging import Logger

'''
Initialize the function runtime
'''
logger = Logger(name='LambdaFunction')
riv_stack_name = environ.get('RIV_STACK_NAME')
region_name = environ.get('REGION')
face_table_name = environ.get('FACE_TABLE_NAME')
assert riv_stack_name is not None, "riv_stack_name is not available"
assert region_name is not None, "region_name is not available"
assert face_table_name is not None, "face_table_name is not available"

'''
Prepare XRAY, if available.
'''
try:
  from aws_xray_sdk.core import xray_recorder, patch_all
  patch_all() # Instrument all AWS methods.
except:
  print('AWS XRAY support not available.')

'''
Initialize any clients (... after xray!)
'''
rek_client = boto3.client('rekognition', region_name=region_name)
ssm_client = boto3.client('ssm', region_name=region_name)
ddb_client = boto3.client('dynamodb', region_name=region_name)

'''
Initialize the StorageWriter object
'''
storage_writer = StorageWriter(ddb_client, face_table_name)
if str(environ.get('ENABLE_IMAGE_BUCKET')).upper() == "TRUE":
  storage_writer.enable_image_bucket(
    s3_client  = boto3.client('s3', region_name=region_name),
    bucket_name= environ.get('IMAGE_BUCKET_NAME'),
    prefix = environ.get('IMAGE_BUCKET_PREFIX'))

'''
Determine the collection partition metadata 
'''
def get_partition_count()->int:
  
  #xray_recorder.begin_segment('get_partition_count')
  try:
    parameter_name = '/riv/{}/rekognition/partition-count'.format(riv_stack_name)
    response = ssm_client.get_parameter(Name=parameter_name)
    value = response['Parameter']['Value']
    return int(value)
  except Exception as error:
    logger.error('Unable to get_partition_count() - run src/rekognition/setup.')
    raise error
  finally:
    # xray_recorder.end_segment()
    pass

partition_count = get_partition_count()

def get_collection_id(user_id:str)->str:
  '''
  Fetch the collection id for input event.
  '''
  collection_id = hash(user_id) % partition_count
  return '{}-{}'.format(riv_stack_name, collection_id)

def function_main(event:Mapping[str,Any],_=None):
  '''
  Main function handler.
  '''
  face_metadata = FaceMetadata(event)  

  '''
  Index the face into the Amazon Rekognition Collection.
  '''
  try:
    response = rek_client.index_faces(
      CollectionId = get_collection_id(face_metadata.user_id),
      ExternalImageId= face_metadata.user_id,
      MaxFaces=1,
      Image={
        'Bytes':face_metadata.image_bytes
      })    
  except Exception as error:
    print('Unable to update collection')
    raise error

  '''
  Write the metadata and image content
  '''
  if not len(response['FaceRecords']) == 1:
    raise NotImplementedError('This sample only supports one indexed face.')

  face_record = response['FaceRecords'][0]
  face_id = face_record['Face']['FaceId']
  storage_writer.persist(face_metadata, face_id)
    
  '''
  Return a response
  '''
  return {
    'FaceModelVersion': response['FaceModelVersion'],
    'FaceRecord': face_record
  }

def read_example_file(filename:str)->Mapping[str,Any]:
  example_dir = path.join(path.dirname(__file__),'examples')
  file = path.join(example_dir, filename)

  with open(file, 'r') as f:
    return loads(f.read())

if __name__ == '__main__':
  xray_recorder.begin_segment('LocalDebug')
  payload = read_example_file('payload.json')
  function_main(payload)
  xray_recorder.end_segment()
