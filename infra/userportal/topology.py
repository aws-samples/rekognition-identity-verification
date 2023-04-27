import builtins
from infra.configsettings import ConfigManager

from aws_cdk.aws_stepfunctions import StateMachineType
from infra.storage.topology import RivSharedDataStores
from infra.userportal.functions.topology import RivUserPortalFunctionSet
from infra.userportal.states.topology import RivUserPortalStateMachines
from infra.userportal.gateway.topology import RivUserPortalGateway
from json import dumps
from infra.interfaces import IVpcRivStack
from constructs import Construct

config = ConfigManager()
class RivUserPortal(Construct):
  def __init__(self, scope: Construct, id: builtins.str, riv_stack:IVpcRivStack, sharedStorage, subnet_group_name:str='Default') -> None:
    super().__init__(scope, id)
    
    if config.use_isolated_subnets:
      '''
      Declare any VPC endpoints required by this construct.
      '''
      riv_stack.networking.endpoints.add_lambda_support()
      riv_stack.networking.endpoints.add_apigateway_support()
      riv_stack.networking.endpoints.add_rekognition_support()

    '''
    Declare the function set that powers the backend
    '''
    self.functions = RivUserPortalFunctionSet(self,'Functions',
      riv_stack=riv_stack,
      subnet_group_name=subnet_group_name,
      sharedStorage=sharedStorage)

    '''
    Create an Amazon API Gateway and register Step Function Express integrations.
    '''
    self.api_gateway = RivUserPortalGateway(self,'Gateway', riv_stack=riv_stack)
    self.state_machines = RivUserPortalStateMachines(self,'States',
      riv_stack=riv_stack,
      functions=self.functions,
      state_machine_type= StateMachineType.EXPRESS)

    self.api_gateway.bind_state_machines(self.state_machines)

    self.api_gateway.bind_reset_user(self.functions)

    self.api_gateway.bind_start_liveness_session(self.functions)

    self.api_gateway.bind_liveness_session_result(self.functions)

    self.api_gateway.bind_check_userid(self.functions)

    self.api_gateway.bind_extract_id_card(self.functions)

    '''
    Create Standard Stepfunctions to simplify developer troubleshooting.
    '''
    self.debug_state_machines = RivUserPortalStateMachines(self,'DebugStates',
      riv_stack=riv_stack,
      functions=self.functions,
      state_machine_type= StateMachineType.STANDARD)
