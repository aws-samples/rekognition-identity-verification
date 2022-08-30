import boto3
from base64 import b64decode
from os import environ, path
from typing import Any, Mapping
from json import loads
from logging import Logger

'''
Initialize the function runtime
'''
logger = Logger(name='LambdaFunction')
riv_stack_name = environ.get('RIV_STACK_NAME')
region_name = environ.get('REGION')
assert riv_stack_name is not None, "riv_stack_name is not available"
assert region_name is not None, "region_name is not available"

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

ddb = boto3.resource('dynamodb', region_name=region_name)

table = ddb.Table(environ.get('FACE_TABLE_NAME'))


def function_main(event: Mapping[str, Any], _=None):
    '''
    Main function handler.
    '''
    collectionID = riv_stack_name+'-0'
    scan = table.scan()
    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(
                Key={
                    'PartitionKey': each['PartitionKey'],
                    "SortKey": each['SortKey']
                }
            )

    deleteCollection = rek_client.delete_collection(
        CollectionId=collectionID
    )
    createCollection = rek_client.create_collection(
        CollectionId=collectionID
    )
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': "RIV data reset successfully"
    }


if __name__ == '__main__':
    xray_recorder.begin_segment('LocalDebug')
    function_main()
    xray_recorder.end_segment()
