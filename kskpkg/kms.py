####################################################################################################
# 
# Purpose   : get list kms info
# Source    : kms.py
# Usage     : python kms.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.21     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html
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

def list_keys():
  '''
    search KMS 
  '''
  klogger_dat.debug('kms')
  try:
    results = [] 
    kms=boto3.client('kms')
    keys = kms.list_keys()
    # klogger_dat.debug(keys)
    if 200 == keys["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(keys["Keys"])
      if 'Keys' in keys and len(keys["Keys"]) > 0 :
        for key in keys["Keys"]:
        #   klogger_dat.debug(key)
          keyids = []
          keyids.append(key['KeyId'])

          results.append( { "KeyId": keyids,
                            "KeyAlias" : list_aliases(keyids[0]),
                            "KeyArn": key['KeyArn'],
                          })
      else: # column list
        results.append( { "KeyId": ' ',
                          "KeyAlias": ' ',
                          "KeyArn": list(' '),
                         })
    else:
      klogger.error("call error : %d", keys["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "KeyId": 'ERROR CHECK',
                        "KeyAlias": 'ERROR CHECK',
                        "KeyArn": list('ERROR CHECK'),
                       })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("kms.list_keys(),%s", othererr)
    results.append( { "KeyId": 'ERROR CHECK',
                      "KeyAlias": 'ERROR CHECK',
                      "KeyArn": list('ERROR CHECK'),
                     })
  finally:
    return results

def list_aliases(KeyId):
  '''
    search KMS alias
  '''
#   klogger_dat.debug('kms alias')
  try:
    result = 'ERROR CHECK' 
    kms=boto3.client('kms')
    alias = kms.list_aliases(KeyId=KeyId)
    # klogger_dat.debug(keys)
    if 200 == alias["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(alias["Aliases"])
      if len(alias["Aliases"]) > 0 :
        for alias in alias["Aliases"]:
        #   klogger_dat.debug(alias)
          if 'AliasName' in alias :
            result = alias['AliasName']
            break        
    else:
      klogger.error("call error : %d", alias["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("kms.list_aliases(),%s", othererr)
  finally:
    return result

def main(argv):

  list_keys() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
