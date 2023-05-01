from ast import Str
from ddb import FaceTableClient

import boto3
from os import environ, path
from typing import Any, Mapping, Tuple
from json import loads
from logging import Logger


'''
Initialize the runtime.
'''
region_name = environ.get('REGION')
logger = Logger(name='LambdaFunction')
SIMILARITY_THRESHOLD = 95.0

'''
Prepare XRAY, if available.
'''
try:
    from aws_xray_sdk.core import xray_recorder, patch_all
    patch_all()  # Instrument all AWS methods.
except:
    print('AWS XRAY support not available.')

'''
Initialize any clients (... after xray!)
'''
rek_client = boto3.client('rekognition', region_name=environ.get('REGION'))
face_table_client = FaceTableClient(environ.get(
    'FACE_TABLE_NAME'), region_name=region_name)

def choose_random_face(faces: Mapping[str, str]) -> Tuple[str, str]:
    '''
    Chooses a random face from the set.
    :returns: face_id (str) and image (bytes)
    '''
    faceids = list(faces.keys())
    ix = randint(0, len(faceids)-1)
    return faceids[ix], faces[faceids[ix]]


def function_main(event: Mapping[str, Any], _=None):
    userId = event['UserId']

    '''
  Retrieve the face information.
  If an exact match exists, we're done.
  '''
    faces = face_table_client.check_ID(userId)
    if userId in faces:
        return {
            'Reason': 'User Exist'
        }
    else:
        return {
            'Reason': 'User not Exist'
        }

def read_example_file(filename: str) -> Mapping[str, Any]:
    example_dir = path.join(path.dirname(__file__), 'examples')
    file = path.join(example_dir, filename)

    with open(file, 'r') as f:
        return loads(f.read())

if __name__ == '__main__':
    xray_recorder.begin_segment('LocalDebug')
    payload = read_example_file('payload.json')
    function_main(payload)
    xray_recorder.end_segment()