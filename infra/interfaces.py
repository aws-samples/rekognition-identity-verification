from typing import List, Mapping
from aws_cdk.core import Construct, Tags, Stack
from aws_cdk import (
    core,
    aws_ec2 as ec2,
)

class IVpcEndpointsForAWSServices(core.Construct):
  '''
  Represents an interface for creating VPC-endpoints.
  '''
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.__interfaces = {}
    self.__gateways = {}

  @property
  def interfaces(self)->Mapping[str,ec2.IInterfaceVpcEndpoint]:
    '''
    Gets a mapping of defined service to interface endpoint.
    '''
    return self.__interfaces

  @property
  def gateways(self)->Mapping[str,ec2.IGatewayVpcEndpoint]:
    '''
    Gets a mapping of defined service to interface endpoints.
    '''
    return self.__gateways

class ILandingZone(Stack):
  '''
  Represents an interface into a deployment environment.
  '''
  def __init__(self, scope:Construct, id:str, **kwargs)->None:
    super().__init__(scope, id, **kwargs)
 
  @property
  def zone_name(self)->str:
    '''
    Gets the name of the deployment environment.
    '''
    raise NotImplementedError()

class IVpcNetworkingConstruct(core.Construct):
  '''
  Represent a networking configuration for an ILandingZone.
  '''
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

  @property
  def vpc(self)->ec2.IVpc:
    '''
    Gets the VPC associated with this environment.
    '''
    raise NotImplementedError()

  @property
  def endpoints(self)->IVpcEndpointsForAWSServices:
    '''
    Gets the VPC-endpoints for this environment.
    '''
    raise NotImplementedError()

class IVpcLandingZone(ILandingZone):
  '''
  Represents an interface to a deployment environment with Vpc.
  '''
  def __init__(self, scope:Construct, id:str, **kwargs)->None:
    super().__init__(scope, id, **kwargs)

  @property
  def cidr_block(self)->str:
    '''
    Gets the environments network block (e.g., 10.0.0.0/16).
    '''
    raise NotImplementedError()
  
  @property
  def subnet_configuration(self)->List[ec2.SubnetConfiguration]:
    '''
    Gets the VPCs subnet topology.
    '''
    raise NotImplementedError()

  @property
  def vpc(self)->ec2.IVpc:
    '''
    Gets the VPC associated with this landing zone.
    '''
    raise NotImplementedError()

  @property
  def networking(self)->IVpcNetworkingConstruct:
    '''
    Gets the network configuration for this environment.
    '''
    raise NotImplementedError()

  @property
  def security_group(self)->ec2.SecurityGroup:
    '''
    Gets the default security group for this environment.
    '''
    raise NotImplementedError()

  @property
  def vpc_endpoints(self)->IVpcEndpointsForAWSServices:
    raise NotImplementedError()


class LandingZone(ILandingZone):
  '''
  Represents a deployable environment (aka CloudFormation Stack).
  '''
  def __init__(self, scope:Construct, id:str, **kwargs)->None:
    super().__init__(scope, id, **kwargs)
    Tags.of(self).add('landing_zone',self.zone_name)

  @property
  def zone_name(self)->str:
    '''
    Gets the name of this environment.
    '''
    raise NotImplementedError()

