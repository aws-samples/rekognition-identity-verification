# Amazon Rekognition Identity Verification (RIV)

A solution to assist with identity verification using Amazon Rekognition.

## Prerequisites

```sh
# Setup the AWS CLI
aws configure                                                                     
 ```                                                                                  

1. Locally install AWS CDK as the [official documentation](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) describes.
2. [Bootstrap CDK for AWS Account](https://github.com/aws/aws-cdk/blob/master/design/cdk-bootstrap.md) 
3. Create a Python virtual environment
  ```sh
  python3 -m venv .venv                                      
  ```

4. Activate virtual environment
  On MacOS or Linux
  ```sh
  source .venv/bin/activate                                       
  ```
  On Windows
  ```sh
    .venv\Scripts\activate.bat                                        
```
  

## Solution Deployment

The [one-click.sh](https://github.com/aws-samples/rekognition-identity-verification/blob/main/one-click.sh) utility script is the recommended procedure for deploying a RIV stack into an AWS Account.  It automates every step including installing missing dependency and executing all Out-Of-Band (OOB) operations.  Additionally, there is support for upgrading existing environments and seamlessly handling any future requirements.  The script relies on environment variables to control its behavior.  Customers can either explicitly define these values or rely on its discovery mechanisms.

This table enumerates the overridable environment variables.  The deployment script supports deploying multiple stacks within the same account and region (e.g., Prod and Dev in us-east-1).  Additionally, the default settings support 200M unique faces.  Please contact us at rekognition-identity-verification@amazon.com for instructions beyond this threshold.  Lastly, AWS CloudFormation requires the Amazon S3 bucket and deployment region are the same.  When these values differ the *create-stack* command fails with a descriptive error.

```sh
# Set the desired region.
export AWS_REGION=us-east-1

# Customers can deploy multiple instances to the same region (Prod vs Dev)
# If this value is not set then it defaults to 'Riv-Prod'
# You control this functionality by setting the Landing Zone Name value
export RIV_STACK_NAME=Riv-Prod

# Running this command will install any dependencies (brew, yum, or apt required)
# After preparing the local machine it will synthesize and deploy into your environment.
TOTAL_COLLECTIONS=1 ./one-click.sh

#TOTAL_COLLECTIONS=1 ./one-click.sh 
```

|Name|	Default|	Description|
|----|----------|------------|
|TOTAL_COLLECTIONS|	1|	Total Rekognition Collections to Create (1=20M faces)|
|RIV_STACK_NAME	|Riv-Prod	|The stack name |


## How do I run the amplify app locally
#First create a .env.local file in the frontend directory with the following contents:

```
REACT_APP_ENV_API_URL=https://YOUR_API_GW_STAGE_URL
REACT_APP_IDENTITYPOOL_ID=REACT_APP_IDENTITYPOOL_ID
REACT_APP_REGION=REACT_APP_REGION
REACT_APP_USERPOOL_ID=REACT_APP_USERPOOL_ID
REACT_APP_WEBCLIENT_ID=REACT_APP_WEBCLIENT_ID


```

#Install depedency and start the app

```
npm install
npm start

```


## How is the code organized

- [images](images). Contains any docker definitions to deploy the solution
- [infra](infra).  CDK Automation for provisioning the environment(s)
  - [services](infra/rekognition). Rekognition supporting components 
  - [storage](infra/storage). Defines all shared data stores.
  - [userportal](infra/userportal).  The public interface that endusers interact with
- [src](src).  The backing code for Lambdas functions and other compute constructs
  - [rekognition](src/rekognition).  Step function tasks for interacting with Amazon Rekognition
  - [test-client](src/test-client).  A command line interface for interacting with the RIV service.
  - [textract](src/textract).  Step function tasks for interacting with Amazon Textract
  - [frontend](src/frontend).  React Frontend Web App for Indentificaton Verification

## How do I get intellisence in Microsoft Visual Studio Code

1. Run `pip3 install -r images/cdk-deploy/requirements.txt`
1. Close and reopen the project e.g., `code /git/amazon-rekognition-identity-verification`
