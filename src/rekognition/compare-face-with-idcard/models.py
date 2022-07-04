from typing import Any
from base64 import b64decode

class InputRequest:
  def __init__(self, event:dict) -> None:
    self.user_id = event['UserId']
    self.image_bytes = event['Image']
    self.idcard_image_bytes = event['IdCard']
    
  @property
  def user_id(self)->str:
    return self.__user_id

  @user_id.setter
  def user_id(self, value:str)->None:
    self.__user_id = value.lower()

 
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
  def idcard_image_bytes(self)->bytes:
    return self.__idcard

  @idcard_image_bytes.setter
  def idcard_image_bytes(self, value:Any)->None:
    if isinstance(value, bytes):
      self.__idcard = value
    elif isinstance(value, str):
      self.__idcard = b64decode(value)
    else:
      raise NotImplementedError() 




