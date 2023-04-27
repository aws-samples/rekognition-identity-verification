#!/usr/bin/env python3
from infra.configsettings import ConfigManager
from infra.services.networking.vpc import VpcNetworkingConstruct
from infra.services.core.backup import BackupStrategyConstruct
from typing import List

from infra.services.rekognition.topology import RivRekognitionSetupConstruct
from infra.storage.topology import RivSharedDataStores
from infra.userportal.topology import RivUserPortal
from infra.interfaces import IVpcRivStack, IVpcNetworkingConstruct
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
)

config = ConfigManager()

class VpcRivStack(IVpcRivStack):
  '''
  Represents an empty deployment enviroment with VPC and default services.
  '''
  def __init__(self:IVpcRivStack, scope:Construct, id:str, **kwargs)->None:
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

    if config.use_automated_backup:
      '''
      Create default backup policy for all resources 
      '''
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
    default_subnet_type = ec2.SubnetType.PRIVATE_WITH_EGRESS
    if config.use_isolated_subnets:
      default_subnet_type = ec2.SubnetType.PRIVATE_ISOLATED

    return [      
      # 16k addresses x 2 AZ
      ec2.SubnetConfiguration(name='Default', subnet_type=default_subnet_type, cidr_mask=18),
      
      # 8k addresses x 2 AZ
      ec2.SubnetConfiguration(name='Public', subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=19),
      
      # 8k addresses x 2 AZ
      ec2.SubnetConfiguration(name='Reserved', subnet_type=ec2.SubnetType.PRIVATE_ISOLATED, cidr_mask=19),
    ]

  @property
  def vpc(self)->ec2.IVpc:
    return self.networking.vpc    

class DefaultRivStack(VpcRivStack):
  '''
  Represents the simple deployment environment for RIV.
  '''
  def __init__(self, scope:Construct, id:str, riv_stack_name:str, **kwargs)->None:
    self.__zone_name = riv_stack_name
    super().__init__(scope, id, **kwargs)
    
    assert self.riv_stack_name is not None
    
    # Add Shared Services...
    sharedStorage = RivSharedDataStores(self,'SharedStorage',riv_stack=self)

    # Create the User Portal
    userportal = RivUserPortal(self,'UserPortal', riv_stack=self, sharedStorage=sharedStorage)

    # Setup Rekognition
    RivRekognitionSetupConstruct(self,'RekognitionSetup', riv_stack=self)

    #Setup FE
    if config.include_front_end:
      from infra.frontend.topology import RivFrontEnd
      from infra.frontend.cognito.topology import RivCognitoForLivenes
      from infra.frontend.topology import TriggerRivFrontEndBuild
      from infra.frontend.topology import RivFrontEndBuildStatus

      # setup Cognito for Liveness

      cognito = RivCognitoForLivenes(self,"RIVCognito",riv_stack=self )

      feapp = RivFrontEnd(self,"RIVWebAPP",riv_stack=self, apigateway=userportal.api_gateway , cognito= cognito)

      triggerfeapp = TriggerRivFrontEndBuild(self,"RIVWebAPPTrigger",riv_stack=self,amplifyApp=feapp)
      # feapp = RivFrontEnd(self,"RIVWebAPP",riv_stack=self)
      triggerfeapp.node.add_dependency(feapp)
      feappstatus = RivFrontEndBuildStatus(self,"RIVWebAPPStatus",riv_stack=self, amplifyApp=feapp , buildTrigger=triggerfeapp)
      feappstatus.node.add_dependency(triggerfeapp)

    
    if config.include_bulk_loader:
      # Create the bulk loader
      from infra.bulkloader.topology import RivBulkLoader
      bulk_loader = RivBulkLoader(self,'BulkLoader', riv_stack=self, sharedStorage=sharedStorage)

      # Declare any explicit dependencies
      bulk_loader.node.add_dependency(userportal)

  @property
  def cidr_block(self)->str:
    return '10.0.0.0/16'

  @property
  def riv_stack_name(self)->str:
    return self.__zone_name
