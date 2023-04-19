import boto3

from typing import Mapping

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

   

  #@xray_recorder.capture('get_faces')
  def check_ID(self, user_id:str)->Mapping[str,str]:
    '''
    Gets every face associated with a given user.
    :param user_id:  The users alias.
    :returns: Check is ID exist or not
    '''
    assert user_id is not None, "user_id is missing"

    response = self.table.query(
      KeyConditionExpression=Key('PartitionKey').eq('User::'+user_id).__and__(Key('SortKey').begins_with('Face::')),
      )

    faces = []
    for item in response['Items']:
      face_id:str = str(item['PartitionKey']).replace('User::','',1).lower()
      print(face_id)
      faces.append(face_id)
    return faces

