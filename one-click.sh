#!/bin/bash
###########################################################
#  Deployment Script for One-Click Tool
#
#  This script will stage every required for directly 
#   launching this stack within a customer's accounts
#
#  Nate Bachmeier - 2021
###########################################################

BASE_DIR="$( cd "$( dirname "$0" )" && pwd )"

if [ -z "$TOTAL_COLLECTIONS" ]
then
  echo "###########################################################"
  echo "Defaulting total collections to 10 (<=200M faces)"
  echo "###########################################################"
  export TOTAL_COLLECTIONS=10
  echo
fi

if [ -z "ZONE_NAME" ]
then
  echo "###########################################################"
  echo "Defaulting ZONE_NAME to Simple"
  echo "###########################################################"
  export ZONE_NAME=Simple
  echo
fi

echo "###########################################################"
echo "#  Confirm the required tooling is present"
echo "###########################################################"
echo 
function is_present(){
  app_path_len=`command -v $1 | wc -c`
  if [[ "$app_path_len" -gt "0" ]];
  then
    echo "0"
  else
    echo "1"
  fi
}

if [[ "`is_present yum`" -eq "0" ]]; then
  yum -y update
  yum -y install zip jq python3 curl
  curl -sL https://rpm.nodesource.com/setup_16.x | bash -
  yum -y install nodejs

fi 
if [[ "`is_present apt-get`" -eq "0" ]]; then
  apt-get -y update
  apt-get -y install --no-install-recommends npm curl zip jq python3 pip
fi
if [[ "`is_present brew`" -eq "0" ]]; then
  brew update
  brew install node curl zip jq python
fi

for f in npm python3 jq zip; do
  if [[ "`is_present $f`" -eq "1" ]]; then 
    echo "Requirement: [$f]: MISSING"
    exit 1
  fi
done

if [[ "`is_present aws`" -eq "1" ]]; then
  pip3 install awscli
  if [[ "$?" -ne "0" ]]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! Install awscli Failed  !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
  fi

  echo "=============================="
  echo "You must configure AWS CLI"
  echo "=============================="
  echo "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html"
  echo
  aws configure
fi

if [[ "`is_present cdk`" -eq "1" ]]; then
  npm -g install -g aws-cdk
  if [[ "$?" -ne "0" ]]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! Install CDK Failed  !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Try running this script as"
    echo "--------------------------"
    echo "sudo $0 $1"
    exit 1
  fi
fi

echo Passed.
echo

echo "###########################################################"
echo "#  Determine which bucket to use"
echo "###########################################################"
echo 

if [ -z "$S3_ASSET_BUCKET" ]
then
  if [ -z "$1" ]
  then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! Missing S3_ASSET_BUCKET    !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Usage: $0 bucket_name      "
    exit 1
  fi
  echo "Setting S3_ASSET_BUCKET = $1"
  export S3_ASSET_BUCKET=$1
fi

if [[ "$S3_ASSET_BUCKET" =~ "." ]]
then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Unsupported BucketName     !!"
  echo "!! Name cannot contain '.'    !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  exit 1
fi

export S3_ASSET_PREFIX=`date +%Y/%m/%d/%H`
export STACK_TEMPLATE_FILE=$BASE_DIR/cdk.out/RIV-${ZONE_NAME}.template.json

if [ -z "$S3_REGION" ]
then
  echo "======================="
  echo "Querying S3_REGION    "
  echo "======================="
  export S3_REGION=`aws s3api get-bucket-location --bucket $S3_ASSET_BUCKET | jq '.LocationConstraint' | tr -d '"'`
  echo "Setting S3_REGION to $S3_REGION"
  echo
fi

if [ -z "$S3_REGION" ]
then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Unable to determine region !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  exit 1
fi

if [ "$S3_REGION" == "null" ]
then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Invalid LocationConstraint !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "--------------------------------"
  echo "Create a new bucket with command"
  echo "aws s3api create-bucket --region THE_REGION_NAME --create-bucket-configuration \"{\\\"LocationConstraint\\\": \\\"THE_REGION_NAME\\\"}\" --bucket THE_BUCKET_NAME"
  echo "--------------------------------"
  echo "Or explicitly specify the bucket region"
  echo "S3_REGION=THE_REGION_NAME $0 $1"
  echo "--------------------------------"
  exit 1
fi

echo Passed.
echo

echo "###########################################################"
echo "#  Synth the Deployment"
echo "###########################################################"
echo 

rm -rf $BASE_DIR/cdk.out
mkdir -p $BASE_DIR/cdk.out
pip3 install -r $BASE_DIR/images/cdk-deploy/requirements.txt >$BASE_DIR/cdk.out/pip3.log 2>&1

if [ "$?" -ne "0" ]
then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Error installing cdk dependencies !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "Try invoking script as                 "
  echo "---------------------------------------"
  echo "sudo $0 $1"
  exit 1
fi

cdk synth -a $BASE_DIR/app.py --require-approval never > $BASE_DIR/cdk.out/synth.log
if [ "$?" -ne "0" ]
then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Unable to synthesize stack !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  exit 1
fi

python3 $BASE_DIR/default-params.py > $BASE_DIR/cdk.out/OneClickTemplate.template.json
if [ "$?" -ne 0 ]
then 
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Unable to default  Params  !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  exit 1
fi

mv $STACK_TEMPLATE_FILE $STACK_TEMPLATE_FILE.original
mv $BASE_DIR/cdk.out/OneClickTemplate.template.json $STACK_TEMPLATE_FILE

echo Passed.
echo 

echo "###########################################################"
echo "#  Zip the assets"
echo "###########################################################"
echo 

for f in `ls $BASE_DIR/cdk.out/ | grep asset | grep -v .zip`
do
  pushd $BASE_DIR/cdk.out/$f
  if [ -e "$BASE_DIR/cdk.out/$f/requirements.txt" ]
  then
    pip3 install -r "$BASE_DIR/cdk.out/$f/requirements.txt" -t ./python > $BASE_DIR/cdk.out/$f.pip3.log
    if [ "$?" -ne "0" ]
    then 
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "!! Unable to pip3 install     !!"
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "pip3 install -r "$BASE_DIR/cdk.out/$f/requirements.txt" -t ./python"
      echo cat $BASE_DIR/cdk.out/$f.pip3.log
      exit 1
    fi
  fi
  zip -r ../$f.zip . > zip.log
  echo Zipped `wc -l zip.log | cut -d ' ' -f 1` files.
  popd
  rm -rf $BASE_DIR/cdk.out/$f
done

aws --region ${S3_REGION} s3 cp --recursive $BASE_DIR/cdk.out/ s3://$S3_ASSET_BUCKET/$S3_ASSET_PREFIX/

echo Passed.
echo

echo "###########################################################"
echo "#  Tell user how to deploy this stack"
echo "###########################################################"
echo 

echo "===================================="
echo "Asset Deployment Successful"
echo "===================================="
echo Asset Bucket     : $S3_ASSET_BUCKET
echo Asset Prefix     : $S3_ASSET_PREFIX
echo Asset Region     : $S3_REGION
echo StackTemplate    : $STACK_TEMPLATE_FILE
echo

echo "===================================="
echo "Bootstrap CDK"
echo "===================================="

ACCOUNT_ID=`aws --region ${S3_REGION} sts get-caller-identity | jq '.Account' | tr -d '"'`
if [ "$?" -ne "0" -o -z "$ACCOUNT_ID" ]
then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Query STS Failed      !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  exit 1
fi 

cdk bootstrap aws://${ACCOUNT_ID}/${S3_REGION}

if [[ "$?" -ne "0" ]]; then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! CDK Boostrap Failed   !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  exit 1
fi

echo Passed.
echo

echo "===================================="
echo "Create Rekognition Objects"
echo "===================================="
REGION=$S3_REGION python3 $BASE_DIR/src/rekognition/setup/app.py
if [ "$?" -ne "0" ]
then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Configure Rekognition Failed   !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  exit 1
fi

echo "===================================="
echo "Stack Deployment Command"
echo "===================================="

aws cloudformation describe-stacks --stack-name Identity-Verification-${ZONE_NAME} --region ${S3_REGION} 2>/dev/null >/dev/null
if [[ "$?" -eq "0" ]]; then
  cfn_command=update-stack
else
  cfn_command=create-stack
fi

STACK_NAME=`echo --region ${S3_REGION} --stack-name Identity-Verification-${ZONE_NAME}`
TEMPLATE_URL=`echo --template-url https://${S3_ASSET_BUCKET}.s3.${S3_REGION}.amazonaws.com/${S3_ASSET_PREFIX}/RIV-${ZONE_NAME}.template.json`
IAM_CAPABILITIES=`echo --capabilities CAPABILITY_NAMED_IAM`

echo "aws cloudformation ${cfn_command} ${STACK_NAME} ${TEMPLATE} ${TEMPLATE_URL} ${IAM_CAPABILITIES}"
aws cloudformation ${cfn_command} ${STACK_NAME} ${TEMPLATE} ${TEMPLATE_URL} ${IAM_CAPABILITIES}
