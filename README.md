# Amazon Rekognition Identity Verification (RIV)

A solution to assist with identity verification using Amazon Rekognition.

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

## How can I deploy this solution

**Option: Local Install**:  Debian (Bullseye), Ubuntu (Focal), OSX (Catalina), and Amazon Linux 2 users can run the [one-click.sh](one-click.sh) script to synthesize the OneClickTemplate.template.json for Amazon CloudFormation and deploy the supporting Lambda functions.  The script will also install any missing dependencies on the local box.

```sh
# Create a bucket in your desired region
# Note: Bucket name cannot contain dots (.)
REGION_NAME=us-east-1
BUCKET_NAME=my-unique-bucket-name
aws s3api create-bucket --region $REGION_NAME --create-bucket-configuration "{\"LocationConstraint\": \"$REGION_NAME\"}" --bucket $BUCKET_NAME

# Customers can deploy multiple instances to the same region (Prod vs Dev)
# If this value is not set then it defaults to 'Simple'
# You control this functionality by setting the Landing Zone Name value
export ZONE_NAME=Prod

# Running this command will install any dependencies (brew, yum, or apt required)
# After preparing the machine it will synthesize and deploy the environment
./one-click.sh $BUCKET_NAME
```

**Option: Docker**: The solution comes with [Docker-Enabled Deployment Scripts](docker-deploy) that will provide a consistent experience without cluttering your workstation.  This route will is geared toward developers and power users specifically. 

Note: Developers must [configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) and [install](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) the AWS CLI before using either path.  This requirement comes from both install solutions relying on the `~/.aws/credentials` to access cloud resources.

## How do I get intellisence in Microsoft Visual Studio Code

1. Run `pip3 install -r images/cdk-deploy/requirements.txt`
1. Close and reopen the project e.g., `code /git/amazon-rekognition-identity-verification`
