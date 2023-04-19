import builtins
from os import environ
from infra.configsettings import ConfigManager
from infra.interfaces import IRivStack
from infra.rekognition.collections import RekognitionCollectionConstruct

from constructs import Construct
from aws_cdk import (
  aws_ssm as ssm,
)

config_mgr = ConfigManager()

class RivRekognitionSetupConstruct(Construct):
  def __init__(self, scope: Construct, id: builtins.str, riv_stack:IRivStack) -> None:
    super().__init__(scope, id)

    '''
    Configure the Collections...
    '''
    total_collections = config_mgr.total_collections

    for ix in range(int(total_collections)):
      RekognitionCollectionConstruct(self,'Collection_'+str(ix),
        collection_id = '%s-%s' % (riv_stack.stack_name, ix))

    '''
    Add parameters for lambdas
    '''
    ssm.StringParameter(self,'PartitionCountParameter',
      parameter_name='/riv/{}/rekognition/{}'.format(riv_stack.stack_name, 'partition-count'),
      string_value=str(total_collections),
      #data_type=ssm.ParameterType.STRING,
      #cltype = ssm.ParameterType.STRING,
      tier= ssm.ParameterTier.STANDARD,
      description='Generated from %s' % __file__)
