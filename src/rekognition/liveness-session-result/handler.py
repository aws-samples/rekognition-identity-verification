from sys import prefix
import boto3
from base64 import b64decode
from os import environ, path
from typing import Any, Mapping
from logging import Logger
from json import loads
from logging import Logger
import base64
import json
import sys

'''
Initialize the runtime.
'''
region_name = environ.get('REGION')
logger = Logger(name='LambdaFunction')


client = boto3.client('rekognition', region_name=environ.get('REGION'))
s3 = boto3.resource('s3')

def session_result(sessionid):
  '''
  Get Session result.
  '''
  session = client.get_face_liveness_session_results(SessionId=sessionid)
  print(session)
  return session

def function_main(event, context):
    output = session_result(event['sessionid'])
    if output and output['ReferenceImage']:
      bucketName = output['ReferenceImage']['S3Object']['Bucket']
      keyName = output['ReferenceImage']['S3Object']['Name']
      bucket = s3.Bucket(bucketName) 
      obj = bucket.Object(keyName)
      response = obj.get()  
      img = response['Body'].read() 
      myObj = [base64.b64encode(img)]  
      return_json = str(myObj[0])
      return_json = return_json.replace("b'","")  
      encoded_image = return_json.replace("'","")   
      output['ReferenceImageBase64'] = encoded_image
      return {
          'statusCode': 200,
          'body': output
    }

if __name__ == '__main__':
  # xray_recorder.begin_segment('LocalDebug')
  # payload = read_example_file('payload.json')
  args = sys.argv[1]
  print(args)
  session_result(args)
  # xray_recorder.end_segment()
