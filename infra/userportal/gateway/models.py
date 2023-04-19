import builtins
from json import dumps
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
  aws_apigateway as api,
)

class GatewayModels(Construct):
  '''
  Represents the UserPortal API Gateway service contracts.
  '''
  def __init__(self, scope: Construct, id: builtins.str, rest_api:api.IRestApi) -> None:
    '''
    Initializes the models for a given API Gateway.
    :param scope: - 
    :param id: -
    :param rest_api: The User Portal API Gateway Construct.
    '''
    super().__init__(scope, id)

    '''
    This online tool was helpful defining the json schema models.
      Note: It is an external resource and has no affiliation with Amazon.
      https://www.liquid-technologies.com/online-json-to-schema-converter
    '''
    self.register_user_request = api.Model(self,'RegisterUserRequest',
      rest_api=rest_api,
      model_name='RegisterUserRequest',
      description='Enroll a new user within the system.',
      content_type='application/json',
      schema= api.JsonSchema(
        type=api.JsonSchemaType.OBJECT,
        required=[
          "UserId",
          "Image",
          "Properties",
        ],
        properties={
          "UserId": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Primary identifier for the user.'),
          "Image": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='utf8(base64( image ))'),
          "Properties": api.JsonSchema(
            type= api.JsonSchemaType.OBJECT,
            description='An arbitrary property bag.')
        }))

    self.update_user_request = api.Model(self,'UpdateUserRequest',
      rest_api=rest_api,
      model_name='UpdateUserRequest',
      description='Update an existing users profile.',
      content_type='application/json',
      schema= api.JsonSchema(
        type=api.JsonSchemaType.OBJECT,
        required=[
          "UserId",
          "Image",
          "Properties",
        ],
        properties={
          "UserId": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Primary identifier for the user.'),
          "Image": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='utf8(base64( image ))'),
          "Properties": api.JsonSchema(
            type= api.JsonSchemaType.OBJECT,
            description='An arbitrary property bag.')
        }))

    self.register_idcard_request = api.Model(self,'RegisterIdCardRequest',
      rest_api=rest_api,
      model_name='RegisterWithIdCardRequest',
      description='Registers a new user with a valid id card.',
      content_type='application/json',
      schema= api.JsonSchema(
        type=api.JsonSchemaType.OBJECT,
        required=[
          "UserId",
          "Image",
          "IdCard",
          "Properties",
        ],
        properties={
          "UserId": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Primary identifier for the user.'),
          "Image": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='utf8(base64( image ))'),
          "IdCard": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='utf8(base64( image ))'),
          "Properties": api.JsonSchema(
            type= api.JsonSchemaType.OBJECT,
            description='An arbitrary property bag.')
        }))

    self.auth_input_model = api.Model(self,'AuthenticateRequest',
      rest_api=rest_api,
      model_name='AuthenticateUserRequest',
      description='Verifies the caller matches their onfile photo',
      content_type='application/json',
      schema= api.JsonSchema(
        type=api.JsonSchemaType.OBJECT,
        required=[
          "UserId",
          "Image",
        ],
        properties={
          "UserId": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Primary identifier for the user.'),
          "Image": api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='utf8(base64( image ))')
        }))

    self.register_response_model = api.Model(self,'RegisterUserResponse',
      rest_api=rest_api,
      model_name='RegisterUserResponse',
      description='Output from the Register operation.',
      schema= api.JsonSchema(
        type=api.JsonSchemaType.OBJECT,
        description='The response from a register user flow.',
        required=[
          'UserId',
          'ImageId',
          'Status'
        ],
        properties={
          'UserId': api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Primary identifier for the user.'),
          'ImageId': api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Internal identifier for the user.'),
          'Status': api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Outcome of the Register operation.'),
        }))

    self.update_respose_model = api.Model(self,'UpdateUserResponse',
      rest_api=rest_api,
      model_name='UpdateUserResponse',
      description='Output from the Update operation.',
      schema= api.JsonSchema(
        type=api.JsonSchemaType.OBJECT,
        description='The response from a update user flow.',
        required=[
          'UserId',
          'ImageId',
          'Status'
        ],
        properties={
          'UserId': api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Primary identifier for the user.'),
          'ImageId': api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Internal identifier for the user.'),
          'Status': api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Outcome of the Update operation.'),
        }))

    self.auth_response_model = api.Model(self,'AuthenticateUserResponse',
      rest_api=rest_api,
      model_name='AuthenticateUserResponse',
      description='Output from the Authentication operation.',
      schema= api.JsonSchema(
        type=api.JsonSchemaType.OBJECT,
        description='The response from a auth user flow.',
        required=[
          'UserId',
          'Status'
        ],
        properties={
          'UserId': api.JsonSchema(
            type=api.JsonSchemaType.STRING,
            description='Primary identifier for the user.'),
          'Status': api.JsonSchema(
            type=api.JsonSchemaType.BOOLEAN,
            description='Outcome of the Authenticate operation.'),
        }))
