####################################################################################################
# 
# Purpose   : get list codedeploy
# Source    : codedeploy.py
# Usage     : python codedeploy.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.08     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codedeploy.html
#          
####################################################################################################
### This first line is for modules to work with Python 2 or 3
from __future__ import print_function
import os, sys, getopt
import json 
from urllib import request
import boto3
import logging

# OS 판단  : win32, linux, cygwin, darwin, aix
my_os = sys.platform
#print(my_os)
if my_os == "linux":
  path_logconf = os.getcwd() + '/config/logging.conf'
else:
  path_logconf = os.getcwd() + '\config\logging.conf'

if __name__ == "__main__":
  # Main 실행으로 절대 경로 
  from config import awsglobal
  awsglobal.init_logger(path_logconf)
  global klogger
  global klogger_dat

  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
#   import utils  오류
#  * global 변수를 공유하는 package 내의 모듈을 Main으로 실행할 때 import 하는 방법 확인 필요.

else:
  # Module 실행으로 상대 경로 
  from .config import awsglobal
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
  from . import utils

def list_applications():
  '''
    search codedeploy  
  '''
  klogger_dat.debug('codedeploy applications')

  try:
    results = [] 
    codedeploy=boto3.client('codedeploy')
    applications = codedeploy.list_applications()
    # klogger_dat.debug(applications)
    if 200 == applications["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(applications["applications"])
      if len(applications["applications"]) > 0 :
        for application in applications["applications"]:
        #   klogger_dat.debug(application)
          applinfo = get_application(application)
        #   klogger_dat.debug(applinfo)
          applicationid = ''; createtime = ''; linkedtogithub = ''; computeplatform = [];
          if applinfo != None :
            applicationid = applinfo['applicationId'] if 'applicationId' in applinfo else ' '
            createtime = applinfo['createTime'].strftime('%Y-%m-%d %H:%M') if 'createTime' in applinfo else ' '
            linkedtogithub = applinfo['linkedToGitHub'] if 'linkedToGitHub' in applinfo else ' '
            computeplatform.append(applinfo['computePlatform'] if 'computePlatform' in applinfo else ' ')
          deploygrps = list_deployment_groups(application)
          deploygrpname = []; deploycfgname = []; ec2tagfilters = []; onpremtagfilters = []; autoscalinggrps = [];
          svcrolearns = []; targetrevisions = []; deploymentstyles = []; outdatedinsstrategies = []; bluegreencfgs = [];
          lbinfos = []; ec2tagsets = []; onpremtagsets = []; computeplatforms = []; ecsservices = [];
          for deploygrp in deploygrps:
            deploygrpinfo = get_deployment_group(application, deploygrp)
            # klogger_dat.debug(deploygrpinfo)
            if deploygrpinfo != None :
              deploygrpname.append(deploygrpinfo['deploymentGroupName'])
              deploycfgname.append(deploygrpinfo['deploymentConfigName'] if 'deploymentConfigName' in deploygrpinfo else ' ')
              if 'ec2TagFilters' in deploygrpinfo :
                for item in deploygrpinfo['ec2TagFilters'] :
                  ec2tagfilters.append(item) 
              if 'onPremisesInstanceTagFilters' in deploygrpinfo :
                for item in deploygrpinfo['onPremisesInstanceTagFilters'] :
                  onpremtagfilters.append(item)
              if 'autoScalingGroups' in deploygrpinfo :
                for item in deploygrpinfo['autoScalingGroups'] :
                  autoscalinggrps.append(item)
              svcrolearns.append(deploygrpinfo['serviceRoleArn'] if 'serviceRoleArn' in deploygrpinfo else ' ')
              targetrevisions.append(deploygrpinfo['targetRevision'] if 'targetRevision' in deploygrpinfo else ' ')
              deploymentstyles.append(deploygrpinfo['deploymentStyle'] if 'deploymentStyle' in deploygrpinfo else ' ')
              outdatedinsstrategies.append(deploygrpinfo['outdatedInstancesStrategy'] if 'outdatedInstancesStrategy' in deploygrpinfo else ' ')
              bluegreencfgs.append(deploygrpinfo['blueGreenDeploymentConfiguration'] if 'blueGreenDeploymentConfiguration' in deploygrpinfo else ' ')
              lbinfos.append(deploygrpinfo['loadBalancerInfo'] if 'loadBalancerInfo' in deploygrpinfo else ' ')
              ec2tagsets.append(deploygrpinfo['ec2TagSet'] if 'ec2TagSet' in deploygrpinfo else ' ')
              onpremtagsets.append(deploygrpinfo['onPremisesTagSet'] if 'onPremisesTagSet' in deploygrpinfo else ' ')
              computeplatforms.append(deploygrpinfo['computePlatform'] if 'computePlatform' in deploygrpinfo else ' ')
              if 'ecsServices' in deploygrpinfo :
                for ecssvc in deploygrpinfo['ecsServices'] :
                  ecsservices.append(ecssvc)
          # list count sync with space
          utils.ListSyncCountWithSpace(computeplatform, deploygrpname, deploycfgname, ec2tagfilters, onpremtagfilters,
                                       autoscalinggrps, svcrolearns, targetrevisions, deploymentstyles, outdatedinsstrategies,
                                       bluegreencfgs, lbinfos, ec2tagsets, onpremtagsets, computeplatforms, ecsservices
                                      )

          results.append( { "Application": application,
                            "applicationId" : applicationid,
                            "createTime" : createtime,
                            "linkedToGitHub" : linkedtogithub,
                            "computePlatform" : computeplatform,
                            "deploymentGroupName" : deploygrpname,
                            "deploymentConfigName" : deploycfgname,
                            "ec2TagFilters" : ec2tagfilters,
                            "onPremisesInstanceTagFilters" : onpremtagfilters,
                            "autoScalingGroups" : autoscalinggrps,
                            "serviceRoleArn" : svcrolearns,
                            "targetRevision" : targetrevisions,
                            "deploymentStyle" : deploymentstyles,
                            "outdatedInstancesStrategy" : outdatedinsstrategies,
                            "blueGreenDeploymentConfiguration" : bluegreencfgs,
                            "loadBalancerInfo" : lbinfos,
                            "ec2TagSet" : ec2tagsets,
                            "onPremisesTagSet" : onpremtagsets,
                            "computePlatform" : computeplatforms,
                            "ecsServices" : ecsservices,
                          })
      else: # column list
        results.append( { "Application": ' ',
                          "applicationId" : ' ',
                          "createTime" : ' ',
                          "linkedToGitHub" : ' ',
                          "computePlatform" : ' ',
                          "deploymentGroupName" : ' ',
                          "deploymentConfigName" : ' ',
                          "ec2TagFilters" : ' ',
                          "onPremisesInstanceTagFilters" : ' ',
                          "autoScalingGroups" : ' ',
                          "serviceRoleArn" : ' ',
                          "targetRevision" : ' ',
                          "deploymentStyle" : ' ',
                          "outdatedInstancesStrategy" : ' ',
                          "blueGreenDeploymentConfiguration" : ' ',
                          "loadBalancerInfo" : ' ',
                          "ec2TagSet" : ' ',
                          "onPremisesTagSet" : ' ',
                          "computePlatform" : ' ',
                          "ecsServices" : list(' '),
                        })
    else:
      klogger.error("call error : %d", applications["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "Application": 'ERROR CHECK',
                        "applicationId" : 'ERROR CHECK',
                        "createTime" : 'ERROR CHECK',
                        "linkedToGitHub" : 'ERROR CHECK',
                        "computePlatform" : 'ERROR CHECK',
                        "deploymentGroupName" : 'ERROR CHECK',
                        "deploymentConfigName" : 'ERROR CHECK',
                        "ec2TagFilters" : 'ERROR CHECK',
                        "onPremisesInstanceTagFilters" : 'ERROR CHECK',
                        "autoScalingGroups" : 'ERROR CHECK',
                        "serviceRoleArn" : 'ERROR CHECK',
                        "targetRevision" : 'ERROR CHECK',
                        "deploymentStyle" : 'ERROR CHECK',
                        "outdatedInstancesStrategy" : 'ERROR CHECK',
                        "blueGreenDeploymentConfiguration" : 'ERROR CHECK',
                        "loadBalancerInfo" : 'ERROR CHECK',
                        "ec2TagSet" : 'ERROR CHECK',
                        "onPremisesTagSet" : 'ERROR CHECK',
                        "computePlatform" : 'ERROR CHECK',
                        "ecsServices" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("codedeploy.list_applications(),%s", othererr)
    results.append( { "Application": 'ERROR CHECK',
                      "applicationId" : 'ERROR CHECK',
                      "createTime" : 'ERROR CHECK',
                      "linkedToGitHub" : 'ERROR CHECK',
                      "computePlatform" : 'ERROR CHECK',
                      "deploymentGroupName" : 'ERROR CHECK',
                      "deploymentConfigName" : 'ERROR CHECK',
                      "ec2TagFilters" : 'ERROR CHECK',
                      "onPremisesInstanceTagFilters" : 'ERROR CHECK',
                      "autoScalingGroups" : 'ERROR CHECK',
                      "serviceRoleArn" : 'ERROR CHECK',
                      "targetRevision" : 'ERROR CHECK',
                      "deploymentStyle" : 'ERROR CHECK',
                      "outdatedInstancesStrategy" : 'ERROR CHECK',
                      "blueGreenDeploymentConfiguration" : 'ERROR CHECK',
                      "loadBalancerInfo" : 'ERROR CHECK',
                      "ec2TagSet" : 'ERROR CHECK',
                      "onPremisesTagSet" : 'ERROR CHECK',
                      "computePlatform" : 'ERROR CHECK',
                      "ecsServices" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_application(applicationName):
  '''
    search codedeploy application
  '''
#   klogger_dat.debug('codedeploy application')

  try:
    result = None
    codedeploy=boto3.client('codedeploy')
    # klogger_dat.debug(applicationName)
    application = codedeploy.get_application(applicationName=applicationName)
    # klogger_dat.debug(application)
    if 200 == application["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(application["application"])
      if 'application' in application :
        result = application['application']
    else:
      klogger.error("call error : %d", application["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("codedeploy.get_application(),%s", othererr)
  finally:
    return result

def get_deployment_group(applicationName, deploymentGroupName):
  '''
    search codedeploy deployment group
  '''
#   klogger_dat.debug('codedeploy deployment group')

  try:
    result = None
    codedeploy=boto3.client('codedeploy')
    # klogger_dat.debug(applicationName, deploymentGroupName)
    deploygrp = codedeploy.get_deployment_group(applicationName=applicationName, deploymentGroupName=deploymentGroupName)
    # klogger_dat.debug(deploygrp)
    if 200 == deploygrp["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(deploygrp["deploymentGroupInfo"])
      if 'deploymentGroupInfo' in deploygrp :
        result = deploygrp['deploymentGroupInfo']
    else:
      klogger.error("call error : %d", deploygrp["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("codedeploy.get_deployment_group(),%s", othererr)
  finally:
    return result

def list_deployment_groups(applicationName):
  '''
    search codedeploy  deployment groups
  '''
#   klogger_dat.debug('codedeploy deployment groups')

  try:
    results = [] 
    codedeploy=boto3.client('codedeploy')
    deploygrps = codedeploy.list_deployment_groups(applicationName=applicationName)
    # klogger_dat.debug(deploygrps)
    if 200 == deploygrps["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(deploygrps["deploymentGroups"])
      if 'deploymentGroups' in deploygrps :
        results = deploygrps['deploymentGroups']
    else:
      klogger.error("call error : %d", deploygrps["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("codedeploy.list_deployment_groups(),%s", othererr)
  finally:
    return results

def list_deployments():
  '''
    search codedeploy depolyments
  '''
  klogger_dat.debug('codedeploy deployments')

  try:
    results = [] 
    codedeploy=boto3.client('codedeploy')
    deployments = codedeploy.list_deployments()
    # klogger_dat.debug(deployments)
    if 200 == deployments["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(deployments["deployments"])
      if len(deployments["deployments"]) > 0 :
        for deployment in deployments["deployments"]:
        #   klogger_dat.debug(deployment)
          deployinfo = get_deployment(deployment)
        #   klogger_dat.debug(deployinfo)
          applicationname = ' '; deploymentgrpname = ' '; deploymentcfgname = ' '; revisions = []; status = ' ';
          errinforms = []; createtime = ' '; completetime = ' '; description = ' '; creator = ' '; updateonly = ' ';
          deploymentstyles = []; targetinstances = []; bluegreencfgs = []; lbinfos = []; filebehavior = ' ';
          computeplatform = ' '; relateddeployments = [];

          if deployinfo != None :
            applicationname = deployinfo['applicationName'] if 'applicationName' in deployinfo else ' '
            deploymentgrpname = deployinfo['deploymentGroupName'] if 'deploymentGroupName' in deployinfo else ' '
            deploymentcfgname = deployinfo['deploymentConfigName'] if 'deploymentConfigName' in deployinfo else ' '
            if 'revision' in deployinfo :
              revisions.append(deployinfo['revision'])
            status = deployinfo['status'] if 'status' in deployinfo else ' '
            if 'errorInformation' in deployinfo :
              errinforms.append(deployinfo['errorInformation'])
            createtime = deployinfo['createTime'].strftime('%Y-%m-%d') if 'createTime' in deployinfo else ' '
            completetime = deployinfo['completeTime'].strftime('%Y-%m-%d') if 'completeTime' in deployinfo else ' '
            description = deployinfo['description'] if 'description' in deployinfo else ' '
            creator = deployinfo['creator'] if 'creator' in deployinfo else ' '
            if 'updateOutdatedInstancesOnly' in deployinfo :
              if deployinfo['updateOutdatedInstancesOnly'] :
                updateonly = 'True'
              else :
                updateonly = 'False'
            if 'deploymentStyle' in deployinfo :
              deploymentstyles.append(deployinfo['deploymentStyle'])
            if 'targetInstances' in deployinfo :
              targetinstances.append(deployinfo['targetInstances'])
            if 'blueGreenDeploymentConfiguration' in deployinfo :
              bluegreencfgs.append(deployinfo['blueGreenDeploymentConfiguration'])
            if 'loadBalancerInfo' in deployinfo :
              lbinfos.append(deployinfo['loadBalancerInfo'])
            filebehavior = deployinfo['fileExistsBehavior'] if 'fileExistsBehavior' in deployinfo else ' '
            computeplatform = deployinfo['computePlatform'] if 'computePlatform' in deployinfo else ' '
            if 'relatedDeployments' in deployinfo :
              relateddeployments.append(deployinfo['relatedDeployments'])
          # list count sync with space
          utils.ListSyncCountWithSpace(revisions, errinforms, deploymentstyles, targetinstances, bluegreencfgs, 
                                       lbinfos, relateddeployments
                                       )

          results.append( { "DeploymentId": deployment,
                            "applicationName" : applicationname,
                            "deploymentGroupName" : deploymentgrpname,
                            "deploymentConfigName" : deploymentcfgname,
                            "revision" : revisions,
                            "status" : status,
                            "errorInformation" : errinforms,
                            "createTime" : createtime,
                            "completeTime" : completetime,
                            "description" : description,
                            "creator" : creator,
                            "updateOutdatedInstancesOnly" : updateonly,
                            "deploymentStyle" : deploymentstyles,
                            "targetInstances" : targetinstances,
                            "blueGreenDeploymentConfiguration" : bluegreencfgs,
                            "loadBalancerInfo" : lbinfos,
                            "fileExistsBehavior" : filebehavior,
                            "computePlatform" : computeplatform,
                            "relatedDeployments" : relateddeployments,
                          })
      else: # column list
        results.append( { "DeploymentId": ' ',
                          "applicationName" : ' ',
                          "deploymentGroupName" : ' ',
                          "deploymentConfigName" : ' ',
                          "revision" : ' ',
                          "status" : ' ',
                          "errorInformation" : ' ',
                          "createTime" : ' ',
                          "completeTime" : ' ',
                          "description" : ' ',
                          "creator" : ' ',
                          "updateOutdatedInstancesOnly" : ' ',
                          "deploymentStyle" : ' ',
                          "targetInstances" : ' ',
                          "blueGreenDeploymentConfiguration" : ' ',
                          "loadBalancerInfo" : ' ',
                          "fileExistsBehavior" : ' ',
                          "computePlatform" : ' ',
                          "relatedDeployments" : list(' '),
                        })
    else:
      klogger.error("call error : %d", deployments["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "DeploymentId": 'ERROR CHECK',
                        "applicationName" : 'ERROR CHECK',
                        "deploymentGroupName" : 'ERROR CHECK',
                        "deploymentConfigName" : 'ERROR CHECK',
                        "revision" : 'ERROR CHECK',
                        "status" : 'ERROR CHECK',
                        "errorInformation" : 'ERROR CHECK',
                        "createTime" : 'ERROR CHECK',
                        "completeTime" : 'ERROR CHECK',
                        "description" : 'ERROR CHECK',
                        "creator" : 'ERROR CHECK',
                        "updateOutdatedInstancesOnly" : 'ERROR CHECK',
                        "deploymentStyle" : 'ERROR CHECK',
                        "targetInstances" : 'ERROR CHECK',
                        "blueGreenDeploymentConfiguration" : 'ERROR CHECK',
                        "loadBalancerInfo" : 'ERROR CHECK',
                        "fileExistsBehavior" : 'ERROR CHECK',
                        "computePlatform" : 'ERROR CHECK',
                        "relatedDeployments" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("codedeploy.list_deployments(),%s", othererr)
    results.append( { "DeploymentId": 'ERROR CHECK',
                      "applicationName" : 'ERROR CHECK',
                      "deploymentGroupName" : 'ERROR CHECK',
                      "deploymentConfigName" : 'ERROR CHECK',
                      "revision" : 'ERROR CHECK',
                      "status" : 'ERROR CHECK',
                      "errorInformation" : 'ERROR CHECK',
                      "createTime" : 'ERROR CHECK',
                      "completeTime" : 'ERROR CHECK',
                      "description" : 'ERROR CHECK',
                      "creator" : 'ERROR CHECK',
                      "updateOutdatedInstancesOnly" : 'ERROR CHECK',
                      "deploymentStyle" : 'ERROR CHECK',
                      "targetInstances" : 'ERROR CHECK',
                      "blueGreenDeploymentConfiguration" : 'ERROR CHECK',
                      "loadBalancerInfo" : 'ERROR CHECK',
                      "fileExistsBehavior" : 'ERROR CHECK',
                      "computePlatform" : 'ERROR CHECK',
                      "relatedDeployments" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_deployment(deploymentId):
  '''
    search codedeploy deployment
  '''
#   klogger_dat.debug('codedeploy deployment')

  try:
    result = None
    codedeploy=boto3.client('codedeploy')
    # klogger_dat.debug(applicationName)
    deployment = codedeploy.get_deployment(deploymentId=deploymentId)
    # klogger_dat.debug(deployment)
    if 200 == deployment["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(deployment["deploymentInfo"])
      if 'deploymentInfo' in deployment :
        result = deployment['deploymentInfo']
    else:
      klogger.error("call error : %d", deployment["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("codedeploy.get_deployment(),%s", othererr)
  finally:
    return result

def main(argv):

  list_applications() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
