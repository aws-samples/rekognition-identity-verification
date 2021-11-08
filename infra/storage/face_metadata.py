import builtins
from infra.interfaces import IVpcRivStack
from aws_cdk import (
  core,
  aws_dynamodb as ddb,
)

class RivStorageFaceMetadata(core.Construct):
  '''
  Represents a central storage for Facial metadata.
  '''
  @property
  def face_table(self)->ddb.ITable:
    '''
    Gets the DynamoDB Face metadata table.
    '''
    return self.__face_table

  @face_table.setter
  def face_table(self,value:ddb.ITable)->None:
    self.__face_table = value

  def __init__(self, scope: core.Construct, id: builtins.str, landing_zone:IVpcRivStack) -> None:
    super().__init__(scope, id)

    self.face_table = ddb.Table(self,'FaceTable',
      removal_policy= core.RemovalPolicy.DESTROY,
      #table_name='Riv{}-FaceTable'.format(landing_zone.zone_name),
      partition_key= ddb.Attribute(
        name='PartitionKey',
        type=ddb.AttributeType.STRING),
      sort_key=ddb.Attribute(
        name='SortKey',
        type=ddb.AttributeType.STRING),
      billing_mode= ddb.BillingMode.PAY_PER_REQUEST,
      point_in_time_recovery=True)
