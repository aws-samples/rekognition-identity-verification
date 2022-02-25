import os
from json import loads

src_root_dir = os.path.join(os.path.dirname(__file__),'..')
default_config_file = os.path.join(src_root_dir,'config.json')

class LambdaCodeLocation:
  '''
  Represents the source location for Lambda function.
  '''
  def __init__(self, bucket_name:str, key:str, object_version:str) -> None:
    self.bucket_name:str = bucket_name
    self.key:str = key
    self.object_version:str = object_version

class ConfigManager:
  '''
  Represents a utility for interacting with the config.json file.
  '''
  def __init__(self, config_file:os.PathLike=None) -> None:
    if config_file is None:
      config_file = default_config_file

    if os.path.exists(config_file):
      with open(config_file,'r') as f:
        self.json = loads(f.read())
    else:
      self.json = {}

  @property
  def region_name(self)->str:
    if 'region' in self.json:
      return self.json['region']

    region = os.environ.get("CDK_DEFAULT_REGION")
    if not region is None:
      return region
    else:
      return cdk.Aws.REGION

  @property
  def account(self)->str:
    if 'account' in self.json:
      return self.json['account']

    account = os.environ.get('CDK_DEFAULT_ACCOUNT')
    if not account is None:
      return account
    else:
      return cdk.Aws.ACCOUNT_ID

  @property
  def use_isolated_subnets(self)->bool:
    if 'use_isolated_subnets' in self.json:
      return self.json['use_isolated_subnets']
    return False

  @property
  def use_automated_backup(self)->bool:
    if 'use_automated_backup' in self.json:
      return self.json['use_automated_backup']
    return False

  @property
  def total_collections(self)->int:
    if 'total_collections' in self.json:
      return int(self.json['total_collections'])
    
    # Support the same variable as one-click.sh
    total_collections = os.environ.get('TOTAL_COLLECTIONS')
    if total_collections is None:
      total_collections = 1
    
    return int(total_collections)

  @property
  def include_bulk_loader(self)->bool:
    if 'include_bulk_loader' in self.json:
      return self.json['include_bulk_loader']
    return False

  @property
  def use_custom_asset_bucket(self)->bool:
    if not 'use_custom_asset_bucket' in self.json:
      return False
    return self.json['use_custom_asset_bucket']

  @property
  def custom_asset_bucket_name(self)->str:
    assert 'custom_asset_bucket_name' in self.json,"missing expected config value $.custom_asset_bucket_name"
    return self.json['custom_asset_bucket_name']

  def get_lambda_code(self,component_name:str)->LambdaCodeLocation:
    assert component_name is not None, "missing component_name argument"
    assert component_name in self.json['custom_assets'], 'missing definition for $.custom_assets.%s' % component_name

    bucket_name:str = None
    if 'bucket' in self.json['custom_assets'][component_name]:
      bucket_name = self.json['custom_assets'][component_name]['bucket']
    else:
      bucket_name = self.custom_asset_bucket_name

    assert 'key' in self.json['custom_assets'][component_name], "missing $.custom_assets.%s.key" % component_name
    key:str = self.json['custom_assets'][component_name]['key']

    object_version = None
    if 'objectVersion' in self.json['custom_assets'][component_name]:
      object_version = self.json['custom_assets'][component_name]['objectVersion']

    return LambdaCodeLocation(
      bucket_name = bucket_name,
      key=key,
      object_version = object_version)
