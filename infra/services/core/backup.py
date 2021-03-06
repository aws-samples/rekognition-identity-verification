from infra.interfaces import IRivStack
import aws_cdk as core
from constructs import Construct
from aws_cdk import (
  aws_backup as backup,
  aws_iam as iam,
  aws_kms as kms,
  aws_sns as sns,
)

class BackupStrategyConstruct(Construct):
  def __init__(self, scope:Construct, id:str, riv_stack:IRivStack, **kwargs):
    '''
    Landing Zone Backup Policy
    '''
    super().__init__(scope,id, **kwargs)

    region = core.Stack.of(self).region

    self.encryption_key = kms.Key(self,'EncryptionKey',
      description='Encryption Key for BackupStrategy')

    self.topic = sns.Topic(self,'Topic')
    self.role = iam.Role(self,'Role',
      description='Account Backup Role',
      assumed_by= iam.ServicePrincipal(service='backup'))

    self.vault = backup.BackupVault(self,'Vault',
      encryption_key=self.encryption_key,
      notification_topic= self.topic,
      removal_policy= core.RemovalPolicy.DESTROY,
      #backup_vault_name='{}-Backup-Vault'.format(riv_stack.riv_stack_name),
      access_policy= iam.PolicyDocument(
        statements=[
          iam.PolicyStatement(
            effect= iam.Effect.ALLOW,
            resources=["*"],
            actions=['backup:CopyIntoBackupVault'],
            principals= [
              iam.ArnPrincipal(arn = self.role.role_arn) 
            ])
        ]))

    self.default_plan = backup.BackupPlan(self,'DefaultPlan',
      backup_vault= self.vault,
      backup_plan_name='Default Plan {} in {}'.format(riv_stack.riv_stack_name, region),
      backup_plan_rules=[
        backup.BackupPlanRule.daily(),
        backup.BackupPlanRule.weekly(),
      ])

    self.default_plan.add_selection('SelectionPolicy',
      allow_restores=True,
      role=self.role,
      resources=[
        backup.BackupResource.from_tag("riv_stack", riv_stack.riv_stack_name),
      ])
