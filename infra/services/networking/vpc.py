#!/usr/bin/env python3
from infra.services.networking.vpce import VpcEndpointsForAWSServices
from typing import List
from constructs import Construct
from aws_cdk import (
  aws_ec2 as ec2,
)

class VpcNetworkingConstruct(Construct):
  '''
  Configure the networking layer
  '''
  def __init__(self, scope: Construct, id: str,cidr:str,subnet_configuration:List[ec2.SubnetConfiguration], **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    # Determine if we need NAT Gateways...
    has_private_networks = len([x for x in subnet_configuration if x.subnet_type == ec2.SubnetType.PRIVATE_WITH_NAT])
    nat_gateways=0
    if has_private_networks > 0:
      nat_gateways = 1

    self.vpc = ec2.Vpc(self,'Network',
      cidr=cidr,
      enable_dns_hostnames=True,
      enable_dns_support=True,
      max_azs= 2,
      nat_gateways=nat_gateways,
      subnet_configuration=subnet_configuration)

    self.endpoints = VpcEndpointsForAWSServices(self,'Endpoints',vpc=self.vpc)
