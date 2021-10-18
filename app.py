#!/usr/bin/env python3
from os import environ
from infra.configsettings import ConfigManager
from typing import List
from aws_cdk import core
from infra.interfaces  import ILandingZone
from infra.topologies import DefaultLandingZone

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

    landing_zone_name = environ.get('ZONE_NAME')
    if landing_zone_name is None:
      landing_zone_name = 'Simple'
    self.landing_zone = DefaultLandingZone(self,'RIV-%s' % landing_zone_name, zone_name=landing_zone_name, env=env)

  @property
  def zones(self)->List[ILandingZone]:
    return [ self.landing_zone ]

app = RIVApp()
assembly = app.synth()

