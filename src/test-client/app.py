import click
import http
import boto3
import requests
import names
from json import dumps, loads
from io import BytesIO
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
  response = ssm_client.get_parameter(Name='/riv/{}/userportal/url'.format(riv_stack_name))
  userportal_url:str = response['Parameter']['Value']
  
  if not userportal_url.endswith('/'):
    userportal_url = userportal_url + '/'

  return userportal_url + endpoint.lstrip('/')

def create_payload(image_path:PathLike=None, user_id:str=None, properties:Mapping[str,str]=None)->dict:
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

  if image_path is not None:
    with open(image_path,'rb') as f:
      photo_contents = f.read()
      return {
          'UserId': user_id,
          'Image': str(b64encode(photo_contents),'utf-8'),
          'Properties': properties
      }
  else:
    # response = requests.get('https://thispersondoesnotexist.com/image', stream=True)
    # buffer = BytesIO()
    # response.raw.decode_content = True
    # for chunk in response:
    #   buffer.write(chunk)
    
    # return {
    #     'UserId': user_id,
    #     'Image': str(b64encode(buffer.getvalue()),'utf-8'),
    #     'Properties': properties
    #   }
    raise ValueError("No Image specified.")

def print_response(response:requests.models.Response)->None:
  '''
  Write the friendly output for developers
  '''
  print('=' * 20)
  print('[%d] : %s' % (response.status_code, http.HTTPStatus(response.status_code).name))
  print('=' * 20)
  
  json = dumps(loads(response.content), indent=2)
  colorful = highlight(json, lexer=JsonLexer(),formatter=formatters.TerminalFormatter())
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
@click.option("-z", "--stack", help="RIV Zone Name", required=True)
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

@cli.command("update")
@click.option("-r", "--region", help="Amazon region hosting RIV", required=True)
@click.option("-z", "--stack", help="RIV Zone Name", required=True)
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
@click.option("-z", "--stack", help="RIV Zone Name", required=True)
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