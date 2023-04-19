#!/usr/bin/env python3
from infra.configsettings import ConfigManager
from typing import List

from infra.rekognition.topology import RivRekognitionSetupConstruct
from infra.storage.topology import RivSharedDataStores
from infra.userportal.topology import RivUserPortal
from infra.frontend.topology import RivFrontEnd
from infra.frontend.cognito.topology import RivCognitoForLivenes
from infra.frontend.topology import TriggerRivFrontEndBuild
from infra.frontend.topology import RivFrontEndBuildStatus
from infra.interfaces import IRivStack
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
)

config = ConfigManager()


class DefaultRivStack(IRivStack):
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

    # setup Cognito for Liveness

    cognito = RivCognitoForLivenes(self,"RIVCognito",riv_stack=self )

    #Setup FE
    feapp = RivFrontEnd(self,"RIVWebAPP",riv_stack=self, apigateway=userportal.api_gateway , cognito= cognito)

    triggerfeapp = TriggerRivFrontEndBuild(self,"RIVWebAPPTrigger",riv_stack=self,amplifyApp=feapp)
    # feapp = RivFrontEnd(self,"RIVWebAPP",riv_stack=self)
    triggerfeapp.node.add_dependency(feapp)
    feappstatus = RivFrontEndBuildStatus(self,"RIVWebAPPStatus",riv_stack=self, amplifyApp=feapp , buildTrigger=triggerfeapp)
    feappstatus.node.add_dependency(triggerfeapp)


  @property
  def riv_stack_name(self)->str:
    return self.__zone_name
