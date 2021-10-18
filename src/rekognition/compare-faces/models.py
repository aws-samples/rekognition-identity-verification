from typing import Any
from base64 import b64decode

class InputRequest:
  def __init__(self, event:dict) -> None:
    self.user_id = event['UserId']
    self.image_bytes = event['Image']
    
    if 'FaceId' in event:
      self.face_id = event['FaceId']
    else:
      self.face_id = 'FACEID_NOT_AVAIL'

    if 'Properties' in event:
      self.property_bag = event['Properties']
    else:
      self.property_bag = {}

  @property
  def user_id(self)->str:
    return self.__user_id

  @user_id.setter
  def user_id(self, value:str)->None:
    self.__user_id = value.lower()

  @property
  def face_id(self)->str:
    return self.__face_id

  @face_id.setter
  def face_id(self, value:str)->None:
    self.__face_id = value

  @property
  def image_bytes(self)->bytes:
    return self.__image

  @image_bytes.setter
  def image_bytes(self, value:Any)->None:
    if isinstance(value, bytes):
      self.__image = value
    elif isinstance(value, str):
      self.__image = b64decode(value)
    else:
      raise NotImplementedError()

  @property
  def property_bag(self)->dict:
    return self.__property_bag

  @property_bag.setter
  def property_bag(self, value:dict)->None:
    self.__property_bag = value

  def to_dyanmodb_item(self)->dict:
    '''
    Encodes this object as Amazon DyanmoDB Item.
    '''
    return {
      'PartitionKey': {'S': 'User::{}'.format(self.user_id)},
      'SortKey': {'S': self.face_id },
      #'image': {'B', self.image },
      'property_bag': {'M': InputRequest.ddb_encode_dict(self.property_bag) }
    }

  @staticmethod
  def ddb_encode_dict(dict:dict)->dict:
    encoded = {}
    for key in dict.keys():
      encoded[str(key)] = {'S': str(dict[key]) }
    return encoded

