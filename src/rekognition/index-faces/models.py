from typing import Any
from base64 import b64decode, b64encode

class FaceMetadata:
  def __init__(self, event:dict) -> None:
    self.user_id = event['UserId']
    #self.face_id = event['FaceId']
    self.image_bytes = event['Image'] if event.get('Image') != None else None
    self.bucket = event['Bucket']
    self.name = event['Name']
    self.property_bag = event['Properties']

  @property
  def user_id(self)->str:
    return self.__user_id

  @user_id.setter
  def user_id(self, value:str)->None:
    self.__user_id = value.lower().strip()
  
  @property
  def bucket(self)->str:
    return self.__bucket

  @bucket.setter
  def bucket(self, value:str)->None:
    self.__bucket = value.lower()
  
  @property
  def name(self)->str:
    return self.__name

  @name.setter
  def name(self, value:str)->None:
    self.__name = value.lower()

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
      self.__image = None

  @property
  def property_bag(self)->dict:
    return self.__property_bag

  @property_bag.setter
  def property_bag(self, value:dict)->None:
    self.__property_bag = value

  @staticmethod
  def ddb_encode_dict(dict:dict)->dict:
    encoded = {}
    for key in dict.keys():
      encoded[str(key)] = {'S': str(dict[key]) }
    return encoded

