import builtins
from infra.userportal.functions.topology import RivUserPortalFunctionSet
from infra.interfaces import  IRivStack
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
  aws_logs as logs,
  aws_stepfunctions as sf,
)

# Hard-limit due to API Gateway
max_runtime= core.Duration.seconds(30)

class RivStateMachineConstruct(Construct):
  '''
  Represents the base class for RivUserPortal StateMachines.
  '''
  @property
  def riv_stack(self)->IRivStack:
    '''
    Gets the destination RIV stack.
    '''
    return self.__landing_zone

  @property
  def functions(self)->RivUserPortalFunctionSet:
    '''
    Gets the backing Lambda functions for the state machines.
    '''
    return self.__functions

  @property
  def state_machine(self)->sf.IStateMachine:
    '''
    Gets the state machine that implements this construct.
    '''
    return self.__state_machine

  def __init__(self, scope: Construct, id: builtins.str, riv_stack:IRivStack,functions:RivUserPortalFunctionSet, state_machine_type:sf.StateMachineType) -> None:
    '''
    Initializes a new instance of the RivStateMachineConstruct.
    '''
    super().__init__(scope, id)
    self.__landing_zone = riv_stack
    self.__functions = functions
    self.__state_machine = None
    self.state_machine_type = state_machine_type

    self.log_group = logs.LogGroup(self,'LogGroup',
      removal_policy=core.RemovalPolicy.DESTROY)

  def set_state_machine(self, state_machine_name:str, definition:sf.IChainable)->None:
    '''
    Creates the state machine from definition with a given name.
    :param state_machine_name: The name of the state machine.
    :param definition: The state machine activity flow.
    '''
    assert state_machine_name is not None, "state_machine_name not specified"
    assert definition is not None, "definition not specified"
    assert self.__state_machine is None, "set_state_machine called multiple times."

    '''
    API Gateway integrates with Step Function Express.
    However, the solution also creates Step Function Standard workflows.
      Standard workflows are easier to debug and troubleshoot via the console.
      They serve no purpose other than improving developer experience.
    '''
    suffix = ''
    if self.state_machine_type == sf.StateMachineType.STANDARD:
      suffix = '_Debuggable'

    self.__state_machine = sf.StateMachine(self,'StateMachine',
      state_machine_name='{}{}'.format(state_machine_name, suffix),
      state_machine_type= self.state_machine_type,
      tracing_enabled=True,
      definition= definition,
      timeout= max_runtime,
      logs= sf.LogOptions(
        include_execution_data=True,
        level = sf.LogLevel.ALL,
        destination= self.log_group
      ))

class IRivUserPortalStateMachines(Construct):
  '''
  Represents an interface bundle for accessing the UserPortal StateMachines.
  '''
  def __init__(self, scope: Construct, id: builtins.str) -> None:
    '''
    Initializes a new instance of this base class.
    '''
    super().__init__(scope, id)

  @property
  def register_new_user(self) -> RivStateMachineConstruct:
    '''
    Gets the Register New User flow's state machine. 
    '''
    assert self.__register is not None, "Missing call to setter register_new_user"
    return self.__register

  @register_new_user.setter
  def register_new_user(self,value:RivStateMachineConstruct)->None:
    '''
    Sets the RivStateMachineConstruct that implements the Register New User flow.
    '''
    assert value is not None, "No value provided."
    self.__register = value

  @property
  def register_with_idcard(self) -> RivStateMachineConstruct:
    '''
    Gets the Register with Id Card flow's state machine. 
    '''
    assert self.__register_idcard is not None, "Missing call to setter register_with_idcard"
    return self.__register_idcard

  @register_with_idcard.setter
  def register_with_idcard(self,value:RivStateMachineConstruct)->None:
    '''
    Sets the RivStateMachineConstruct that implements the Register with Id Card flow.
    '''
    assert value is not None, "No value provided."
    self.__register_idcard = value

  @property
  def update_existing_user(self) -> RivStateMachineConstruct:
    '''
    Gets the Update Existing User flow's state machine. 
    '''
    assert self.__update is not None, "Missing call to setter update_existing_user"
    return self.__update

  @update_existing_user.setter
  def update_existing_user(self,value:RivStateMachineConstruct)->None:
    '''
    Sets the RivStateMachineConstruct that implements the Update Existing User flow.
    '''
    assert value is not None, "No value provided."
    self.__update = value

  @property
  def auth_existing_user(self) -> RivStateMachineConstruct:
    '''
    Gets the Authenticate Existing User flow's state machine. 
    '''
    assert self.__auth is not None, "Missing call to setter auth_existing_user"
    return self.__auth

  @auth_existing_user.setter
  def auth_existing_user(self,value:RivStateMachineConstruct)->None:
    '''
    Sets the RivStateMachineConstruct that implements the Authenticate Existing User flow.
    '''
    assert value is not None, "No value provided."
    self.__auth = value
