from sys import prefix
import boto3
from base64 import b64decode
from os import environ, path
from typing import Any, Mapping
from json import loads
from logging import Logger
import json

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

class FaceLivenessError(Exception):
    '''
    Represents an error due to Face Liveness Issue.
    '''
    pass

def getSession():
    '''
    Get liveness session.
    '''
    try:
        session = rek_client.create_face_liveness_session(Settings={'AuditImagesLimit':1, 'OutputConfig': {"S3Bucket": environ.get('IMAGE_BUCKET_NAME')}})
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
    except rek_client.exceptions.ThrottlingException:
        logger.error('ThrottlingException')
        raise FaceLivenessError('ThrottlingException')
    except rek_client.exceptions.ProvisionedThroughputExceededException:
        logger.error('ProvisionedThroughputExceededException')
        raise FaceLivenessError('ProvisionedThroughputExceededException')


def function_main(event, context):
    '''
    Main function handler.
    '''
    return {
        'statusCode': 200,
        'body': getSession()
    }


if __name__ == '__main__':
    xray_recorder.begin_segment('LocalDebug')
    getSession()
    xray_recorder.end_segment()
