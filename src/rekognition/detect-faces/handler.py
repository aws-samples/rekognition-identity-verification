import boto3
from exceptions import InvalidPoseDetectedException, NoFacesDetectedException, SunglassesDetectedException, TooManyFacesDetectedException
from os import environ, path
from typing import Any, Mapping
from json import dumps, loads
from logging import Logger
from base64 import b64decode

'''
Initialize the function runtime.
'''
logger = Logger(name='LambdaFunction')

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
client = boto3.client('rekognition', region_name=environ.get('REGION'))

def valid_pose_value(value:float)->bool:
  '''
  Check that a pose angle is within an acceptable range.
  '''
  assert value is not None, "valid_pose_value missing value"
  return -45 < value and value < 45

#@xray_recorder.capture('detect_faces')
def detect_faces(image:str)->dict:
  '''
  Invoke the rekognition:detect_faces method.
  :param image: The utf8(base64( image-bytes ))
  :rtype: The response from detect_faces method.
  '''
  assert image is not None, "detect_faces missing image argument."

  response = client.detect_faces(
    Attributes=['ALL'],
    Image={
      'Bytes':b64decode(image)
    })
  return response

def function_main(event:Mapping[str,Any], _=None):
  '''
  Convert the input into a Amazon Rekognition call...
  '''
  response = detect_faces(event['Image'])

  '''
  Confirm the face is usable...
  '''
  valid_faces = [face for face in response['FaceDetails'] if face['Confidence'] > 90]
  if len(valid_faces) == 0:
    raise NoFacesDetectedException()
  elif len(valid_faces) > 1:
    raise TooManyFacesDetectedException()

  user_face = valid_faces[0]

  '''
  Confirm the face position is within range
  Each pose dimension is between -180 to 180 degress
  '''
  pose = user_face['Pose']
  for dimension in ['Pitch','Roll','Yaw']:
    if not valid_pose_value(pose[dimension]):
      raise InvalidPoseDetectedException(dimension)

  '''
  Do not permit users to wear sunglasses
  '''
  if user_face['Sunglasses']['Value']:
    raise SunglassesDetectedException()

  '''
  Return the valid faces...
  '''
  return {
    'FaceDetails': user_face
  }

def read_example_file(filename:str)->Mapping[str,Any]:
  example_dir = path.join(path.dirname(__file__),'examples')
  file = path.join(example_dir, filename)

  with open(file, 'r') as f:
    return loads(f.read())

if __name__ == '__main__':
  xray_recorder.begin_segment(name='LocalDebug')
  payload = read_example_file('nbachmei.json')
  function_main(payload)
  xray_recorder.end_segment()