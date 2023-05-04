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

function color_red(){
  echo -e "\e[1;31m"
}

function color_green(){
  echo -e "\e[1;32m"
}

function color_reset(){
  echo -e "\e[1;0m"
}

color_green
echo "###########################################################"
echo "Configuring collections"
echo "###########################################################"

color_reset
if [ -z "$TOTAL_COLLECTIONS" ]
then
  color_reset
  export TOTAL_COLLECTIONS=1
  echo "TOTAL_COLLECTIONS not set, defaulted to 1 collections (20M faces)."
else
  echo "TOTAL_COLLECTIONS overridden to $TOTAL_COLLECTIONS (1 collection = 20M faces)."
fi

if [ -z "$RIV_STACK_NAME" ]
then
  color_green
  echo "###########################################################"
  echo "Defaulting RIV_STACK_NAME to Riv-Prod"
  echo "###########################################################"
  export RIV_STACK_NAME=Riv-Prod
  echo
fi

color_green
echo "###########################################################"
echo "#  Confirm the required tooling is present"
echo "###########################################################"
echo 
color_reset
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
  apt-get -y install --no-install-recommends npm curl zip jq python3-pip
fi
if [[ "`is_present brew`" -eq "0" ]]; then
  brew update
  brew install node curl zip jq python
fi

for f in npm python3 jq zip; do
  if [[ "`is_present $f`" -eq "1" ]]; then
    color_red
    echo "Requirement: [$f]: MISSING"
    color_reset
    exit 1
  fi
done

if [[ "`is_present awscliv2`" -eq "1" ]]; then
  pip3 install awscliv2
  awscliv2 --install
  if [[ "$?" -ne "0" ]]; then
    color_red
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! Install awscli Failed  !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    color_reset
    exit 1
  fi

  echo "=============================="
  echo "You must configure AWS CLI"
  echo "=============================="
  echo "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html"
  echo
  awscliv2 configure
fi

if [[ "`is_present cdk`" -eq "1" ]]; then
  npm -g install -g aws-cdk
  if [[ "$?" -ne "0" ]]; then
    color_red
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! Install CDK Failed  !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Try running this script as"
    echo "--------------------------"
    echo "sudo $0 $1"
    color_reset
    exit 1
  fi
fi

color_green
echo Passed.
echo

export S3_REGION=${S3_REGION:-$(aws configure get region)}

if [ -z "$S3_REGION" ]
then
  color_red
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Unable to determine region !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  color_reset
  exit 1
fi

# us-east-1 does not support location-constraints
# Its a special case likely for backward compatibility
if [ "$S3_REGION" == "null" ]
then
  export S3_REGION=us-east-1
fi

color_green
echo Passed.
echo

echo "###########################################################"
echo "#  Synth the Deployment"
echo "###########################################################"
echo 
color_reset

rm -rf $BASE_DIR/cdk.out
mkdir -p $BASE_DIR/cdk.out
pip3 install -r $BASE_DIR/images/cdk-deploy/requirements.txt >$BASE_DIR/cdk.out/pip3.log 2>&1 

if [ "$?" -ne "0" ]
then
  color_red
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Error installing cdk dependencies !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "Try invoking script as                 "
  echo "---------------------------------------"
  echo "sudo $0 $1"
  color_reset
  exit 1
fi

chmod a+x $BASE_DIR/app.py
cdk synth -a $BASE_DIR/app.py --require-approval never > $BASE_DIR/cdk.out/synth.log
if [ "$?" -ne "0" ]
then
  color_red
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Unable to synthesize stack !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  color_reset
  exit 1
fi

export STACK_TEMPLATE_FILE=$BASE_DIR/cdk.out/$RIV_STACK_NAME.template.json
python3 $BASE_DIR/default-params.py > $BASE_DIR/cdk.out/OneClickTemplate.template.json
if [ "$?" -ne 0 ]
then 
  color_red
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Unable to default  Params  !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  color_reset
  exit 1
fi

mv $STACK_TEMPLATE_FILE $STACK_TEMPLATE_FILE.original
mv $BASE_DIR/cdk.out/OneClickTemplate.template.json $STACK_TEMPLATE_FILE

color_green
echo Passed.
echo 

echo "###########################################################"
echo "#  Zip the assets"
echo "###########################################################"
echo 
color_reset
for f in `ls $BASE_DIR/cdk.out/ | grep 'asset\.' | grep -v .zip`
do
  pushd $BASE_DIR/cdk.out/$f
  if [ -e "$BASE_DIR/cdk.out/$f/requirements.txt" ]
  then
    pip3 install --no-build-isolation -r "$BASE_DIR/cdk.out/$f/requirements.txt" -t ./python > $BASE_DIR/cdk.out/$f.pip3.log
    # pip3 install aws-cdk.aws-cognito-identitypool -t ./python > $BASE_DIR/cdk.out/$f.pip3.log

    if [ "$?" -ne "0" ]
    then
      color_red
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "!! Unable to pip3 install     !!"
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "pip3 install --no-build-isolation -r "$BASE_DIR/cdk.out/$f/requirements.txt" -t ./python"
      echo cat $BASE_DIR/cdk.out/$f.pip3.log

      color_reset
      exit 1
    fi
  fi
  zip -r ../$f.zip . > zip.log
  color_green
  echo Zipped `wc -l zip.log | cut -d ' ' -f 1` files.
  color_reset
  popd
  #rm -rf $BASE_DIR/cdk.out/$f
done

# awscliv2 --region ${S3_REGION} s3 cp --recursive $BASE_DIR/cdk.out/ s3://$S3_ASSET_BUCKET/$S3_ASSET_PREFIX/

color_green
echo Passed.
echo

echo "###########################################################"
echo "#  Tell user how to deploy this stack"
echo "###########################################################"
echo 

echo "===================================="
echo "Asset Deployment Successful"
echo "===================================="
color_reset
echo Asset Bucket     : $S3_ASSET_BUCKET
echo Asset Prefix     : $S3_ASSET_PREFIX
echo Asset Region     : $S3_REGION
echo StackTemplate    : $STACK_TEMPLATE_FILE
echo

color_green
echo "===================================="
echo "Bootstrap CDK"
echo "===================================="
color_reset
ACCOUNT_ID=`awscliv2 --region ${S3_REGION} sts get-caller-identity | jq '.Account' | tr -d '"'`
if [ "$?" -ne "0" -o -z "$ACCOUNT_ID" ]
then
  color_red
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Query STS Failed      !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  color_reset
  exit 1
fi 

color_reset
cdk bootstrap aws://${ACCOUNT_ID}/${S3_REGION}
#npx cdk@2.1.0 bootstrap aws://${ACCOUNT_ID}/${S3_REGION}

if [[ "$?" -ne "0" ]]; then
  color_red
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! CDK Boostrap Failed   !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  color_reset
  exit 1
fi

color_green
echo Passed.
echo

# /infra/services/rekognition/topology.py - handles this step.
# echo "===================================="
# echo "Create Rekognition Objects"
# echo "===================================="
# color_reset
# REGION=$S3_REGION python3 $BASE_DIR/src/rekognition/setup/app.py
# if [ "$?" -ne "0" ]
# then
#   color_red
#   echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
#   echo "!! Configure Rekognition Failed   !!"
#   echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
#   color_reset
#   exit 1
# fi

color_green
echo "===================================="
echo "Deploying Stack "
echo "===================================="
color_reset


CDK_REGION=S3_REGION cdk deploy -a ./app.py --require-approval never
