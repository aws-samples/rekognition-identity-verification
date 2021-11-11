from lib.storage import StorageClient
import boto3
from requests import post
from lib.models import SQSMessage, SQSMessageRecord
from os import environ, path
from typing import Any, List, Mapping
from json import dumps, loads
from logging import Logger

'''
Initialize the environment
'''
logger = Logger(name='LambdaFunction')
USER_PORTAL_PARAM = environ.get('USER_PORTAL_PARAM')
REGION_NAME = environ.get('REGION')
RIV_STACK_NAME =environ.get('RIV_STACK_NAME')

assert USER_PORTAL_PARAM is not None, "USER_PORTAL_PARAM is missing"
assert REGION_NAME is not None, "REGION_NAME is missing"

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
storage_client = StorageClient(region_name=REGION_NAME)
ssm_client = boto3.client('ssm', region_name=REGION_NAME)

'''
Discover the UserPortal Address.
'''
def get_user_portal_url()->str:
  '''
  Gets the UserPortal public endpoint.
  '''
  #xray_recorder.begin_segment('get_user_portal_url')
  try:
    #xray_recorder.context.context_missing
    parameter_name = '/riv/{}/userportal/url'.format(RIV_STACK_NAME)
    
    response = ssm_client.get_parameter(Name=parameter_name)
    value:str = response['Parameter']['Value']

    if value is None:
      raise ValueError('No userportal url available.')
    if not value.startswith('http'):
      raise ValueError('UserPortalUrl in unexpected format: '.format(value))

    return value
  except Exception as error:
    logger.error('Unable to get_user_portal_url.')
    raise error
  finally:
    #xray_recorder.end_segment()
    pass

USER_PORTAL_URL = get_user_portal_url()

#@xray_recorder.capture('process_sqs_record')
def process_sqs_record(record:SQSMessageRecord)->None:
  '''
  Process an individual SQS message.
  '''
  payload = storage_client.attach_image(record.payload)
  post(url='{}/register'.format(USER_PORTAL_URL), json=payload.input_request)
  storage_client.write_index_complete(payload)

def function_main(event:Mapping[str,Any],_=None):
  '''
  Main Lambda Function entry point.
  https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
  
  :param event:  An SQS message event.
  '''
  logger.debug(dumps(event))
  message = SQSMessage(event)
  
  '''
  Enumerate through the incoming records and process them sequentially. 
  '''
  for record in message.records:
    process_sqs_record(record)

def read_example_file(filename:str)->Mapping[str,Any]:
  example_dir = path.join(path.dirname(__file__),'examples')
  file = path.join(example_dir, filename)

  with open(file, 'r') as f:
    return loads(f.read())

if __name__ == '__main__':
  xray_recorder.begin_segment('LocalDebug')
  sqs_message = read_example_file('payload.json')
  function_main(sqs_message)
  xray_recorder.end_segment()
