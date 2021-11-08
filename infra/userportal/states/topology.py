import builtins
from infra.userportal.states.interfaces import IRivUserPortalStateMachines
from infra.userportal.functions.topology import RivUserPortalFunctionSet
from infra.userportal.states.register_user import RegisterStateMachine
from infra.userportal.states.register_idcard import RegisterIdCardStateMachine
from infra.userportal.states.update import UpdateStateMachine
from infra.userportal.states.auth import AuthStateMachine
from infra.interfaces import IVpcRivStack
from aws_cdk import (
  core,
  aws_stepfunctions as sf,
)

class RivUserPortalStateMachines(IRivUserPortalStateMachines):
  '''
  Represents a Construct containing all UserPortal state machines.
  '''
  def __init__(self, scope: core.Construct, id: builtins.str, landing_zone:IVpcRivStack,functions:RivUserPortalFunctionSet, state_machine_type:sf.StateMachineType) -> None:
    '''
    Initializes a new instance of the RivUserPortalStateMachines Construct.
    '''
    super().__init__(scope, id)
    
    '''
    Create the state machines for each flow
    '''
    self.register_new_user = RegisterStateMachine(self,'Register', 
      landing_zone=landing_zone,
      functions=functions,
      state_machine_type=state_machine_type)

    self.register_with_idcard = RegisterIdCardStateMachine(self,'Register-IdCard',
      landing_zone=landing_zone,
      functions=functions,
      state_machine_type=state_machine_type)

    self.update_existing_user = UpdateStateMachine(self,'Update',
      landing_zone=landing_zone,
      functions=functions,
      state_machine_type=state_machine_type)

    self.auth_existing_user = AuthStateMachine(self,'Auth',
      landing_zone=landing_zone,
      functions=functions,
      state_machine_type=state_machine_type)
