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
echo "===================================="
echo "Deploying Stack "
echo "===================================="
color_reset

if [ -z "$RIV_STACK_NAME" ]
then
  color_green
  echo "###########################################################"
  echo "Defaulting RIV_STACK_NAME to Riv-Prod"
  echo "###########################################################"
  export RIV_STACK_NAME=Riv-Prod
  echo
fi


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
