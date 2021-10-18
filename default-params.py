#!/usr/bin/env python3
#########################################################
# Modifies a CloudFormation Template to include
#   default Stack Parameter values.
#########################################################

from os import environ
from json import loads,dumps
from sys import stderr

def get_asset_bucket()->str:
  '''
  Determines what bucket to use.
  '''
  bucket = environ.get('S3_ASSET_BUCKET')
  if not bucket is None:
    return bucket

  raise ValueError('Missing env TEMPLATE_ASSET_BUCKET and S3_ASSET_BUCKET')

def get_asset_prefix()->str:
  '''
  Gets the preferred Asset bucket prefix 
  '''
  prefix = environ.get('S3_ASSET_PREFIX')
  if prefix is None:
    prefix = ''
  
  return prefix.strip('/')

if __name__ == '__main__':
  '''
  The program main routine.
  '''
  #content = stdin.read()
  with open(environ.get('STACK_TEMPLATE_FILE'),'rt') as f:
    content = loads(f.read()) #stdin.read())

  parameters:dict = content['Parameters']
  for key in parameters.keys():
    key:str = key
    if not key.startswith('AssetParameters'):
      continue

    if 'Bucket' in key:
      parameters[key]['Default'] = get_asset_bucket()
    elif 'ArtifactHash' in key:
      start=len('AssetParameters')
      end=key.index('ArtifactHash')
      parameters[key]['Default'] = key[start:end] 
    elif 'VersionKey' in key:
      start=len('AssetParameters')
      end=key.index('S3VersionKey')
      sha = key[start:end]
      parameters[key]['Default'] = '%s/||asset.%s.zip' % (get_asset_prefix(), sha)
    else:
      stderr.write('ignoring %s' % key)

  #with open('cdk.out/OneClick.template.json', 'w') as f:
  #  f.write(dumps(content, indent=2))
  print(dumps(content, indent=2))
