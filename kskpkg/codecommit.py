####################################################################################################
# 
# Purpose   : get list codecommit
# Source    : codecommit.py
# Usage     : python codecommit.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.08     first create
#  1.1      2023.05.17     add session handling logic
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html
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

def list_repositories():
  '''
    search codecommit  
  '''
  klogger_dat.debug('codecommit')

  try:
    results = [] 
    global CODECOMMIT_session

    CODECOMMIT_session = utils.get_session('codecommit')
    codecommit = CODECOMMIT_session
    repositories = codecommit.list_repositories()
    # klogger_dat.debug(repositories)
    if 200 == repositories["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(repositories["repositories"])
      if 'repositories' in repositories and len(repositories["repositories"]) > 0 :
        for repository in repositories["repositories"]:
        #   klogger_dat.debug(repository)

          repoinfo = get_repository(repository['repositoryName'])
        #   klogger.debug(repoinfo)
          arn = [];
          if repoinfo != None :
            description = repoinfo['repositoryDescription'] if 'repositoryDescription' in repoinfo else ' '
            accountid = repoinfo['accountId'] if 'accountId' in repoinfo else ' '
            defaultbranch = repoinfo['defaultBranch'] if 'defaultBranch' in repoinfo else ' '
            lastmodifieddate = repoinfo['lastmodifieddate'].strftime('%Y-%m-%d') if 'lastmodifieddate' in repoinfo else ' '
            creationdate = repoinfo['creationDate'].strftime('%Y-%m-%d') if 'creationDate' in repoinfo else ' '
            cloneurlhttp = repoinfo['cloneUrlHttp'] if 'cloneUrlHttp' in repoinfo else ' '
            cloneurlssh = repoinfo['cloneUrlSsh'] if 'cloneUrlSsh' in repoinfo else ' '
            arn.append(repoinfo['Arn'] if 'Arn' in repoinfo else ' ')
          # list count sync with space
          utils.ListSyncCountWithSpace(arn)

          results.append( { "repositoryName": repository['repositoryName'],
                            "repositoryId" : repository['repositoryId'],
                            "repositoryDescription" : description,
                            "accountId" : accountid,
                            "defaultBranch" : defaultbranch,
                            "lastModifiedDate" : lastmodifieddate,
                            "creationDate" : creationdate,
                            "cloneUrlHttp" : cloneurlhttp,
                            "cloneUrlSsh" : cloneurlssh,
                            "Arn" : arn,
                          })
      else: # column list
        results.append( { "repositoryName": ' ',
                          "repositoryId" : ' ',
                          "repositoryDescription" : ' ',
                          "accountId" : ' ',
                          "defaultBranch" : ' ',
                          "lastModifiedDate" : ' ',
                          "creationDate" : ' ',
                          "cloneUrlHttp" : ' ',
                          "cloneUrlSsh" : ' ',
                          "Arn" : list(' '),
                        })
    else:
      klogger.error("call error : %d", repositories["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "repositoryName": 'ERROR CHECK',
                        "repositoryId" : 'ERROR CHECK',
                        "repositoryDescription" : 'ERROR CHECK',
                        "accountId" : 'ERROR CHECK',
                        "defaultBranch" : 'ERROR CHECK',
                        "lastModifiedDate" : 'ERROR CHECK',
                        "creationDate" : 'ERROR CHECK',
                        "cloneUrlHttp" : 'ERROR CHECK',
                        "cloneUrlSsh" : 'ERROR CHECK',
                        "Arn" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("codecommit.list_repositories(),%s", othererr)
    results.append( { "repositoryName": 'ERROR CHECK',
                      "repositoryId" : 'ERROR CHECK',
                      "repositoryDescription" : 'ERROR CHECK',
                      "accountId" : 'ERROR CHECK',
                      "defaultBranch" : 'ERROR CHECK',
                      "lastModifiedDate" : 'ERROR CHECK',
                      "creationDate" : 'ERROR CHECK',
                      "cloneUrlHttp" : 'ERROR CHECK',
                      "cloneUrlSsh" : 'ERROR CHECK',
                      "Arn" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_repository(repositoryName):
  '''
    search codecommit repository
  '''
#   klogger_dat.debug('codecommit repository')
  try:
    result = None 
    codecommit = CODECOMMIT_session
    repository = codecommit.get_repository(repositoryName=repositoryName)
    # klogger_dat.debug(repository)
    if 200 == repository["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(repository["repositoryMetadata"])
      result = repository["repositoryMetadata"]
    else:
      klogger.error("call error : %d", repository["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("codecommit.get_repository(),%s", othererr)
  finally:
    return result


def main(argv):

  list_repositories() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
