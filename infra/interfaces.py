from typing import List, Mapping
from aws_cdk import Tags, Stack
from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
)

class IRivStack(Stack):
    '''
    Represents an interface into a deployment environment.
    '''

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    @property
    def riv_stack_name(self) -> str:
        '''
        Gets the name of the deployment environment.
        '''
        raise NotImplementedError()


class RivStack(IRivStack):
    '''
    Represents a deployable environment (aka CloudFormation Stack).
    '''

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        Tags.of(self).add('riv_stack', self.riv_stack_name)

    @property
    def riv_stack_name(self) -> str:
        '''
        Gets the name of this environment.
        '''
        raise NotImplementedError()
