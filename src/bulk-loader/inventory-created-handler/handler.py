import boto3
from lib.parser import S3ObjectRef, ManifestParser
from os import environ, path
from typing import Any, List, Mapping
from json import dumps, loads
from logging import Logger

'''
Initialize the environment
'''
logger = Logger(name='LambdaFunction')
ACCOUNT_ID = environ.get('ACCOUNT_ID')
BATCH_FUNCTION_ARN = environ.get('BATCH_FUNCTION_ARN')
BATCH_ROLE_ARN = environ.get('BATCH_ROLE_ARN')
ZONE_NAME= environ.get('ZONE_NAME')

assert ACCOUNT_ID is not None, "ACCOUNT_ID is missing"
assert BATCH_FUNCTION_ARN is not None, "BATCH_FUNCTION_ARN is missing"
assert BATCH_ROLE_ARN is not None, "BATCH_ROLE_ARN is missing"
assert ZONE_NAME is not None, "ZONE_NAME is missing"

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
s3control = boto3.client('s3control', region_name=environ.get('REGION'))

def create_manifest_parser(record:dict)->ManifestParser:
  '''
  Creates a manifest parser for the S3 Inventory Report.
  '''
  region_name = record['awsRegion']
  bucket_name = record['s3']['bucket']['name']
  object_key = record['s3']['object']['key']
  return ManifestParser(bucket_name, object_key, region_name)

def should_process(objectRef:S3ObjectRef)->bool:
  '''
  Checks if the given S3ObjectRef should be included in the job. 
  '''
  key = objectRef.object_key.lower()
  if key.endswith('.png') or key.endswith('.jpg'):
    return True
  return False

#@xray_recorder.capture('process_message_record')
def process_message_record(record:dict)->dict:
  '''
  Process an individual notification record.
  
  :param record:  A single notification within the ObjectCreatedNotification message.
  :rtype: The response from the s3control.create_job operation.
  '''
  references:List[S3ObjectRef] = []
  parser = create_manifest_parser(record)
  if parser.manifest_object_key.startswith('reports/'):
    logger.info(
      'Skipping process_message_record for reports manifest - {} '.format(
        parser.manifest_object_key))
    return None

  for file in parser.manifest_files:
    for reference in parser.fetch_inventory_entries(file):
      if should_process(reference):
        references.append(reference)

  '''
  Write the inventory list for processing.
  '''
  inventory_report_name = parser.get_inventory_report_name()
  object_key ='input/{}.csv'.format(inventory_report_name)
  putObjectResponse = parser.write_reference_list(references, object_key=object_key)

  '''
  Run the batch job.
  '''
  createJobResponse = s3control.create_job(
    AccountId=ACCOUNT_ID,
    ConfirmationRequired=False,
    Operation={
      'LambdaInvoke':{
        'FunctionArn': BATCH_FUNCTION_ARN
      }
    },
    Report= {
      'Bucket': "arn:aws:s3:::{}".format(parser.inventory_bucket_name),
      'Prefix': 'reports',
      "Format": "Report_CSV_20180820",
      "Enabled": True,
      "ReportScope": "AllTasks"
    },
    ClientRequestToken=inventory_report_name,
    Manifest= {
      "Spec": {
        "Format": "S3BatchOperations_CSV_20180820",
        "Fields": [
          "Bucket",
          "Key"
        ]
      },
      "Location": {
        'ObjectArn':"arn:aws:s3:::riv-simple-sharedstorageimagesinventorybucketab8f-qlx62dgkgypf/input/Full-InventoryReport/2021-08-16T01-00Z.csv",
        'ETag': putObjectResponse['ETag'].strip('"'),
      }
    },
    Description='RivSimple Import',
    Priority=123,
    RoleArn=BATCH_ROLE_ARN,
    Tags=[
      {'Key':'landing_zone', 'Value': ZONE_NAME},
      {'Key':'inventory_bucket', 'Value': parser.inventory_bucket_name},
      {'Key':'content_bucket', 'Value': references[0].bucket_name},
    ])

  return createJobResponse

def function_main(event:Mapping[str,Any],_=None):
  '''
  Main Lambda Function entry point.
  
  :param event:  An ObjectCreatedNotification message from S3.
  '''
  logger.debug(dumps(event))
  
  '''
  Extract and filter the inventory report to only applicable content. 
  '''
  for record in event['Records']:
    process_message_record(record)
    
def read_example_file(filename:str)->Mapping[str,Any]:
  example_dir = path.join(path.dirname(__file__),'examples')
  file = path.join(example_dir, filename)

  with open(file, 'r') as f:
    return loads(f.read())

if __name__ == '__main__':
  xray_recorder.begin_segment('LoadDebug')
  sqs_message = read_example_file('sqs_message.json')
  function_main(sqs_message)
