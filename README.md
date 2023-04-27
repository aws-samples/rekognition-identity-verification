# Amazon Rekognition Identity Verification (RIV)

A solution to assist with identity verification using Amazon Rekognition.

## Prerequisites

There are two personas that will need to deploy the Rekognition Identity Verification sample.  First, is operational teams that want to use the official artifacts.  These users can leverage the Launch Template button to deploy the topology into their account.  This audience does not need to worry about additional prerequisite or deployment steps.  In contrast, the second persona is development teams that must customize the solution.  These users can either use the Docker-based build terminal or locally install on their workstation.

The Docker-based build terminal provides a consistent experience across Microsoft Windows, Apple OSX, and Linux environments.  There are [two scripts](docker-deploy), available named *ship-it* and *debug*.  Invoking *ship-it* will create the Docker-based deployment process, push the local code into AWS, and then exit. Alternatively, *debug* creates a long running terminal session that’s suited for hands-on-keyboard situations.

```sh
# Setup the AWS CLI
aws configure                                                                     
                                                                                  
# Launch the Windows-specific script                                              
c:\git\rekoginition-identity-verification\docker-deploy\debug.bat                 
                                                                                  
# Launch the Linux-specific script                                                
~/git/rekoginition-identity-verification/docker-deploy/debug.sh                   
```

Locally installing on a workstation requires the following steps.  The specific commands can be found within the cdk-deploy/Dockerfile (https://github.com/aws-samples/rekognition-identity-verification/blob/main/images/cdk-deploy/Dockerfile).  Using this approach simplifies specific debugging scenarios, and is recommended for more sophisticated development scenarios.

1. Locally install AWS CDK as the [official documentation](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) describes.
2. [Bootstrap CDK for AWS Account](https://github.com/aws/aws-cdk/blob/master/design/cdk-bootstrap.md) 
3. Install Python >=3.6 from [python.org](http://python.org/)
4. Install the additional dependencies using: pip3 install -r [requirements.txt](images/cdk-deploy/requirements.txt)

**Option: Local Install**:  Debian (Bullseye), Ubuntu (Focal), OSX (Catalina), and Amazon Linux 2 users can run the [one-click.sh](one-click.sh) script to synthesize the OneClickTemplate.template.json for Amazon CloudFormation and deploy the supporting Lambda functions.  The script will also install any missing dependencies on the local box.

**Option: Docker**: The solution comes with [Docker-Enabled Deployment Scripts](docker-deploy) that will provide a consistent experience without cluttering your workstation.  This route will is geared toward developers and power users specifically. 

Note: Developers must [configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) and [install](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) the AWS CLI before using either path.  This requirement comes from both install solutions relying on the `~/.aws/credentials` to access cloud resources.

## Solution Deployment

The [one-click.sh](https://github.com/aws-samples/rekognition-identity-verification/blob/main/one-click.sh) utility script is the recommended procedure for deploying a RIV stack into an AWS Account.  It automates every step including installing missing dependency and executing all Out-Of-Band (OOB) operations.  Additionally, there is support for upgrading existing environments and seamlessly handling any future requirements.  The script relies on environment variables to control its behavior.  Customers can either explicitly define these values or rely on its discovery mechanisms.

```sh
# Run the script                                                                  
./one-click.sh  my-unique-bucket-name                                             
```

This table enumerates the overridable environment variables.  The deployment script supports deploying multiple stacks within the same account and region (e.g., Prod and Dev in us-east-1).  Additionally, the default settings support 200M unique faces.  Please contact us at rekognition-identity-verification@amazon.com for instructions beyond this threshold.  Lastly, AWS CloudFormation requires the Amazon S3 bucket and deployment region are the same.  When these values differ the *create-stack* command fails with a descriptive error.

```sh
# Create a bucket in your desired region.
# If the specified bucket does not exist, it will be created.
# Note: Bucket name cannot contain dots (.)
export AWS_REGION=us-east-1
export BUCKET_NAME=my-unique-bucket-name

# Customers can deploy multiple instances to the same region (Prod vs Dev)
# If this value is not set then it defaults to 'Riv-Prod'
# You control this functionality by setting the Landing Zone Name value
export RIV_STACK_NAME=Riv-Prod

# Running this command will install any dependencies (brew, yum, or apt required)
# After preparing the local machine it will synthesize and deploy into your environment.
TOTAL_COLLECTIONS=1 ./one-click.sh $BUCKET_NAME
```

|Name|	Default|	Description|
|----|----------|------------|
|TOTAL_COLLECTIONS|	1|	Total Rekognition Collections to Create (1=20M faces)|
|RIV_STACK_NAME	|Riv-Prod	|The stack name |
|S3_ASSET_BUCKET|	Argument |	The Amazon S3 Bucket to stage deployment artifacts|
|S3_REGION|	Discovered |	The Region hosting the S3_ASSET_BUCKET|

## How do I run the amplify app locally
#First create a .env.local file in the frontend directory with the following contents:

```
REACT_APP_ENV_API_URL=https://YOUR_API_GW_STAGE_URL
REACT_APP_IDENTITYPOOL_ID=COGNITO_IDENTITY_POOL_ID
REACT_APP_REGION=COGNITO_APP_REGION
REACT_APP_USERPOOL_ID=COGNITO_APP_USERPOOL_ID
REACT_APP_WEBCLIENT_ID=COGNITO_APP_WEBCLIENT_ID

```

#Install depedency and start the app

```
npm install
npm start

```


## How is the code organized

- [images](images). Contains any docker definitions to deploy the solution
- [infra](infra).  CDK Automation for provisioning the environment(s)
  - [bulkloader](infra/bulkloader).  The RIV bulk importing service. 
  - [services](infra/services). Standard AWS supporting components (e.g., backup)
  - [storage](infra/storage). Defines all shared data stores.
  - [userportal](infra/userportal).  The public interface that endusers interact with
- [src](src).  The backing code for Lambdas functions and other compute constructs
  - [rekognition](src/rekognition).  Step function tasks for interacting with Amazon Rekognition
  - [bulk-loader](src/bulk-loader).  Imports a source bucket into the RIV service
  - [test-client](src/test-client).  A command line interface for interacting with the RIV service.
  - [textract](src/textract).  Step function tasks for interacting with Amazon Textract
  - [frontend](src/frontend).  React Frontend Web App for Indentificaton Verification

## How do I get intellisence in Microsoft Visual Studio Code

1. Run `pip3 install -r images/cdk-deploy/requirements.txt`
1. Close and reopen the project e.g., `code /git/amazon-rekognition-identity-verification`
