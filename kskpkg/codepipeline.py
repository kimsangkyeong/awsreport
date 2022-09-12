####################################################################################################
# 
# Purpose   : get list codepipeline
# Source    : codepipeline.py
# Usage     : python codepipeline.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.09     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html
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

def list_pipelines():
  '''
    search codepipeline  
  '''
  klogger_dat.debug('codepipeline')

  try:
    results = [] 
    codepipeline=boto3.client('codepipeline')
    pipelines = codepipeline.list_pipelines()
    # klogger_dat.debug(pipelines)
    if 200 == pipelines["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(pipelines["pipelines"])
      if 'pipelines' in pipelines and len(pipelines["pipelines"]) > 0 :
        for pipeline in pipelines["pipelines"]:
        #   klogger_dat.debug(pipeline)
          pipelinename = pipeline['name']
          version = pipeline['version']
          created = pipeline['created'].strftime('%Y-%m-%d')
          updated = pipeline['updated'].strftime('%Y-%m-%d') if 'updated' in pipeline else ' '
          pipelineinfo = get_pipeline(pipeline['name'])
        #   klogger_dat.debug(pipelineinfo)
          artifactstore = []; artifactstores = []; stages = []; 
          if pipelineinfo != None :
            if 'pipeline' in pipelineinfo :
              rolearn = pipelineinfo['pipeline']['roleArn'] if 'roleArn' in pipelineinfo['pipeline'] else ' '
              artifactstore.append(pipelineinfo['pipeline']['artifactStore'] if 'artifactStore' in pipelineinfo['pipeline'] else ' ')
              artifactstores.append(pipelineinfo['pipeline']['artifactStores'] if 'artifactStores' in pipelineinfo['pipeline'] else ' ')
              if 'stages' in pipelineinfo['pipeline'] :
                for stage in pipelineinfo['pipeline']['stages'] :
                  stages.append(stage)
            if 'metadata' in pipelineinfo :
              pipelinearn = pipelineinfo['metadata']['pipelineArn'] if 'pipelineArn' in pipelineinfo['metadata'] else ' '
              
          # list count sync with space
          utils.ListSyncCountWithSpace(artifactstore, artifactstores, stages )

          results.append( { "PipelineName": pipelinename,
                            "pipelineArn" : pipelinearn, 
                            "version" : version,
                            "created" : created,
                            "updated" : updated,
                            "roleArn" : rolearn,
                            "artifactStore" : artifactstore,
                            "artifactStores" : artifactstores,
                            "stages" : stages,
                          })
      else: # column list
        results.append( { "PipelineName": ' ',
                          "pipelineArn" : ' ',
                          "version" : ' ',
                          "created" : ' ',
                          "updated" : ' ',
                          "roleArn" : ' ',
                          "artifactStore" : ' ',
                          "artifactStores" : ' ',
                          "stages" : list(' '),
                        })
    else:
      klogger.error("call error : %d", pipelines["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "PipelineName": 'ERROR CHECK',
                        "pipelineArn" : 'ERROR CHECK',
                        "version" : 'ERROR CHECK',
                        "created" : 'ERROR CHECK',
                        "updated" : 'ERROR CHECK',
                        "roleArn" : 'ERROR CHECK',
                        "artifactStore" : 'ERROR CHECK',
                        "artifactStores" : 'ERROR CHECK',
                        "stages" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("codepipeline.list_pipelines(),%s", othererr)
    results.append( { "PipelineName": 'ERROR CHECK',
                      "pipelineArn" : 'ERROR CHECK',
                      "version" : 'ERROR CHECK',
                      "created" : 'ERROR CHECK',
                      "updated" : 'ERROR CHECK',
                      "roleArn" : 'ERROR CHECK',
                      "artifactStore" : 'ERROR CHECK',
                      "artifactStores" : 'ERROR CHECK',
                      "stages" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_pipeline(pipelineName):
  '''
    search codepipeline pipeline
  '''
#   klogger_dat.debug('codepipeline pipeline')

  try:
    result = None
    codepipeline=boto3.client('codepipeline')
    # klogger_dat.debug(pipelineName)
    pipeline = codepipeline.get_pipeline(name=pipelineName)
    # klogger_dat.debug(pipeline)
    if 200 == pipeline["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(pipeline["pipeline"])
      result = pipeline
    else:
      klogger.error("call error : %d", pipeline["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("codepipeline.get_pipeline(),%s", othererr)
  finally:
    return result

def main(argv):

  list_pipelines() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
