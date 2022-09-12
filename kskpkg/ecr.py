####################################################################################################
# 
# Purpose   : get list ecr info
# Source    : ecr.py
# Usage     : python ecr.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.30     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html
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

def describe_repositories():
  '''
    search ECR 
  '''
  klogger_dat.debug('ecr')
  try:
    results = [] 
    ecr=boto3.client('ecr')
    repositories = ecr.describe_repositories()
    # klogger_dat.debug(repositories)
    if 200 == repositories["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(repositories["repositories"])
      if 'repositories' in repositories and len(repositories["repositories"]) > 0 :
        for repository in repositories["repositories"]:
        #   klogger_dat.debug(repository)
          scanonpush = []
          if 'imageScanningConfiguration' in repository :
            if repository['imageScanningConfiguration']['scanOnPush'] :
              scanonpush.append('True')
            else :
              scanonpush.append('False')
          else:
            scanonpush.append('False')
          if 'encryptionConfiguration' in repository :
            encryptiontype = repository['encryptionConfiguration']['encryptionType']
            kmskey = repository['encryptionConfiguration']['kmsKey'] if 'KmsKey' in repository['encryptionConfiguration'] else ' '
          results.append( { "RepositoryName": repository['repositoryName'],
                            "RegistryId" : repository['registryId'],
                            "RepositoryArn": repository['repositoryArn'],
                            "RepositoryUri": repository['repositoryUri'],
                            "ImageTagMutability": repository['imageTagMutability'],
                            "ImageScanningscanOnPush": scanonpush,
                            "EncryptionType": encryptiontype,
                            "KmsKeyId": kmskey,
                            "KmsKeyAlias" : '',
                            "CreatedTime" : repository['createdAt'].strftime("%Y-%m-%d %H:%M"),
                          })
      else: # column list
        results.append( { "RepositoryName": ' ',
                          "RegistryId" : ' ',
                          "RepositoryArn": ' ',
                          "RepositoryUri": ' ',
                          "ImageTagMutability": ' ',
                          "ImageScanningscanOnPush": ' ',
                          "EncryptionType": ' ',
                          "KmsKeyId": ' ',
                          "KmsKeyAlias" : ' ',
                          "CreatedTime" : list(' '),
                        })
    else:
      klogger.error("call error : %d", repositories["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "RepositoryName": 'ERROR CHECK',
                        "RegistryId" : 'ERROR CHECK',
                        "RepositoryArn": 'ERROR CHECK',
                        "RepositoryUri": 'ERROR CHECK',
                        "ImageTagMutability": 'ERROR CHECK',
                        "ImageScanningscanOnPush": 'ERROR CHECK',
                        "EncryptionType": 'ERROR CHECK',
                        "KmsKeyId": 'ERROR CHECK',
                        "KmsKeyAlias" : 'ERROR CHECK',
                        "CreatedTime" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("ecr.describe_repositories(),%s", othererr)
    results.append( { "RepositoryName": 'ERROR CHECK',
                      "RegistryId" : 'ERROR CHECK',
                      "RepositoryArn": 'ERROR CHECK',
                      "RepositoryUri": 'ERROR CHECK',
                      "ImageTagMutability": 'ERROR CHECK',
                      "ImageScanningscanOnPush": 'ERROR CHECK',
                      "EncryptionType": 'ERROR CHECK',
                      "KmsKeyId": 'ERROR CHECK',
                      "KmsKeyAlias" : 'ERROR CHECK',
                      "CreatedTime" : list('ERROR CHECK'),
                    })
  finally:
    return results

def main(argv):

  describe_repositories() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
