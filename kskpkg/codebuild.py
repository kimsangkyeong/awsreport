####################################################################################################
# 
# Purpose   : get list codebuild
# Source    : codebuild.py
# Usage     : python codebuild.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.08     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html
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


def list_projects():
  '''
    search codebuild  
  '''
  klogger_dat.debug('codebuild')

  try:
    results = [] 
    codebuild=boto3.client('codebuild')
    projects = codebuild.list_projects()
    # klogger_dat.debug(projects)
    if 200 == projects["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(projects["projects"])
      if len(projects["projects"]) > 0 :
        for project in projects["projects"]:
        #   klogger_dat.debug(project)
          batchgetprjInput = []
          batchgetprjInput.append(project)
          prjinfos = batch_get_projects(batchgetprjInput)
        #   klogger.debug(prjinfos)
          getPrjInfo = {}
          for prjinfo in prjinfos :
            if project == prjinfo['name'] :
              getPrjInfo = prjinfo
              break
        #   klogger_dat.debug(getPrjInfo)

          secondarysources =[]; secondaryartifacts = []; vpcid = ''; subnets = []; sgroups = []; filesystemlocations = [];
          sources = []; artifacts = []; caches = []; environments = []; webhooks = []; buildbatchconfigs = [];
          sources.append(getPrjInfo['source'] if 'source' in getPrjInfo else ' ')
          artifacts.append(getPrjInfo['artifacts'] if 'artifacts' in getPrjInfo else ' ')
          caches.append(getPrjInfo['cache'] if 'cache' in getPrjInfo else ' ')
          environments.append(getPrjInfo['environment'] if 'environment' in getPrjInfo else ' ')
          webhooks.append(getPrjInfo['webhook'] if 'webhook' in getPrjInfo else ' ')
          buildbatchconfigs.append(getPrjInfo['buildBatchConfig'] if 'buildBatchConfig' in getPrjInfo else ' ')

          if 'secondarySources' in getPrjInfo :
            for secondsrc in getPrjInfo['secondarySources'] :
              secondarysources.append(secondsrc)
          if 'secondaryArtifacts' in getPrjInfo :
            for secondartifact in getPrjInfo['secondaryArtifacts'] :
              secondaryartifacts.append(secondartifact)
          if 'vpcConfig' in getPrjInfo :
            vpcid = getPrjInfo['vpcConfig']['vpcId'] if 'vpcId' in getPrjInfo['vpcConfig'] else ' '
            if 'subnets' in getPrjInfo['vpcConfig'] :
              for subnet in getPrjInfo['vpcConfig']['subnets'] :
                subnets.append(subnet)
            if 'securityGroupIds' in getPrjInfo['vpcConfig'] :
              for sgrpid in getPrjInfo['vpcConfig']['securityGroupIds'] :
                sgroups.append(sgrpid)
          if 'fileSystemLocations' in getPrjInfo :
            for filesystemloc in getPrjInfo['fileSystemLocations'] :
              filesystemlocations.append(filesystemloc)
          # list count sync with space
          utils.ListSyncCountWithSpace(secondarysources, secondaryartifacts, subnets, sgroups, filesystemlocations,
                                       sources, artifacts, caches, environments, webhooks, buildbatchconfigs
                                       )

          results.append( { "ProjectName": project,
                            "projectVisibility" : getPrjInfo['projectVisibility'] if 'projectVisibility' in getPrjInfo else ' ',
                            "publicProjectAlias" : getPrjInfo['publicProjectAlias'] if 'publicProjectAlias' in getPrjInfo else ' ',
                            "Arn" : getPrjInfo['arn'] if 'arn' in getPrjInfo else ' ',
                            "description" : getPrjInfo['description'] if 'description' in getPrjInfo else ' ',
                            "source" : sources,
                            "secondarySources" : secondarysources,
                            "artifacts" : artifacts,
                            "secondaryArtifacts" : secondaryartifacts,
                            "cache" : caches,
                            "environment" : environments,
                            "serviceRole" : getPrjInfo['serviceRole'] if 'serviceRole' in getPrjInfo else ' ',
                            "encryptionKey" : getPrjInfo['encryptionKey'] if 'encryptionKey' in getPrjInfo else ' ',
                            "KeyAlias" : ' ',
                            "created" : getPrjInfo['created'].strftime('%Y-%m-%d') if 'created' in getPrjInfo else ' ',
                            "lastModified" : getPrjInfo['lastModified'].strftime('%Y-%m-%d') if 'lastModified' in getPrjInfo else ' ',
                            "webhook" : webhooks,
                            "VpcId" : vpcid,
                            "VpcTName" : ' ',
                            "Subnets" : subnets,
                            "SubnetTName" : ' ',
                            "SecurityGroup" : sgroups,
                            "SGroupTName" : ' ',
                            "fileSystemLocations" : filesystemlocations,
                            "buildBatchConfig" : buildbatchconfigs,
                          })
      else: # column list
        results.append( { "ProjectName": ' ',
                          "projectVisibility" : ' ',
                          "publicProjectAlias" : ' ',
                          "Arn" : ' ',
                          "description" : ' ',
                          "source" : ' ',
                          "secondarySources" : ' ',
                          "artifacts" : ' ',
                          "secondaryArtifacts" : ' ',
                          "cache" : ' ',
                          "environment" : ' ',
                          "serviceRole" : ' ',
                          "encryptionKey" : ' ',
                          "KeyAlias" : ' ',
                          "created" : ' ',
                          "lastModified" : ' ',
                          "webhook" : ' ',
                          "VpcId" : ' ',
                          "VpcTName" : ' ',
                          "Subnets" : ' ',
                          "SubnetTName" : ' ',
                          "SecurityGroup" : ' ',
                          "SGroupTName" : ' ',
                          "fileSystemLocations" : ' ',
                          "buildBatchConfig" : list(' '),
                        })
    else:
      klogger.error("call error : %d", projects["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "ProjectName": 'ERROR CHECK',
                        "projectVisibility" : 'ERROR CHECK',
                        "publicProjectAlias" : 'ERROR CHECK',
                        "Arn" : 'ERROR CHECK',
                        "description" : 'ERROR CHECK',
                        "source" : 'ERROR CHECK',
                        "secondarySources" : 'ERROR CHECK',
                        "artifacts" : 'ERROR CHECK',
                        "secondaryArtifacts" : 'ERROR CHECK',
                        "cache" : 'ERROR CHECK',
                        "environment" : 'ERROR CHECK',
                        "serviceRole" : 'ERROR CHECK',
                        "encryptionKey" : 'ERROR CHECK',
                        "KeyAlias" : 'ERROR CHECK',
                        "created" : 'ERROR CHECK',
                        "lastModified" : 'ERROR CHECK',
                        "webhook" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : 'ERROR CHECK',
                        "Subnets" : 'ERROR CHECK',
                        "SubnetTName" : 'ERROR CHECK',
                        "SecurityGroup" : 'ERROR CHECK',
                        "SGroupTName" : 'ERROR CHECK',
                        "fileSystemLocations" : 'ERROR CHECK',
                        "buildBatchConfig" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("codebuild.list_projects(),%s", othererr)
    results.append( { "ProjectName": 'ERROR CHECK',
                      "projectVisibility" : 'ERROR CHECK',
                      "publicProjectAlias" : 'ERROR CHECK',
                      "Arn" : 'ERROR CHECK',
                      "description" : 'ERROR CHECK',
                      "source" : 'ERROR CHECK',
                      "secondarySources" : 'ERROR CHECK',
                      "artifacts" : 'ERROR CHECK',
                      "secondaryArtifacts" : 'ERROR CHECK',
                      "cache" : 'ERROR CHECK',
                      "environment" : 'ERROR CHECK',
                      "serviceRole" : 'ERROR CHECK',
                      "encryptionKey" : 'ERROR CHECK',
                      "KeyAlias" : 'ERROR CHECK',
                      "created" : 'ERROR CHECK',
                      "lastModified" : 'ERROR CHECK',
                      "webhook" : 'ERROR CHECK',
                      "VpcId" : 'ERROR CHECK',
                      "VpcTName" : 'ERROR CHECK',
                      "Subnets" : 'ERROR CHECK',
                      "SubnetTName" : 'ERROR CHECK',
                      "SecurityGroup" : 'ERROR CHECK',
                      "SGroupTName" : 'ERROR CHECK',
                      "fileSystemLocations" : 'ERROR CHECK',
                      "buildBatchConfig" : list('ERROR CHECK'),
                    })
  finally:
    return results

def batch_get_projects(project):
  '''
    search codebuild project
  '''
#   klogger_dat.debug('codebuild project')

  try:
    results = [] 
    codebuild=boto3.client('codebuild')
    # klogger_dat.debug(project)
    projects = codebuild.batch_get_projects(names=project)
    # klogger_dat.debug(projects)
    if 200 == projects["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(projects["projects"])
      if len(projects["projects"]) > 0 :
        # klogger_dat.debug(projects["projects"])
        # for project in projects['projects'] :
        #   results.append(project)
        results = projects['projects']
    else:
      klogger.error("call error : %d", projects["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("codebuild.batch_get_projects(),%s", othererr)
  finally:
    return results

def main(argv):

  list_projects() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
