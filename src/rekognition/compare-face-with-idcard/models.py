from typing import Any
from base64 import b64decode

class InputRequest:
  def __init__(self, event:dict) -> None:
    self.user_id = event['UserId']
    self.image_bytes = event['Image'] if event.get('Image') != None else None
    # self.idcard_image_bytes = event['IdCard']
    self.bucket = event['Bucket']
    self.name = event['Name']
    print(event['IdCardName'])
    self.idcard_name = event['IdCardName']
    
  @property
  def user_id(self)->str:
    return self.__user_id

  @user_id.setter
  def user_id(self, value:str)->None:
    self.__user_id = value.lower()

  @property
  def bucket(self)->str:
    return self.__bucket

  @bucket.setter
  def bucket(self, value:str)->None:
    self.__bucket = value


  @property
  def name(self)->str:
    return self.__name

  @name.setter
  def name(self, value:str)->None:
    self.__name = value

  @property
  def idcard_name(self)->str:
    return self.__idcard_name

  @idcard_name.setter
  def idcard_name(self, value:str)->None:
    self.__idcard_name = value
 
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




