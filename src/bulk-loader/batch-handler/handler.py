from lib.importhistory import ImportHistoryManager
from lib.registrationproviders import S3TagUserRegistrationInfo
from lib.models import BatchRequest, BatchResponse, BatchTask, BatchTaskResult, TaskResultCode
import boto3
from os import environ, path
from typing import Any, List, Mapping
from json import dumps, loads
from logging import Logger

'''
Initialize the environment
'''
logger = Logger(name='LambdaFunction')
THROTTLED_QUEUE_URL = environ.get('THROTTLED_QUEUE_URL')

assert THROTTLED_QUEUE_URL is not None, "THROTTLED_QUEUE_URL is missing"

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
sqs = boto3.client('sqs', region_name=environ.get('REGION'))
import_table = ImportHistoryManager(region_name=environ.get('REGION'))

'''
Important: Configure your registration source here 
'''
registration_data_provider = S3TagUserRegistrationInfo(region_name=environ.get('REGION'))

#@xray_recorder.capture('process_task')
def process_task(task:BatchTask) ->BatchTaskResult:
  '''
  Processes an individual Amazon S3 Batch Task.
  '''
  user_data = registration_data_provider.get_registration_data(task)
  if not user_data.is_valid:
    return BatchTaskResult(task.taskId, TaskResultCode.SUCCEEDED, 'Skipping invalid object.')

  '''
  Confirm this task qualifies for processing.
  '''
  if not import_table.qualifies_for_processing(
    user_id=user_data.user_id,
    task= task):
    return BatchTaskResult(task.taskId, TaskResultCode.SUCCEEDED, 'Skipping non-qualified object')

  '''
  Write the message into the throttling queue.
  The throttled-indexer will pull these messages and process them.
  '''
  response = sqs.send_message(
    QueueUrl= THROTTLED_QUEUE_URL,
    MessageBody = dumps({
      'BucketArn': task.s3BucketArn,
      'ObjectKey': task.s3Key,
      'InputRequest': user_data.to_dict(),
    })
  )
  return BatchTaskResult(task.taskId, TaskResultCode.SUCCEEDED, 'Queued message {}'.format(response['MessageId']))

def function_main(event:Mapping[str,Any],_=None):
  '''
  Main Lambda Function entry point.
  https://docs.aws.amazon.com/lambda/latest/dg/services-s3-batch.html
  
  :param event:  An Amazon S3 batch request.
  '''
  print(dumps(event))
  inputRequest = BatchRequest(event)
  
  '''
  Process the incoming tasks. 
  '''
  response = BatchResponse(invocationId=inputRequest.invocationId)
  for task in inputRequest.tasks:
    response.results.append(process_task(task))

  return response.to_dict()
    
def read_example_file(filename:str)->Mapping[str,Any]:
  example_dir = path.join(path.dirname(__file__),'examples')
  file = path.join(example_dir, filename)

  with open(file, 'r') as f:
    return loads(f.read())

if __name__ == '__main__':
  xray_recorder.begin_segment('LocalDebug')
  batchRequest = read_example_file('payload.json')
  function_main(batchRequest)
  xray_recorder.end_segment()
