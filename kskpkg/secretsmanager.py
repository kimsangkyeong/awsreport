####################################################################################################
# 
# Purpose   : get list secretsmanager info
# Source    : secretsmanager.py
# Usage     : python secretsmanager.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.06     first create
#  1.1      2023.05.17     add session handling logic
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html
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

def list_secrets():
  '''
    search secretsmanager 
  '''
  klogger_dat.debug('secretsmanager')
  try:
    results = [] 
    global SECRETMANAGER_session

    SECRETMANAGER_session = utils.get_session('secretsmanager')
    secretsmgr = SECRETMANAGER_session
    secrets = secretsmgr.list_secrets()
    # klogger_dat.debug(secrets)
    if 200 == secrets["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(secrets["SecretList"])
      if 'SecretList' in secrets and len(secrets["SecretList"]) > 0 :
        for secret in secrets["SecretList"]:
        #   klogger_dat.debug(secret)
          rotationenabled = 'False'
          if 'RotationEnabled' in secret :
            if secret['RotationEnabled'] :
              rotationenabled = 'True'
          lastchageddate = ''
          if 'LastChangedDate' in secret :
            lastchageddate = secret['LastChangedDate'].strftime("%Y-%m-%d")
          deleteddate = ''
          if 'DeletedDate' in secret :
            deleteddate = secret['DeletedDate'].strftime("%Y-%m-%d")
          # secret Tag중 Name 값
          tagname = ['Not Exist Name Tag']
          if 'Tags' in secret:
            for tag in secret['Tags']:
              if tag['Key'] == 'Name':
                tagname[0] = tag['Value']
                break

          results.append( { "Name": secret['Name'] if 'Name' in secret else '',
                            "TName" :tagname,
                            "ARN" : secret['ARN'] if 'ARN' in secret else '',
                            "Description": secret['Description'] if 'Description' in secret else '',
                            "KmsKeyId": secret['KmsKeyId'] if 'KmsKeyId' in secret else '',
                            "KmsKeyAlias" : '',
                            "RotationEnabled": rotationenabled,
                            "OwningService": secret['OwningService'] if 'OwningService' in secret else '',
                            "PrimaryRegion": secret['PrimaryRegion'] if 'PrimaryRegion' in secret else '',
                            "CreatedDate" : secret['CreatedDate'].strftime("%Y-%m-%d"),
                            "LastChangedDate" : lastchageddate,
                            "DeletedDate" : deleteddate,
                          })
      else: # column list
          results.append( { "Name": ' ',
                            "TName" : ' ',
                            "ARN" : ' ',
                            "Description": ' ',
                            "KmsKeyId": ' ',
                            "KmsKeyAlias" : ' ',
                            "RotationEnabled": ' ',
                            "OwningService": ' ',
                            "PrimaryRegion": ' ',
                            "CreatedDate" : ' ',
                            "LastChangedDate" : ' ',
                            "DeletedDate" : list(' '),
                          })
    else:
      klogger.error("call error : %d", secrets["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "Name": 'ERROR CHECK',
                        "TName" : 'ERROR CHECK',
                        "ARN" : 'ERROR CHECK',
                        "Description": 'ERROR CHECK',
                        "KmsKeyId": 'ERROR CHECK',
                        "KmsKeyAlias" : 'ERROR CHECK',
                        "RotationEnabled": 'ERROR CHECK',
                        "OwningService": 'ERROR CHECK',
                        "PrimaryRegion": 'ERROR CHECK',
                        "CreatedDate" : 'ERROR CHECK',
                        "LastChangedDate" : 'ERROR CHECK',
                        "DeletedDate" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("secretsmgr.list_secrets(),%s", othererr)
    results.append( { "Name": 'ERROR CHECK',
                      "TName" : 'ERROR CHECK',
                      "ARN" : 'ERROR CHECK',
                      "Description": 'ERROR CHECK',
                      "KmsKeyId": 'ERROR CHECK',
                      "KmsKeyAlias" : 'ERROR CHECK',
                      "RotationEnabled": 'ERROR CHECK',
                      "OwningService": 'ERROR CHECK',
                      "PrimaryRegion": 'ERROR CHECK',
                      "CreatedDate" : 'ERROR CHECK',
                      "LastChangedDate" : 'ERROR CHECK',
                      "DeletedDate" : list('ERROR CHECK'),
                    })
  finally:
    return results

def main(argv):

  list_secrets() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
