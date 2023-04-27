import builtins
from infra.interfaces import IVpcRivStack
from infra.userportal.gateway.topology import RivUserPortalGateway
from infra.frontend.cognito.topology import RivCognitoForLivenes
from constructs import Construct
import aws_cdk as core
from constructs import Construct
from os import path
from aws_cdk import (
    CfnOutput,
    aws_iam as iam,
    aws_lambda as lambda_,
    custom_resources as cr,
    aws_codecommit as codecommit,
    aws_amplifyuibuilder as builder
    
)

import aws_cdk.aws_amplify_alpha as amplify2

import aws_cdk.aws_s3_assets as s3_assets

# import aws_amplify.cdk.exported_backend

root_directory = path.dirname(__file__)
bin_directory = path.join(root_directory, "bin")


class RivFrontEnd(Construct):
    '''
    Represents the root construct to create Amplify APP
    '''

    # def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack) -> None:
    def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack, apigateway: RivUserPortalGateway,cognito:RivCognitoForLivenes) -> None:
        super().__init__(scope, id)

        s3_asset = s3_assets.Asset(self, "RIV-Web-App-Code",
                                   path="./src/frontend"
                                   )
        self.appRrepo = codecommit.Repository(self, "RIV-Web-App-Repo",
                                                    repository_name='{}-Repo'.format(
                                                        riv_stack.riv_stack_name),
                                                    code=codecommit.Code.from_asset(
                                                        s3_asset)
                                              )

        role = iam.Role(self, 'Role',
                        assumed_by=iam.ServicePrincipal(service='amplify'),
                        description='role for amplify riv-prod app',
                        managed_policies=[
                            iam.ManagedPolicy.from_aws_managed_policy_name(
                                managed_policy_name='AWSCodeArtifactReadOnlyAccess')
                        ])
                   
        self.amplify = amplify2.App(self, "RIV-Web-App",
                                    app_name=riv_stack.stack_name,
                                    auto_branch_creation=amplify2.AutoBranchCreation(
                                        auto_build=True,
                                        patterns=["main/*", "prod/*"],
                                    ),
                                    role=role,
                                    custom_rules=[amplify2.CustomRule(
                                        source="</^((?!\.(css|gif|ico|jpg|js|png|txt|svg|woff|ttf)$).)*$/>",
                                        target="/index.html",
                                        status=amplify2.RedirectStatus.REWRITE
                                    )],
                                    source_code_provider=amplify2.CodeCommitSourceCodeProvider(
                                        repository=self.appRrepo)
                                    )
        self.amplify.add_environment(
            name="REACT_APP_ENV_API_URL", value=apigateway.rest_api_url())
        self.amplify.add_environment(
            name="REACT_APP_IDENTITYPOOL_ID", value=cognito.idp.ref)
        self.amplify.add_environment(
            name="REACT_APP_USERPOOL_ID", value=cognito.cognito.user_pool_id)
        self.amplify.add_environment(
            name="REACT_APP_WEBCLIENT_ID", value=cognito.client.user_pool_client_id)
        self.amplify.add_environment(
            name="REACT_APP_REGION", value=core.Stack.of(self).region)

        self.amplify.add_branch("main", auto_build=True, branch_name="main")

       

        # aws_amplify.cdk.exported_backend(self.amplify,'AmplifyExportedBackend',{
        #     path:'./backend'

        # })


class TriggerRivFrontEndBuild(Construct):
    '''
    Represents the root construct for Triggering FE Aapp
    '''

    # def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack) -> None:
    def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack, amplifyApp: RivFrontEnd) -> None:
        super().__init__(scope, id)
        self.triggerBuild = cr.AwsCustomResource(self, "RIV-Web-App-Trigger-Build", policy=cr.AwsCustomResourcePolicy.from_sdk_calls(resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
                                                 on_create=cr.AwsSdkCall(service="Amplify", action="startJob",
                                                                         physical_resource_id=cr.PhysicalResourceId.of(
                                                                             'app-build-trigger'),
                                                                         parameters={
                                                                             "appId": amplifyApp.amplify.app_id,
                                                                             "branchName": "main",
                                                                             "jobType": 'RELEASE',
                                                                             "jobReason": 'Auto Start build',
                                                                         }))


class RivFrontEndBuildStatus(Construct):
    '''
    Represents the root construct for FE APP build status
    '''

    # def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack) -> None:
    def __init__(self, scope: Construct, id: builtins.str, riv_stack: IVpcRivStack, amplifyApp: RivFrontEnd, buildTrigger: TriggerRivFrontEndBuild) -> None:
        super().__init__(scope, id)
        with open(f"./infra/frontend/amplifydeployment/index.py") as lambda_path:
            code = lambda_path.read()

        self.lambda_function = lambda_.Function(self, 'RIV-Web-App-Lambda',
                                                function_name='{}-webapp-deployment'.format(
                                                    riv_stack.riv_stack_name),
                                                code=lambda_.Code.from_inline(
                                                    code),
                                                timeout=core.Duration.minutes(
                                                    10),
                                                tracing=lambda_.Tracing.ACTIVE,
                                                runtime=lambda_.Runtime.PYTHON_3_9,
                                                handler='index.lambda_handler')

        self.lambda_function.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AWSCloudFormationFullAccess'))

        self.lambda_function.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess-Amplify'))

        input = "{\"app\":\""+riv_stack.stack_name+"\",\"branch\":\"main\"}"

        self.appStatus = cr.AwsCustomResource(self, id="RIV-Web-App-Deploy-Status",
                                              policy=cr.AwsCustomResourcePolicy.from_statements([
                                                       iam.PolicyStatement(
                                                           actions=[
                                                               "lambda:InvokeFunction"],
                                                           resources=[
                                                               self.lambda_function.function_arn]
                                                       )
                                              ]),
                                              on_create=cr.AwsSdkCall(service='Lambda', action='invoke',
                                                                      physical_resource_id=cr.PhysicalResourceId.of('{}-webapp-stack'.format(
                                                                          riv_stack.riv_stack_name)),
                                                                      parameters={
                                                                          'FunctionName': self.lambda_function.function_name,
                                                                          "InvocationType": "RequestResponse",
                                                                          "Payload": input
                                                                      }),

                                              on_update=cr.AwsSdkCall(service='Lambda', action='invoke',
                                                                      physical_resource_id=cr.PhysicalResourceId.of('{}-webapp-stack'.format(
                                                                          riv_stack.riv_stack_name)),
                                                                      parameters={
                                                                          'FunctionName': self.lambda_function.function_name,
                                                                          "InvocationType": "RequestResponse",
                                                                          "Payload": input
                                                                      })
                                              )
        CfnOutput(self, id="RIV-Web-App-URL",
                  value="https://main."+amplifyApp.amplify.app_id+".amplifyapp.com", export_name="RIV-Web-App-URL")
