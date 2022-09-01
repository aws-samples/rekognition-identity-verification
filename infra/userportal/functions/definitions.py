from typing import Mapping
from infra.default_lambda import RivDefaultFunction
from infra.interfaces import IVpcRivStack
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
  aws_iam as iam,
)

class RivUserPortalFunction(RivDefaultFunction):
  '''
  Represents the base template for a UserPortal Lambda function.
  ''' 
  @property
  def component_name(self)->str:
    return self.__class__.__name__

  @property
  def function_name(self) -> str:
    return '{}-UserPortal-{}'.format(
        self.riv_stack.riv_stack_name,
        self.component_name)

  @property
  def function_timeout(self)->core.Duration:
    return core.Duration.seconds(30)
  
  def __init__(self, scope: Construct, id: str, riv_stack:IVpcRivStack,subnet_group_name:str='Default',env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=env, **kwargs)

    '''
    Attach any shared Amazon IAM policies here.
    '''
    self.function.role.add_managed_policy(
      policy=iam.ManagedPolicy.from_aws_managed_policy_name('AmazonRekognitionFullAccess'))

    # Grant access to shared SSM Parameters here.
    self.function.role.add_to_policy(statement=iam.PolicyStatement(
      effect= iam.Effect.ALLOW,
      actions=['ssm:GetParameter*'],
      resources=['arn:aws:ssm:{}:{}:parameter/riv/{}/rekognition/*'.format(
        core.Stack.of(self).region, core.Aws.ACCOUNT_ID, riv_stack.riv_stack_name)]
    ))


class RivUserPortalCompareFaces(RivUserPortalFunction):
  def __init__(self, scope: Construct, id:str, riv_stack:IVpcRivStack,subnet_group_name:str='Default',env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=env)

  @property
  def source_directory(self)->str:
    return 'src/rekognition/compare-faces'

  @property
  def component_name(self)->str:
    return 'CompareFaces'

class RivUserPortalDetectFaces(RivUserPortalFunction):
  def __init__(self, scope: Construct, id:str, riv_stack:IVpcRivStack,subnet_group_name:str='Default', env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=env)

  @property
  def source_directory(self)->str:
    return 'src/rekognition/detect-faces'

  @property
  def component_name(self)->str:
    return 'DetectFaces'

class RivUserPortalIndexFaces(RivUserPortalFunction):
  def __init__(self, scope: Construct, id:str, riv_stack:IVpcRivStack,subnet_group_name:str='Default', env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=env)

  @property
  def source_directory(self)->str:
    return 'src/rekognition/index-faces'

  @property
  def component_name(self)->str:
    return 'IndexFaces'

class RivUserPortalSearchFacesByImage(RivUserPortalFunction):
  def __init__(self, scope: Construct, id:str, riv_stack:IVpcRivStack,subnet_group_name:str='Default', env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=env)

  @property
  def source_directory(self)->str:
    return 'src/rekognition/search-faces'

  @property
  def component_name(self)->str:
    return 'SearchFaces'

class RivUserPortalExtractIdCard(RivUserPortalFunction):
  def __init__(self, scope: Construct, id:str, riv_stack:IVpcRivStack,subnet_group_name:str='Default', env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=env)

    self.function.role.add_managed_policy(
      iam.ManagedPolicy.from_aws_managed_policy_name('AmazonTextractFullAccess'))

  @property
  def source_directory(self)->str:
    return 'src/textract/extract-idcard'

  @property
  def component_name(self)->str:
    return 'Extract-IdCard'

class RivUserPortalCompareFacesWithIDCard(RivUserPortalFunction):
  def __init__(self, scope: Construct, id:str, riv_stack:IVpcRivStack,subnet_group_name:str='Default', env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=env)

  @property
  def source_directory(self)->str:
    return 'src/rekognition/compare-face-with-idcard'

  @property
  def component_name(self)->str:
    return 'CompareFacesWithIDCard'

class RivUserPortalResetUser(RivUserPortalFunction):
  def __init__(self, scope: Construct, id:str, riv_stack:IVpcRivStack,subnet_group_name:str='Default',env:Mapping[str,str]={}, **kwargs) -> None:
    super().__init__(scope, id, riv_stack=riv_stack, subnet_group_name=subnet_group_name, env=env)

  @property
  def source_directory(self)->str:
    return 'src/rekognition/reset'

  @property
  def component_name(self)->str:
    return 'ResetUser'