import boto3
from errors import InvalidImageExtensionException, InvalidImageUriException
from typing import Mapping
from urllib.parse import urlparse
from boto3.dynamodb.conditions import BeginsWith, Key
from boto3.dynamodb.conditions import Key, Attr
from base64 import b64encode
#from aws_xray_sdk.core import xray_recorder


class FaceTableClient:
  '''
  Represents a storage client for querying Facial metadata.
  '''
  def __init__(self, table_name:str, region_name:str) -> None:
    '''
    Initializes a new instance of the FaceTableClient.
    :param table_name: The DyanmoDB table name.
    :param region_name: The Amazon region hosting the table.
    '''
    assert table_name is not None, "No table_name available"
    assert region_name is not None, "No region_name available"

    ddb = boto3.resource('dynamodb', region_name=region_name)
    self.table = ddb.Table(table_name)

    self.s3 = boto3.client('s3', region_name=region_name)

  #@xray_recorder.capture('get_faces')
  def get_faces(self, user_id:str)->Mapping[str,str]:
    '''
    Gets every face associated with a given user.
    :param user_id:  The users alias.
    :returns: Map face_id (str) to image (bytes)
    '''
    assert user_id is not None, "user_id is missing"

    response = self.table.query(
      KeyConditionExpression=Key('PartitionKey').eq('User::'+user_id).__and__(Key('SortKey').begins_with('Face::')),
      )

    faces = {}
    for item in response['Items']:
      face_id:str = str(item['SortKey']).replace('Face::','',1).lower()
      if 'image' in item:
        faces[face_id] = item['image']
      elif 'bucket' in item:
        faces[face_id] = {'bucket':item['bucket'],'name':item['name']}
      else:
        #faces[face_id] = None
        print('user {} - face_id {} has no face.'.format(user_id,face_id))
    
    return faces


  #@xray_recorder.capture('get_image_from_uri')
  def __get_image_from_uri(self, s3_uri:str)->bytes:
    '''
    Downloads the requested image from Amazon S3.
    :param s3_uri: The path in format s3://bucket/key.
    :rtype: The raw image bytes.
    '''
    #xray_recorder.current_subsegment().put_annotation('s3_uri', s3_uri)
    url = urlparse(s3_uri)

    if url.scheme != 's3':
      raise InvalidImageUriException(
        'get_image_from_uri only supports s3://bucket/key format.')

    bucket = url.netloc
    key = url.path.lstrip('/')

    if not key.lower().endswith('.png') and not key.lower().endswith('.jpg'):
      raise InvalidImageExtensionException(
        'get_image_from_uri only supports .png and .jpg files.')

    '''
    Retrieve the object from the bucket.
    '''
    response = self.s3.get_object(Bucket=bucket,Key=key)
    return response['Body'].read()
