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

echo "###########################################################"
echo "#  Determine which bucket to use"
echo "###########################################################"
echo 

if [ -z "$S3_ASSET_BUCKET" ]
then
  if [ -z "$1" ]
  then
    color_red
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! Missing S3_ASSET_BUCKET    !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "Usage: $0 bucket_name      "
    color_reset
    exit 1
  fi
  color_reset
  echo "Setting S3_ASSET_BUCKET = $1"
  export S3_ASSET_BUCKET=$1
fi

if [[ "$S3_ASSET_BUCKET" =~ "." ]]
then
  color_red
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "!! Unsupported BucketName     !!"
  echo "!! Name cannot contain '.'    !!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  color_reset
  exit 1
fi

if [ -z "$S3_ASSET_PREFIX" ]
then
  export S3_ASSET_PREFIX=`date +%Y/%m/%d/%H`
fi

if [ -z "$S3_REGION" ]
then
  color_green
  echo "======================="
  echo "Querying S3_REGION    "
  echo "======================="
  export S3_REGION=`awscliv2 s3api get-bucket-location --bucket $S3_ASSET_BUCKET | jq '.LocationConstraint' | tr -d '"'`
  if [ -z "$S3_REGION" ]
  then
    color_reset
    echo "Bucket not found.  Attempting to create..."
    for var in AWS_REGION AWS_DEFAULT_REGION CDK_DEFAULT_REGION
    do
      color_reset
      echo "Looking for export $var"
      # Check if the environment variable exists.
      if [ ! -z ${!var} ]
      then
        color_green
        echo "------------"
        echo "Attempting to create bucket $S3_ASSET_BUCKET in ${!var}"
        echo "------------"
        color_reset

        # If this is for us-east-1 then we cannot specify the LocationConstraint
        # Every other region requires this flag
        if [ "${!var}" == "us-east-1" ]
        then
          awscliv2 s3api create-bucket --region ${!var} --bucket $S3_ASSET_BUCKET
        else
          awscliv2 s3api create-bucket --region ${!var} --create-bucket-configuration LocationConstraint=${!var} --bucket $S3_ASSET_BUCKET
        fi
        break
      fi
    done
    export S3_REGION=`awscliv2 s3api get-bucket-location --bucket $S3_ASSET_BUCKET | jq '.LocationConstraint' | tr -d '"'`
  else
    color_reset
    echo "Found bucket in region $S3_REGION"
  fi
fi

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
    pip3 install -r "$BASE_DIR/cdk.out/$f/requirements.txt" -t ./python > $BASE_DIR/cdk.out/$f.pip3.log
    if [ "$?" -ne "0" ]
    then
      color_red
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "!! Unable to pip3 install     !!"
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "pip3 install -r "$BASE_DIR/cdk.out/$f/requirements.txt" -t ./python"
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

awscliv2 --region ${S3_REGION} s3 cp --recursive $BASE_DIR/cdk.out/ s3://$S3_ASSET_BUCKET/$S3_ASSET_PREFIX/

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


export API_END_POINT=`awscliv2 cloudformation describe-stacks --stack-name $RIV_STACK_NAME --query "Stacks[0].Outputs[0].OutputValue" --output text`
export BRANCH_NAME=prod

function wait-for-deployment() {
    local jobId=$1
    local timeout=300
    echo "MONITORING: awscliv2 amplify get-job --branch-name ${BRANCH_NAME} --app-id ${APP_ID} --job-id ${jobId}"
    while [[ ! $jobStatus == 'SUCCEED' || $timer > $timeout ]]; do
        local job=$(awscliv2 amplify get-job --branch-name ${BRANCH_NAME} --app-id ${APP_ID} --job-id ${jobId})
        local jobStatus=$(echo ${job} | jq -r '.job.summary.status')
        if [[ $((timer % 5)) == 0 ]]; then
            echo "Waiting for job current status ${jobStatus}"
        fi
        sleep 1
        timer=$((timer + 1))
    done

    curl $(echo ${job} | jq -r '.job.steps[] | select ( .stepName  | contains ( "DEPLOY")) | .logUrl')

}

color_green
echo "###########################################################"
echo "# Build React Frontend APP"
echo "###########################################################"
color_reset

pushd $BASE_DIR/src/frontend

npm install
REACT_APP_ENV_API_URL=$API_END_POINT npm run build

popd

color_green
echo "###########################################################"
echo "#  Create Amplify App"
echo "###########################################################"
color_reset

export AmplifyApp=`awscliv2 amplify list-apps | jq  '.apps[]| select(.name=="Riv-Prod")'`
if [ -z "$AmplifyApp" ]; then
  echo "===================="
  echo "Creating new app"
  echo "===================="
  printf -v data '{"REACT_APP_ENV_API_URL": "%s"}' "$API_END_POINT"
  awscliv2 amplify create-app --name $RIV_STACK_NAME --environment-variables "$data" --custom-rules source='</^((?!\.(css|gif|ico|jpg|js|png|txt|svg|woff|ttf)$).)*$/>',target='/index.html',status=200 --build-spec "REACT_APP_ENV_API_URL=$REACT_APP_ENV_API_URL" 
  if [[ "$?" -ne "0" ]]; then
    color_red
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! amplify create-app failed   !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    color_reset
    exit 1
  fi
  export AmplifyApp=`awscliv2 amplify list-apps | jq  '.apps[]| select(.name=="Riv-Prod")'`
fi

echo "===================="
echo "Using amplify app   "
echo "===================="
echo $AmplifyApp | jq

export APP_ID=`echo $AmplifyApp | jq .appId | tr -d '"'`

color_green
echo "###########################################################"
echo "#  Create Branch"
echo "###########################################################"
color_reset

AmplifyBranch=`awscliv2 amplify list-branches --app-id $APP_ID | jq '.branches[]|select(.branchName=="prod")'`
if [ -z "$AmplifyBranch" ]; then
  echo "===================="
  echo "Creating new branch"
  echo "===================="
  awscliv2 amplify create-branch --app-id ${APP_ID} --environment-variables "$data" --branch-name ${BRANCH_NAME}
  if [[ "$?" -ne "0" ]]; then
    color_red
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! amplify create-branch failed!!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    color_reset
    exit 1
  fi
  AmplifyBranch=`awscliv2 amplify list-branches --app-id $APP_ID | jq '.branches[]|select(.branchName=="prod")'`
fi

echo "===================="
echo "Using branch"
echo "===================="
echo $AmplifyBranch | jq

color_green
echo "###########################################################"
echo "#  Create Zip Archive"
echo "###########################################################"
color_reset

echo "===================="
echo "Compressing files"
echo "===================="
pushd "${BASE_DIR}/src/frontend/build"
rm -f ${BRANCH_NAME}.zip
zip -rq ${BRANCH_NAME}.zip .
ls -lh ${BRANCH_NAME}.zip
popd

echo Passed.

color_green
echo "###########################################################"
echo "#  Deploying Amplify frontend"
echo "###########################################################"
color_reset

# echo "===================="
# echo "Waiting for any pending"
# echo "===================="

# while [[ 1 ]]; do
#   ListJobs=`awscliv2 amplify list-jobs --app-id $APP_ID --branch-name $BRANCH_NAME | jq '.jobSummaries[]|select(.status=="PENDING")'`
#   if [ -z "$ListJobs" ]; then
#     echo "All previous jobs have finished."
#     break
#   fi
  
#   echo "Waiting on $APP_ID ($BRANCH_NAME) to complete `echo $ListJobs|grep status|wc -l` jobs."
#   sleep 15
# done  

echo "===================="
echo "Terminating any pending jobs"
echo "===================="
for jobId in `awscliv2 amplify list-jobs --app-id $APP_ID --branch-name $BRANCH_NAME | jq -r '.jobSummaries[]|select(.status=="PENDING")|.jobId'`;
do
  echo "awscliv2 amplify stop-job --app-id $APP_ID --branch-name $BRANCH_NAME --job-id $jobId"  
  awscliv2 amplify stop-job --app-id $APP_ID --branch-name $BRANCH_NAME --job-id jobId
done

echo Passed.
echo

echo "===================="
echo "amplify create-deployment"
echo "===================="

read jobId URL < <(echo $(awscliv2 amplify create-deployment --app-id  ${APP_ID} --branch ${BRANCH_NAME} | jq -r '.jobId, .zipUploadUrl'))
curl -v --upload-file "${BASE_DIR}/src/frontend/build/${BRANCH_NAME}.zip" $URL
if [[ "$?" -ne "0" ]]; then
    color_red
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! Upload file failed  !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!"
    color_reset
    exit 1
fi

deployment=$(awscliv2 amplify start-deployment --app-id ${APP_ID} --branch-name ${BRANCH_NAME} --job-id ${jobId})
if [[ "$?" -ne "0" ]]; then
    color_red
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! Start-Deployment Failed  !!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    color_reset
    exit 1
fi

echo $deployment | jq

echo "===================="
echo "Waiting for deployment"
echo "===================="

wait-for-deployment $(echo ${deployment} | jq -r '.jobSummary.jobId')

color_green
echo Deployment Complete.
color_reset

# awscliv2 cloudformation describe-stacks --stack-name ${RIV_STACK_NAME} --region ${S3_REGION} 2>/dev/null >/dev/null
# if [[ "$?" -eq "0" ]]; then
#   cfn_command=update-stack
# else
#   cfn_command=create-stack
# fi

# STACK_NAME=`echo --region ${S3_REGION} --stack-name ${RIV_STACK_NAME}`
# TEMPLATE_URL=`echo --template-url https://${S3_ASSET_BUCKET}.s3.${S3_REGION}.amazonaws.com/${S3_ASSET_PREFIX}/${RIV_STACK_NAME}.template.json`
# IAM_CAPABILITIES=`echo --capabilities CAPABILITY_NAMED_IAM`

# color_green
# echo "awscliv2 cloudformation ${cfn_command} ${STACK_NAME} ${TEMPLATE} ${TEMPLATE_URL} ${IAM_CAPABILITIES}"
# color_reset

# awscliv2 cloudformation ${cfn_command} ${STACK_NAME} ${TEMPLATE} ${TEMPLATE_URL} ${IAM_CAPABILITIES}
