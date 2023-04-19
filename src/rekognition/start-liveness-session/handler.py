from sys import prefix
import boto3
from base64 import b64decode
from os import environ, path
from typing import Any, Mapping
from json import loads
from logging import Logger
import json

client = boto3.client('rekognition')


def getSession():
    '''
    Get liveness session.
    '''
    # functions = [attr_name
    #                for attr_name in dir(client)
    #                if str(type(getattr(client,
    #                                    attr_name))) in ("<class 'function'>",
    #                                                     "<class 'method'>")]
    # print(functions)

    session = client.create_face_liveness_session(Settings={'AuditImagesLimit':1, 'OutputConfig': {"S3Bucket": environ.get('IMAGE_BUCKET_NAME')}})
    return session


def function_main(event, context):
    '''
    Main function handler.
    '''
    return {
        'statusCode': 200,
        'body': getSession()
    }


if __name__ == '__main__':
    # xray_recorder.begin_segment('LocalDebug')
    # payload = read_example_file('payload.json')
    getSession()
    # xray_recorder.end_segment()
