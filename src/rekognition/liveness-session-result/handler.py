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

'''
Prepare XRAY, if available.
'''
try:
    from aws_xray_sdk.core import xray_recorder, patch_all
    patch_all()  # Instrument all AWS methods.
except:
    print('AWS XRAY support not available.')

'''
Initialize any clients (... after xray!)
'''
rek_client = boto3.client('rekognition', region_name=region_name)

s3 = boto3.resource('s3', region_name=region_name)


class FaceLivenessError(Exception):
    '''
    Represents an error due to Face Liveness Issue.
    '''
    pass


def session_result(sessionid):
    '''
    Get Session result.
    '''
    try:
        session = rek_client.get_face_liveness_session_results(
            SessionId=sessionid)
        return session

    except rek_client.exceptions.AccessDeniedException:
        logger.error('Access Denied Error')
        raise FaceLivenessError('AccessDeniedError')
    except rek_client.exceptions.InternalServerError:
        logger.error('InternalServerError')
        raise FaceLivenessError('InternalServerError')
    except rek_client.exceptions.InvalidParameterException:
        logger.error('InvalidParameterException')
        raise FaceLivenessError('InvalidParameterException')
    except rek_client.exceptions.SessionNotFoundException:
        logger.error('SessionNotFound')
        raise FaceLivenessError('SessionNotFound')
    except rek_client.exceptions.ThrottlingException:
        logger.error('ThrottlingException')
        raise FaceLivenessError('ThrottlingException')
    except rek_client.exceptions.ProvisionedThroughputExceededException:
        logger.error('ProvisionedThroughputExceededException')
        raise FaceLivenessError('ProvisionedThroughputExceededException')


def function_main(event, context):
    assert event['sessionid'] is not None, "SessionID is not available"
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
        return_json = return_json.replace("b'", "")
        encoded_image = return_json.replace("'", "")
        output['ReferenceImageBase64'] = encoded_image
        return {
            'statusCode': 200,
            'body': output
        }


if __name__ == '__main__':
    xray_recorder.begin_segment('LocalDebug')
    args = sys.argv[1]
    print(args)
    session_result(args)
    xray_recorder.end_segment()
