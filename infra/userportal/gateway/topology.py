import builtins
from infra.userportal.states.interfaces import IRivUserPortalStateMachines, RivStateMachineConstruct
from infra.userportal.functions.topology import RivUserPortalFunctionSet
from infra.userportal.gateway.models import GatewayModels
from json import dumps
from infra.interfaces import IVpcRivStack
from constructs import Construct
from aws_cdk import (
  aws_iam as iam,
  aws_apigateway as api,
  aws_ssm as ssm,
)

def make_template(state_machine_arn:str)->str:
  templateString= '''
  #set($inputRoot = $input.Path('$')) {
    "stateMachineArn": "%s",
    "input": "{ \\"inputRequest\\": $util.escapeJavaScript( $input.json('$')) }"
  }
  '''
  templateString = templateString % state_machine_arn
  return templateString


class RivUserPortalGateway(Construct):
  '''
  Represents the root User Portal using API Gateway Construct.
  '''  
  @property
  def component_name(self)->str:
    return self.__class__.__name__

  def __init__(self, scope: Construct, id: builtins.str, riv_stack:IVpcRivStack) -> None:
    super().__init__(scope, id)
    
    # Define the gateway...
    self.rest_api = api.RestApi(self,'UserPortal',
      rest_api_name='{}-UserPortal'.format(riv_stack.riv_stack_name),
      description='Gateway for {}'.format(self.component_name))
    
    self.models = GatewayModels(self,'Models', rest_api= self.rest_api)
    # Specify the role to use with integrations...
    self.role = iam.Role(self,'Role',
      #role_name='{}@riv.{}.{}'.format(self.component_name, riv_stack.riv_stack_name, core.Stack.of(self).region),
      assumed_by=iam.ServicePrincipal(service='apigateway'),
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name='AWSStepFunctionsFullAccess')
      ])

    # Persist the endpoint for test automation...
    ssm.StringParameter(self,'EndpointAddress',
      parameter_name='/riv/{}/userportal/url'.format(riv_stack.riv_stack_name),
      string_value=self.rest_api.url)

  def rest_api_url(self):
        return self.rest_api.url
  
  def bind_state_machines(self, state_machines:IRivUserPortalStateMachines)->api.ProxyResource:
    '''
    Creates a service integration between a given path and state machine
    :param state_machines: the stepfunction express user flows.
    :type state_machines: IRivUserPortalStateMachines
    '''
    assert state_machines is not None, "no state_machine provided."

    self.__bind_state_machine('register', state_machines.register_new_user, self.models.register_user_request, self.models.register_response_model)
    self.__bind_state_machine('register-idcard', state_machines.register_with_idcard, self.models.register_idcard_request, self.models.register_response_model)
    self.__bind_state_machine('update', state_machines.update_existing_user, self.models.update_user_request, self.models.update_respose_model)
    self.__bind_state_machine('auth', state_machines.auth_existing_user, self.models.auth_input_model, self.models.auth_response_model)
    
  
  def bind_reset_user(self, functions:RivUserPortalFunctionSet)->api.ProxyResource:
    '''
    Configure the service integration
    :param resource_name:  The UserPortal's URL fragment.
    :param handler: The user flows implementing Step Function Express instance
    :param model_in: The request's data contract definition
    :param model_out: The response's data contract definition
    '''
    integration = api.LambdaIntegration(functions.reset_user.function,
    integration_responses=[
          api.IntegrationResponse(
            status_code='200',
            selection_pattern='200',
            response_parameters={
                "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                "method.response.header.Access-Control-Allow-Methods": "'*'",
                "method.response.header.Access-Control-Allow-Origin": "'*'"
    }),
          api.IntegrationResponse(
            status_code='500',
            selection_pattern='500',
            response_parameters={
                "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                "method.response.header.Access-Control-Allow-Methods": "'*'",
                "method.response.header.Access-Control-Allow-Origin": "'*'"
    })
        ],
        passthrough_behavior= api.PassthroughBehavior.NEVER)
        
    '''
    Configure the /resource-name...
    '''    
    resource = self.rest_api.root.add_resource(
      path_part='reset-user',
      default_cors_preflight_options= api.CorsOptions(
        allow_origins=api.Cors.ALL_ORIGINS,
        allow_headers=['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
        allow_credentials=True,
        allow_methods=['OPTIONS', 'GET'],
      ),
      default_method_options=api.MethodOptions(
        request_models= {
          "application/json": self.models.auth_input_model
        }))

    resource.add_method(http_method='GET',
      integration=integration,
      method_responses=[
        api.MethodResponse(status_code='200', response_models={
          'application/json': self.models.auth_response_model,
        },response_parameters={
            "method.response.header.Access-Control-Allow-Headers": True,
            "method.response.header.Access-Control-Allow-Methods": True,
            "method.response.header.Access-Control-Allow-Origin": True
    }),
        api.MethodResponse(status_code='500', response_models={
          'application/json': api.Model.ERROR_MODEL
        },response_parameters={
            "method.response.header.Access-Control-Allow-Headers": True,
            "method.response.header.Access-Control-Allow-Methods": True,
            "method.response.header.Access-Control-Allow-Origin": True
    })
      ])
    

  def __bind_state_machine(self,resource_name:str,handler:RivStateMachineConstruct,model_in:api.Model,model_out:api.Model)->None:
    '''
    Configure the service integration
    :param resource_name:  The UserPortal's URL fragment.
    :param handler: The user flows implementing Step Function Express instance
    :param model_in: The request's data contract definition
    :param model_out: The response's data contract definition
    '''
    integration = api.AwsIntegration(
      service='states',
      action='StartSyncExecution',
      integration_http_method='POST',
      options= api.IntegrationOptions(
        credentials_role= self.role,
        request_templates={
          "application/json": make_template(handler.state_machine.state_machine_arn)
        },
        # TODO: These default templates do not match the GatewayModel definition.
        # Ideally, these would use Velocity Templating to return the expected "OperationResponse" definition
        integration_responses=[
          api.IntegrationResponse(
            status_code='200',
            selection_pattern='200',
            response_templates={                
              'application/json':'''$input.json('$')'''
            },
            response_parameters={
                "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                "method.response.header.Access-Control-Allow-Methods": "'*'",
                "method.response.header.Access-Control-Allow-Origin": "'*'"
    }),
          api.IntegrationResponse(
            status_code='500',
            selection_pattern='500',
            response_templates={
              'application/json':'''$input.json('$')'''
            },
            response_parameters={
                "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                "method.response.header.Access-Control-Allow-Methods": "'*'",
                "method.response.header.Access-Control-Allow-Origin": "'*'"
    })
        ],
        passthrough_behavior= api.PassthroughBehavior.NEVER))

    '''
    Configure the /resource-name...
    '''    
    resource = self.rest_api.root.add_resource(
      path_part=resource_name,
      default_cors_preflight_options= api.CorsOptions(
        allow_origins=api.Cors.ALL_ORIGINS,
        allow_headers=['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
        allow_credentials=True,
        allow_methods=['OPTIONS', 'POST'],
      ),
      default_method_options=api.MethodOptions(
        request_models= {
          "application/json": model_in
        }))

    resource.add_method(http_method='POST',
      integration=integration,
      method_responses=[
        api.MethodResponse(status_code='200', response_models={
          'application/json': model_out,
        },response_parameters={
            "method.response.header.Access-Control-Allow-Headers": True,
            "method.response.header.Access-Control-Allow-Methods": True,
            "method.response.header.Access-Control-Allow-Origin": True
    }),
        api.MethodResponse(status_code='500', response_models={
          'application/json': api.Model.ERROR_MODEL
        },response_parameters={
            "method.response.header.Access-Control-Allow-Headers": True,
            "method.response.header.Access-Control-Allow-Methods": True,
            "method.response.header.Access-Control-Allow-Origin": True
    })
      ])
