import boto3
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
assert riv_stack_name is not None, "riv_stack_name is not available"
assert region_name is not None, "region_name is not available"

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

NO_FACE_MATCH={
  'Similarity':0,
  'Face':{
    'FaceId': '00000000-0000-0000-0000-000000000000',
    'ExternalImageId': 'Special:RIV_NO_FACE_MATCH'
  }
}

'''
Determine the collection partition metadata 
'''
#@xray_recorder.capture('get_partition_count')
def get_partition_count()->int:
  try:
    parameter_name = '/riv/{}/rekognition/partition-count'.format(riv_stack_name)
    
    response = ssm_client.get_parameter(Name=parameter_name)
    value = response['Parameter']['Value']
    return int(value)
  except Exception as error:
    logger.error('Unable to get_partition_count() - run src/rekognition/setup.')
    raise error

partition_count = get_partition_count()

def get_collection_id(user_id:dict)->str:
  '''
  Fetch the collection id for input event.
  '''
  collection_id = hash(user_id) % partition_count
  return '{}-{}'.format(riv_stack_name, collection_id)

#@xray_recorder.capture('search_faces_by_image')
def search_faces_by_image(user_id:str, image:str)->dict:
  '''
  Invoke the Rekognition Search Faces By Image method.
  :param user_id: The user alias to query for.
  :param image: utf8(base64(photo bytes))
  :rtype: The response from Rekognition client.
  '''
  assert user_id is not None, "no user_id provided."
  assert image is not None, "no image provided."

 
  response = rek_client.search_faces_by_image(
    CollectionId= get_collection_id(user_id),
    FaceMatchThreshold= 0.80,
    MaxFaces=1,
    Image={
      'Bytes':b64decode(image)
    })
  return response


#@xray_recorder.capture('search_faces_by_image')
def search_faces(user_id:str, bucket:str , name:str)->dict:
  '''
  Invoke the Rekognition Search Faces By Image method.
  :param user_id: The user alias to query for.
  :param image: utf8(base64(photo bytes))
  :rtype: The response from Rekognition client.
  '''
  assert user_id is not None, "no user_id provided."
  assert bucket is not None or name is not None , "no image provided."

  response = rek_client.search_faces_by_image(
    CollectionId= get_collection_id(user_id),
    FaceMatchThreshold= 0.80,
    MaxFaces=1,
    Image={
        "S3Object": {
      'Bucket':bucket,
      'Name': name
        }
    })
  return response


def function_main(event:Mapping[str,Any],_=None):
  '''
  Main function handler.
  '''
  if event.get('Image', None) != None:
          response = search_faces_by_image(user_id= event['UserId'], image= event['Image'],)
  else:
      response = search_faces(user_id= event['UserId'],bucket=event['Bucket'], name=event['Name'])
  
  '''
  Annotate matches for step function integration.
  These additional properties simplify Choice conditions.
  '''
  matches = response['FaceMatches']
  for match in matches:
    match['Face']['IsCallerUser'] = event['UserId'] == match['Face']['ExternalImageId']

  top_match= None
  if len(matches) >0:
    top_match= matches[0]
  else:
    top_match = NO_FACE_MATCH

  return {
    'SearchedFaceBoundingBox': response['FaceModelVersion'],
    'SearchedFaceConfidence': response['SearchedFaceConfidence'],
    'FaceModelVersion' : response['FaceModelVersion'],
    'FaceMatches': response['FaceMatches'],
    'TopMatch': top_match,
    'HasMatches': len(response['FaceMatches']) > 0,
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
