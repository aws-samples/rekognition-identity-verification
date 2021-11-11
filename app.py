#!/usr/bin/env python3
from os import environ
from infra.configsettings import ConfigManager
from typing import List
from aws_cdk import core
from infra.interfaces  import IRivStack
from infra.topologies import DefaultRivStack

config_mgr = ConfigManager()

def get_environment()->core.Environment:
  '''
  Determines which region and account to deploy into.
  '''
  return core.Environment(
    region=config_mgr.region_name,
    account=config_mgr.account)

class RIVApp(core.App):
  '''
  Represents the root CDK entity.
  '''
  def __init__(self, **kwargs) ->None:
    super().__init__(**kwargs)

    env = get_environment()

    riv_stack_name = environ.get('RIV_STACK_NAME')
    if riv_stack_name is None:
      riv_stack_name = 'Riv-Prod'
    self.riv_stack = DefaultRivStack(self,riv_stack_name, riv_stack_name=riv_stack_name, env=env)

  @property
  def zones(self)->List[IRivStack]:
    return [ self.riv_stack ]

app = RIVApp()
assembly = app.synth()

