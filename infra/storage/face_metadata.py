import builtins
from infra.interfaces import IVpcRivStack
from constructs import Construct
import aws_cdk as core
from aws_cdk import (
  aws_dynamodb as ddb,
)

class RivStorageFaceMetadata(Construct):
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

  def __init__(self, scope: Construct, id: builtins.str, riv_stack:IVpcRivStack) -> None:
    super().__init__(scope, id)

    self.face_table = ddb.Table(self,'FaceTable',
      removal_policy= core.RemovalPolicy.DESTROY,
      #table_name='{}-FaceTable'.format(riv_stack.riv_stack_name),
      partition_key= ddb.Attribute(
        name='PartitionKey',
        type=ddb.AttributeType.STRING),
      sort_key=ddb.Attribute(
        name='SortKey',
        type=ddb.AttributeType.STRING),
      billing_mode= ddb.BillingMode.PAY_PER_REQUEST,
      point_in_time_recovery=True)
