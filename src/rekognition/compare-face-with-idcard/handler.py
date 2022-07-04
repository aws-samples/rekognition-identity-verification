from ddb import FaceTableClient
from models import InputRequest
import boto3
from os import environ, path
from typing import Any, Mapping, Tuple
from json import loads
from logging import Logger
from random import randint
from base64 import b64decode

'''
Initialize the runtime.
'''
region_name= environ.get('REGION')
logger = Logger(name='LambdaFunction')
SIMILARITY_THRESHOLD = 95.0

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
rek_client = boto3.client('rekognition', region_name=environ.get('REGION'))
face_table_client = FaceTableClient(environ.get('FACE_TABLE_NAME'), region_name=region_name)

def function_main(event:Mapping[str,Any],_=None):
  inputRequest = InputRequest(event)
 
  '''
  Otherwise compare a historical record against the input
  '''
  try:
    response = rek_client.compare_faces(
      SimilarityThreshold=0.9,
      SourceImage={
        'Bytes': inputRequest.idcard_image_bytes
      },
      TargetImage={
        'Bytes': inputRequest.image_bytes
      })

    '''
    Confirm these are approximately the same image.
    '''
    if len(response['FaceMatches']) == 0:
      return { 
        'IsMatch':False,
        'Reason': 'Property $.FaceMatches is empty.'
      }
    facenotMatch = False
    for match in response['FaceMatches']:
      similarity:float = match['Similarity']
      if similarity > SIMILARITY_THRESHOLD:
        return { 
          'IsMatch':True,
          'Reason': 'All checks passed.'
        }
      else:
        facenotMatch = True
    if facenotMatch:
      return { 
          'IsMatch':False,
          'Reason': 'Similarity comparison was below threshold (%f < %f).' % (similarity, SIMILARITY_THRESHOLD)
      }
      
    return { 
      'IsMatch':True,
      'Reason': 'All checks passed.'
    }
  except Exception as error:
    print('Comparing({}) to ID Card failed - {}'.format(
      inputRequest.user_id, str(error)))
    raise error

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

 