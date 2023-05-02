import builtins
from infra.interfaces import IRivStack
from constructs import Construct
from os import path
from aws_cdk import (
    aws_iam as iam,
    aws_cognito as cognito
)


root_directory = path.dirname(__file__)
bin_directory = path.join(root_directory, "bin")


class RivCognitoForLivenes(Construct):
    '''
    Represents the root construct to create Amplify APP
    '''

    # def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack) -> None:
    def __init__(self, scope: Construct, id: builtins.str, riv_stack: IRivStack) -> None:
        super().__init__(scope, id)

        self.cognito = cognito.UserPool(
            self, "RIV-Cognito-User-Pool", user_pool_name=riv_stack.stack_name)
        # self.cognito.add_client("RIV-Cogito-app", supported_identity_providers=[
        #                         cognito.UserPoolClientIdentityProvider.COGNITO])

        self.client = cognito.UserPoolClient(
            self, "RIV-Cognito-Client", user_pool=self.cognito, user_pool_client_name=riv_stack.stack_name)

        self.idp = cognito.CfnIdentityPool(self, "RIV-IdentityPool", identity_pool_name=riv_stack.stack_name, allow_unauthenticated_identities=True, cognito_identity_providers=[cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
            client_id=self.client.user_pool_client_id, provider_name=self.cognito.user_pool_provider_name, server_side_token_check=None)])

        self.unAuthrole = iam.Role(self, 'RIVIdentityPoolUnAuthRole',
                                   assumed_by=iam.FederatedPrincipal('cognito-identity.amazonaws.com', conditions=({
                                       "StringEquals": {"cognito-identity.amazonaws.com:aud": self.idp.ref},
                                       "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "unauthenticated"}
                                   }), assume_role_action='sts:AssumeRoleWithWebIdentity'),
                                   description='role for amplify riv-prod app',

                                   managed_policies=[
                                       iam.ManagedPolicy.from_aws_managed_policy_name(
                                           managed_policy_name='AmazonRekognitionFullAccess')
                                   ])

        self.idpAttachment = cognito.CfnIdentityPoolRoleAttachment(
            self, 'RIV-IdentityPool-Role-Attachment', identity_pool_id=self.idp.ref, roles={"unauthenticated": self.unAuthrole.role_arn})
