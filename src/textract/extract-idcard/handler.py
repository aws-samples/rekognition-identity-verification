from model import InputRequest, InvalidImageError, TextractDocument
import boto3
from docparser import DocumentParser
from base64 import b64encode, b64decode
from os import environ, path
from typing import Any, List, Mapping
from json import loads, dumps
from logging import Logger

'''
Initialize the function runtime
'''
logger = Logger(name='LambdaFunction')
region_name = environ.get('REGION')
assert region_name is not None, "region_name is not available"

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
textract_client = boto3.client('textract', region_name=region_name)

#@xray_recorder.capture('DocumentParser::extract_form')
def analyze_id(inputRequest:InputRequest)->dict:
  '''
  Analyze the image using Amazon Textract.
  '''
  try:
    response = textract_client.analyze_id(
      DocumentPages=[
        {'Bytes': inputRequest.idcard_image_bytes},
      ])

    return response
  except textract_client.exceptions.UnsupportedDocumentException:
    logger.error('User %s provided an invalid document.' % inputRequest.user_id)
    raise InvalidImageError('UnsupportedDocument')
  except textract_client.exceptions.DocumentTooLargeException:
    logger.error('User %s provided document too large.' % inputRequest.user_id)
    raise InvalidImageError('DocumentTooLarge')
  except textract_client.exceptions.ProvisionedThroughputExceededException:
    logger.error('Textract throughput exceeded.')
    raise InvalidImageError('ProvisionedThroughputExceeded')
  except textract_client.exceptions.ThrottlingException:
    logger.error('Textract throughput exceeded.')
    raise InvalidImageError('ThrottlingException')
  except textract_client.exceptions.InternalServerError:
    logger.error('Textract Internal Server Error.')
    raise InvalidImageError('ProvisionedThroughputExceeded')

def function_main(event:Mapping[str,Any],_=None):
  '''
  Main function handler.
  '''
  #print(dumps(event))
  inputRequest = InputRequest(event)
  response = analyze_id(inputRequest)
  
  '''
  Create a document parser and extract a table.
    Customers can include additional business logic here (e.g., confirm company watermarks).  
  '''
  if not len(response['IdentityDocuments']) == 1:
    raise NotImplementedError('Sample does not support multiple documents.')

  '''
  Generate a response based on the input.
  '''
  properties = inputRequest.property_bag
  document_fields:List[dict] = response['IdentityDocuments'][0]['IdentityDocumentFields']
  for field in document_fields:
    key = field['Type']['Text']
    value = field['ValueDetection']['Text']    
    properties[key] = value

  return {
    'UserId': inputRequest.user_id,
    'Properties': properties
  }

def read_example_file(filename:str)->Mapping[str,Any]:
  '''
  Create a valid test payload from the examples folder.
  '''
  example_dir = path.join(path.dirname(__file__),'examples')
  file = path.join(example_dir, filename)

  if file.endswith('.jpeg'):
    with open(file, 'rb') as f:
      return {
        'UserId': 'LocalDebug',
        'Image': str(b64encode(f.read()),'utf-8'),
      }

  with open(file, 'rt') as f:
    return loads(f.read())

if __name__ == '__main__':
  xray_recorder.begin_segment('LocalDebug')
  #payload = read_example_file('passport_card.jpeg')
  payload = read_example_file('payload.json')
  function_main(payload)
  xray_recorder.end_segment()
