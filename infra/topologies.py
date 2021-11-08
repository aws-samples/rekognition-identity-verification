#!/usr/bin/env python3
from infra.configsettings import ConfigManager
from infra.services.networking.vpc import VpcNetworkingConstruct
from infra.services.core.backup import BackupStrategyConstruct
from typing import List
from infra.bulkloader.topology import RivBulkLoader
from infra.storage.topology import RivSharedDataStores
from infra.userportal.topology import RivUserPortal
from infra.interfaces import IVpcRivStack, IVpcNetworkingConstruct
from aws_cdk import (
    core,
    aws_ec2 as ec2,
)

config = ConfigManager()

class VpcRivStack(IVpcRivStack):
  '''
  Represents an empty deployment enviroment with VPC and default services.
  '''
  def __init__(self:IVpcRivStack, scope:core.Construct, id:str, **kwargs)->None:
    super().__init__(scope, id, **kwargs)
    core.Tags.of(self).add('riv_stack',self.riv_stack_name)

    self.networking = VpcNetworkingConstruct(self,self.riv_stack_name,
      cidr=self.cidr_block,
      subnet_configuration=self.subnet_configuration)

    if config.use_isolated_subnets:
      '''
      Configure the base networking for the environment.
      **IMPORTANT** ISOLATED subnets cannot reach the public internet.
      This means that customers must whitelist any AWS services
        by creating VPC-endpoints to securely route the traffic.
      '''
      self.networking.endpoints.add_ssm_support()
      self.networking.endpoints.add_kms_support()
      self.networking.endpoints.add_rekognition_support()
      self.networking.endpoints.add_textract_support()

    # Create the default backup policy...
    self.backup_policy = BackupStrategyConstruct(self,'Backup',
      riv_stack=self)

    # Create default security group...
    self.security_group = ec2.SecurityGroup(self,'SecurityGroup',
      description='Default-SG for {} RIV stack'.format(self.riv_stack_name),
      vpc= self.vpc,
      allow_all_outbound=True)
    
    self.security_group.add_ingress_rule(
      peer= ec2.Peer.any_ipv4(),
      connection= ec2.Port.all_icmp(),
      description='Grant icmp from anywhere')

  @property
  def security_group(self) -> ec2.ISecurityGroup:
    return self.__security_group

  @security_group.setter
  def security_group(self,value:ec2.ISecurityGroup):
    self.__security_group = value

  @property
  def networking(self)->IVpcNetworkingConstruct:
    return self.__networking

  @networking.setter
  def networking(self,value) -> IVpcNetworkingConstruct:
    self.__networking = value

  @property
  def cidr_block(self)->str:
    raise NotImplementedError()  

  @property
  def subnet_configuration(self)->List[ec2.SubnetConfiguration]:
    '''
    Gets the Vpc RivStack's subnet configuration.
    '''
    default_subnet_type = ec2.SubnetType.PRIVATE
    if config.use_isolated_subnets:
      default_subnet_type = ec2.SubnetType.ISOLATED

    return [      
      # 16k addresses x 2 AZ
      ec2.SubnetConfiguration(name='Default', subnet_type=default_subnet_type, cidr_mask=18),
      
      # 8k addresses x 2 AZ
      ec2.SubnetConfiguration(name='Public', subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=19),
      
      # 8k addresses x 2 AZ
      ec2.SubnetConfiguration(name='Reserved', subnet_type=ec2.SubnetType.ISOLATED, cidr_mask=19),
    ]

  @property
  def vpc(self)->ec2.IVpc:
    return self.networking.vpc    

class DefaultRivStack(VpcRivStack):
  '''
  Represents the simple deployment environment for RIV.
  '''
  def __init__(self, scope:core.Construct, id:str, riv_stack_name:str, **kwargs)->None:
    self.__zone_name = riv_stack_name
    super().__init__(scope, id, **kwargs)
    
    assert self.riv_stack_name is not None
    
    # Add Shared Services...
    sharedStorage = RivSharedDataStores(self,'SharedStorage',riv_stack=self)

    # Create the User Portal
    userportal = RivUserPortal(self,'UserPortal', riv_stack=self, sharedStorage=sharedStorage)
    
    # Create the bulk loader
    bulk_loader = RivBulkLoader(self,'BulkLoader', riv_stack=self, sharedStorage=sharedStorage)

    # Declare any explicit dependencies
    bulk_loader.node.add_dependency(userportal)

  @property
  def cidr_block(self)->str:
    return '10.25.0.0/16'

  @property
  def riv_stack_name(self)->str:
    return self.__zone_name
