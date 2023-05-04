import json
import logging
import boto3
from botocore.exceptions import ClientError

client = boto3.client('amplify')


def lambda_handler(event, context):
    # apps = client.list_apps()
    appName, appId = getApp(event['app'])
    if(appName is not None):
        branch = getBranch(appId, event['branch'])
        if(branch is not None):
            jobId = False
            jobId = getJob(appId,branch)
            if(jobId is not None):
                while(jobId == False):
                    job_status = client.get_job(
                        appId=appId,
                        branchName=branch,
                        jobId=jobId
                    )
                    status = job_status['job']['summary']['status']
                    if (status == 'FAILED' or status == 'SUCCEED' or status == 'CANCELLED'):
                        jobId = True
                        break
    return {
        "status":"Amplify App deployed Successfully."
    }
    


def getApp(name):
    apps = client.list_apps()
    appName = None
    appId = None
    for sub in apps['apps']:
        if sub['name'] == name:
            appName = sub['name']
            appId = sub['appId']
            # deleteAPP = client.delete_app(
            #     appId=sub['appId']
            # )
            break
    return appName, appId


def getBranch(appId, name):
    response = client.list_branches(appId=appId)
    branchName = None
    for sub in response['branches']:
        if sub['branchName'] == name:
            branchName = sub['branchName']
            break
    return branchName


def getJob(appId, branch):
    jobs = client.list_jobs(
        appId=appId,
        branchName=branch,
    )
    jobId = None
    for sub in jobs['jobSummaries']:
        status = sub['status']
        if (status == 'PENDING' or status == 'PROVISIONING' or status == 'RUNNING' or status == 'CANCELLING'):
            jobId = sub['jobId']
            break
    return jobId



