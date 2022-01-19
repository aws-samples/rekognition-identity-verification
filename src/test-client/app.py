import click
import http
import boto3
import requests
import names
from json import dumps, loads
from typing import Mapping
from  base64 import b64encode
from os import PathLike
from random import randint
from pygments import highlight, formatters
from pygments.lexers import JsonLexer

def get_userportal_address(region_name:str, riv_stack_name:str, endpoint:str)->str:
  '''
  Gets the User Portal public endpoint.
  '''
  ssm_client = boto3.client('ssm', region_name=region_name)
  parameter_name='/riv/{}/userportal/url'.format(riv_stack_name)
  try:
    response = ssm_client.get_parameter(Name=parameter_name)
  except Exception as error:
    print('[ERROR] ssm:GetParameter(name=%s, region=%s) failed. - %s' % (parameter_name,region_name, str(error)))
    exit(1)
    
  userportal_url:str = response['Parameter']['Value']
  if not userportal_url.endswith('/'):
    userportal_url = userportal_url + '/'

  return userportal_url + endpoint.lstrip('/')

def create_payload(image_path:PathLike=None, user_id:str=None, properties:Mapping[str,str]=None, idcard:PathLike=None)->dict:
  '''
  Creates a valid payload for testing. 
  '''
  if user_id is None:
    user_id = str(randint(10000000,100000000-1))

  if properties is None:
    properties = {
      'age' : str(randint(1,80)),
      'fname': names.get_first_name(),
      'lname': names.get_last_name()
    }

  payload = {
    'UserId': user_id,
    #'Image': str(b64encode(photo_contents),'utf-8'),
    'Properties': properties
  }

  if image_path is not None:
    with open(image_path,'rb') as f:
      photo_contents = f.read()
      payload['Image'] = str(b64encode(photo_contents),'utf-8')

  if idcard is not None:
    with open(image_path,'rb') as f:
      photo_contents = f.read()
      payload['IdCard'] = str(b64encode(photo_contents),'utf-8')

  return payload

def print_response(response:requests.models.Response)->None:
  '''
  Write the friendly output for developers
  '''
  response_json = loads(response.content)

  print('=' * 20)
  print('[%d] : Endpoint Response %s.' % (response.status_code, http.HTTPStatus(response.status_code).name))
  print('[%s] : Operation Result' % response_json['status'] if 'status' in response_json else 'Unknown')
  print('=' * 20)
  
  
  code = {
    'output': loads(response_json['output']) if 'output' in response_json else None,
    'runtime':{
      'execution_arn': response_json['executionArn'] if 'executionArn' in response_json else None,
      'durationInMilliseconds': response_json['billingDetails']['billedDurationInMilliseconds'] if 'billingDetails' in response_json else None,
    },
    'error': {
      'type': response_json['error'] if 'error' in response_json else 'Succeeded',
      'cause': response_json['cause'] if 'cause' in response_json else 'Succeeded'
    } 
  }
  
  colorful = highlight(dumps(code, indent=2), lexer=JsonLexer(),formatter=formatters.TerminalFormatter())
  print(colorful)

@click.group("cli")
@click.pass_context
def cli(ctx):#, region:str, stack:str):
  '''
  Rekognition Identity Validation (RIV) Tester.
  '''
  ctx.obj = {}

@cli.command("register")
@click.option("-r", "--region", help="Amazon region hosting RIV", required=True)
@click.option("-z", "--stack", help="RIV Stack Name", required=True)
@click.option("-u", "--userid", help="Username to register")
@click.option("-p", "--picture", help="File location for the user's picture")
@click.pass_context
def register_user(ctx:click.Context, region:str, stack:str, userid:str, picture:PathLike):
  '''
  Registers a new user with a given user_id and picture (password).
  '''

  # Find the registration endpoint...
  register_url = get_userportal_address(region,stack,'register')
  payload = create_payload(image_path=picture, user_id=userid)
  
  try:
    response = requests.post(url=register_url,json=payload)
    print_response(response)
  except Exception as error:
    print_response(str(error))
    exit(1)

@cli.command("register-idcard")
@click.option("-r", "--region", help="Amazon region hosting RIV", required=True)
@click.option("-z", "--stack", help="RIV Stack Name", required=True)
@click.option("-u", "--userid", help="Username to register", required=True)
@click.option("-p", "--picture", help="File location for the user's picture",required=True)
@click.option("-c", "--idcard", help="File location for the user's idcard", required=True)
@click.pass_context
def register_idcard(ctx:click.Context, region:str, stack:str, userid:str, picture:PathLike, idcard:PathLike, verbose:bool=False):
  '''
  Registers a new user with a given user_id and picture (password).
  '''

  # Find the registration endpoint...
  register_url = get_userportal_address(region,stack,'register')
  payload = create_payload(image_path=picture, user_id=userid, idcard=idcard)
  
  try:
    response = requests.post(url=register_url,json=payload)
    print_response(response)
  except Exception as error:
    print_response(str(error))
    exit(1)

@cli.command("update")
@click.option("-r", "--region", help="Amazon region hosting RIV", required=True)
@click.option("-z", "--stack", help="RIV Stack Name", required=True)
@click.option("-u", "--userid", help="Username to register", required=True)
@click.option("-p", "--picture", help="File location for the user's picture",required=True)
@click.pass_context
def update_user(ctx:click.Context, region:str, stack:str, userid:str, picture:PathLike):
  '''
  Updates an existing user_id with a new picture and properties.
  '''
  update_url = get_userportal_address(region,stack,'update')
  payload = create_payload(image_path=picture, user_id=userid)
  
  try:
    response = requests.post(url=update_url,json=payload)
    print_response(response)
  except Exception as error:
    print(str(error))
    exit(1)

@cli.command("auth")
@click.option("-r", "--region", help="Amazon region hosting RIV", required=True)
@click.option("-z", "--stack", help="RIV Stack Name", required=True)
@click.option("-u", "--userid", help="Username to register", required=True)
@click.option("-p", "--picture", help="File location for the user's picture",required=True)
@click.pass_context
def auth_user(ctx:click.Context, region:str, stack:str, userid:str, picture:PathLike):
  '''
  Attempt an authentication with for a given user_id and picture (password).
  '''
  auth_url = get_userportal_address(region,stack,'auth')
  payload = create_payload(image_path=picture, user_id=userid)
  
  try:
    response = requests.post(url=auth_url,json=payload)
    print_response(response)
  except Exception as error:
    print(str(error))
    exit(1)

@cli.command("encode")
@click.option("-u", "--userid", help="Username to register")
@click.option("-p", "--picture", help="File location for the user's picture")
@click.option('-o', '--output', help='Output Filename', default='-')
@click.pass_context
def encode_payload(ctx:click.Context, userid:str, picture:PathLike, output:PathLike='-'):
  '''
  Encodes a user_id and picture (password) for externally calling User Portal. 
  '''
  payload = create_payload(image_path=picture, user_id=userid)
  
  if output == '-':
    print(dumps(payload))
  else:
    with open(output,'w') as f:
      f.write(dumps(payload, indent=2))
  exit(0)

def main():
  cli(prog_name="riv-tester")
 
if __name__ == '__main__':
  main()