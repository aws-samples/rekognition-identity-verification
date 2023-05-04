from os import path
import subprocess
import os
from infra.configsettings import ConfigManager
from typing import Mapping
from infra.interfaces import IVpcRivStack
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_lambda as lambda_,
)

config_mgr = ConfigManager()
shared_deps_path = path.join(path.dirname(__file__),'../src/shared')

base_path = f"./src/shared"

output_dir = f"./cdk.out/shared"

class RivDefaultFunction(Construct):
  '''
  Represents the base template for a UserPortal Lambda function.
  ''' 
  @property
  def source_directory(self)->str:
    raise NotImplemented()

  @property
  def component_name(self)->str:
    return self.__class__.__name__

  @property
  def function_name(self)->str:
    raise NotImplementedError()

  @property
  def riv_stack(self)->IVpcRivStack:
    return self.__landing_zone

  @property
  def function_timeout(self)->core.Duration:
    return core.Duration.seconds(30)

  @property
  def function(self)->lambda_.IFunction:
    return self.__function

  @function.setter
  def function(self,value:lambda_.IFunction)->None:
    self.__function = value
  
  def __init__(self, scope: Construct, id: str, riv_stack:IVpcRivStack,subnet_group_name:str='Default',env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    self.__landing_zone = riv_stack

    role = iam.Role(self,'Role',
      assumed_by=iam.ServicePrincipal(service='lambda'),
      description='{} for the {} component.'.format(self.__class__.__name__, self.component_name),
      # role_name='{}@riv.{}.{}'.format(
      #   self.component_name,
      #   riv_stack.riv_stack_name,
      #   core.Stack.of(self).region),
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name(
          managed_policy_name='service-role/AWSLambdaVPCAccessExecutionRole'),
        iam.ManagedPolicy.from_aws_managed_policy_name(
          managed_policy_name='AWSXRayDaemonWriteAccess')
      ])

    '''
    Define the Amazon Lambda function.
    '''
    environment = dict(env)
    environment['REGION'] = core.Stack.of(self).region
    
    #self.function = lambda_.DockerImageFunction(self,'Function',
    self.function = lambda_.Function(self,'LambdaFunction', 
      code = lambda_.Code.from_asset(
        path= self.source_directory,
        exclude=['requirements.txt','examples/*','.vscode/*']),
      role= role,
      #function_name=self.function_name,
      description='Python container lambda function for '+self.component_name,
      timeout= self.function_timeout,
      handler='handler.function_main',
      runtime= lambda_.Runtime.PYTHON_3_8,
      tracing= lambda_.Tracing.ACTIVE,
      vpc= riv_stack.vpc,
      memory_size=512,
      allow_all_outbound=True,
      vpc_subnets=ec2.SubnetSelection(subnet_group_name=subnet_group_name),
      security_groups=[riv_stack.security_group],
      environment=environment
    )

    '''
    Include the shared requirements.txt 
    '''
    if not os.environ.get("SKIP_PIP"):
      if not os.path.isdir(output_dir): 
        subprocess.check_call(
        # Note: Pip will create the output dir if it does not exist
        f"pip3 install -r {base_path}/requirements.txt -t {output_dir}/python".split()
        )
    self.requirements_txt = lambda_.LayerVersion(self,'SharedDeps',
      code= lambda_.Code.from_asset(path=output_dir),
      compatible_runtimes=[self.function.runtime],
      description='Shared dependencies')

    self.function.add_layers(self.requirements_txt)
