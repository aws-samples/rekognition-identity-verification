from typing import List, Mapping

from infra.interfaces import IVpcRivStack
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
)

class JumpBoxConstruct(core.Construct):
  @property
  def landing_zone(self)->IVpcRivStack:
    return self.__landing_zone

  def __init__(self, scope:core.Construct, id:str, landing_zone:IVpcRivStack, **kwargs) -> None:
    '''
    Configure emphemeral jumpbox for testing
    '''
    super().__init__(scope,id, **kwargs)
    self.__landing_zone = landing_zone

    # Only required for debugging the jumpbox
    #key_pair_name = 'nbachmei.personal.'+core.Stack.of(self).region

    role = iam.Role(self,'Role',
      assumed_by=iam.ServicePrincipal(
        service='ec2',
        region=core.Stack.of(self).region),
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
        iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMDirectoryServiceAccess'),
      ])

    self.instance = ec2.Instance(self,'Instance',
      role= role,
      vpc= landing_zone.vpc,
      #key_name= key_pair_name,
      instance_type=ec2.InstanceType.of(
        instance_class= ec2.InstanceClass.BURSTABLE3,
        instance_size=ec2.InstanceSize.SMALL),
      allow_all_outbound=True,
      user_data_causes_replacement=True,
      security_group= landing_zone.security_group,
      vpc_subnets= ec2.SubnetSelection(subnet_group_name='Default'),
      machine_image= self.machine_image)

  @property
  def machine_image(self)->ec2.IMachineImage:
    return ec2.MachineImage.generic_windows(ami_map={
      'us-east-1': 'ami-0f93c815788872c5d',
      'us-east-2': 'ami-0b697c4ae566cad55',
      'eu-west-1': 'ami-03b9a7c8f0fc1808e',
      'us-west-2': 'ami-0b7ebdd52b84c244d',
    })
