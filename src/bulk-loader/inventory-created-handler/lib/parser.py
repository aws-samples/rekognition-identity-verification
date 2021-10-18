import boto3
import gzip
from urllib.parse import quote
from typing import Any, List, Mapping
from json import dumps, loads
#from aws_xray_sdk.core import xray_recorder

class S3ObjectRef:
  '''
  Represents an Amazon S3 object location.
  '''
  def __init__(self, csv_line) -> None:
    cells = [cell.strip('"') for cell in csv_line.split(',', maxsplit=2)]
    self.__bucket_name = cells[0]
    self.__object_key = cells[1]

  @property
  def bucket_name(self)->str:
    '''
    Gets the name of the bucket.
    :rtype: str
    '''
    return self.__bucket_name

  @property
  def object_key(self)->str:
    '''
    Gets the S3 object key within the bucket.
    '''
    return self.__object_key

  def to_csv(self)->str:
    '''
    Creates an Amazon S3 Batch CSV entry.
    '''
    return "{},{}".format(
      self.bucket_name,
      quote(self.object_key)
    )

class ManifestParser:
  '''
  Represents an Amazon S3 Inventory Manifest Parser.
  '''
  def __init__(self, inventory_bucket_name:str, object_key:str, region_name:str) -> None:
    assert inventory_bucket_name != None, "No bucket_name"
    assert object_key != None, "No object_key"
    assert region_name != None, "No region_name"

    self.__inventory_bucket_name = inventory_bucket_name
    self.__manifest_object_key = object_key
    self.__region_name = region_name
    self.storage_client = boto3.client('s3', region_name=region_name)
    self.manifest_json = self.__fetch_manifest(object_key=object_key)

  @property
  def inventory_bucket_name(self)->str:
    '''
    Gets the name of the bucket holding the report.
    '''
    return self.__inventory_bucket_name

  @property
  def manifest_object_key(self)->str:
    '''
    Gets the S3 object key of the inventory manifest file.
    '''
    return self.__manifest_object_key

  @property
  def region_name(self)->str:
    '''
    Gets the region hosting the inventory bucket.
    '''
    return self.__region_name

  @property
  def manifest_files(self)->List[str]:
    '''
    Gets the individual file "chunks" that makeup the Inventory Report.
    '''
    return [x['key'] for x in self.manifest_json['files']]

  def __fetch_manifest(self, object_key)->Mapping[str,Any]:
    '''
    Fetch the specified inventory manifest definition from the inventory bucket.

    This is a private function external callers should not reference.
    '''
    response:dict = self.storage_client.get_object(
      Bucket=self.inventory_bucket_name,
      Key=object_key)

    contents = response['Body'].read()
    return loads(contents)

  #@xray_recorder.capture('fetch_inventory_entries')
  def fetch_inventory_entries(self, object_key:str)->List[S3ObjectRef]:
    '''
    Gets the inventory content from the specific object key.
    :param object_key: Likely an item from the manifest_files list.
    :rtype: List of S3 objects references.
    '''
    assert object_key is not None, "No object_key given to fetch_inventory_entries"

    response = self.storage_client.get_object(
      Bucket=self.inventory_bucket_name,
      Key=object_key)

    csv_content = gzip.decompress(response['Body'].read())
    csv_content = csv_content.decode().splitlines()
    references = []
    for line in csv_content:
      references.append(S3ObjectRef(line))

    return references

  #@xray_recorder.capture('write_reference_list')
  def write_reference_list(self,references:List[S3ObjectRef], object_key:str)->dict:
    '''
    Creates the Amazon S3 Batch expects manifest files in json or csv format.
    https://aws.amazon.com/blogs/storage/cross-account-bulk-transfer-of-files-using-amazon-s3-batch-operations/
    
    :param references:  The list of S3 objects to process through Amazon S3 Batch.
    :param object_key:  The output Amazon S3 object key (aka filename) in the inventory bucket.
    :rtype dict:  The response from s3:PutObject.
    '''
    assert references != None, "No references"
    assert len(references) != 0, "Empty reference list"
    assert object_key is not None, "No object key specified."

    # Encode for Amazon S3 Batch.
    body = []
    for ref in references:
      body.append(ref.to_csv())
    body = '\n'.join(body)

    # Write the object...
    response:dict = self.storage_client.put_object(
      Bucket = self.inventory_bucket_name,
      Key = object_key,
      Body=body.encode()
    )
    return response

  def get_inventory_report_name(self)->str:
    '''
    Gets the Amazon S3 Inventory Report from the manifest.

    Note: Manifest files emit to paths like:
    s3://inventory-bucket/prefix/image-bucket/report_name/date/manifest.json
    '''
    folders= self.manifest_object_key.split('/')
    return '{}/{}'.format(folders[-3],folders[-2])
