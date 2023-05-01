from enum import Enum
from typing import List, Mapping
from base64 import b64decode
#from aws_xray_sdk.core import xray_recorder

class InvalidImageError(Exception):
  '''
  Represents an error due to invalid image.
  '''
  pass

class TransientError(Exception):
  '''
  Represents a transient and retryable failure. 
  '''
  pass

class InputRequest:
  '''
  Represents the Lambda function input request.
  '''
  def __init__(self, event:Mapping[str,str]) -> None:
    assert event is not None, "No event specified."
    assert 'UserId' in event, "Missing required event.UserId attribute"
    assert 'IdCard' in event, "Missing required event.IdCard attribute"
    assert 'ImageName' in event, "Missing required event.ImageName attribute"

    self.__user_id = event['UserId']
    self.__idcard_image = b64decode(event['IdCard'])
    self.__image_name = event['ImageName']
    
    if 'Properties' in event:
      self.__properties = event['Properties']
    else:
      self.__properties = {}

  @property
  def user_id(self)->str:
    return self.__user_id

  @property
  def idcard_image_bytes(self)->bytes:
    return self.__idcard_image

  @property
  def property_bag(self)->dict:
    return self.__properties
  
  @property
  def image_name(self) -> str:
        return self.__image_name
