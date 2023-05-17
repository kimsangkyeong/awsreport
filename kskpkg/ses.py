####################################################################################################
# 
# Purpose   : get list ses
# Source    : ses.py
# Usage     : python ses.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.11     first create
#  1.1      2023.05.17     add session handling logic
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html
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


def list_identities():
  '''
    search ses
  '''
  klogger_dat.debug('ses')

  try:
    results = [] 
    global SES_session

    SES_session = utils.get_session('ses')
    ses = SES_session
    identities = ses.list_identities()
    # klogger_dat.debug("%s", identities)
    if 200 == identities["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(identities["Identities"])
      if 'Identities' in identities and len(identities["Identities"]) > 0 :
        for identity in identities["Identities"]:
        #   klogger_dat.debug(identity)
          policies = list_identity_policies(identity)
          # list count sync with space
          utils.ListSyncCountWithSpace(policies)

          results.append( { "SESId": identity,
                            "Policies" : policies,
                          })
      else: # column list
        results.append( { "SESId": ' ',
                          "Policies" : list(' '),
                        })
    else:
      klogger.error("call error : %d", identities["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "SESId": 'ERROR CHECK',
                        "Policies" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("ses.list_identities(),%s", othererr)
    results.append( { "SESId": 'ERROR CHECK',
                      "Policies" : list('ERROR CHECK'),
                    })
  finally:
    return results

def list_identity_policies(Identity):
  '''
    search ses id policies
  '''
#   klogger_dat.debug('ses id policy')

  try:
    results = []
    ses = SES_session
    # klogger.debug(f'{Identity}')
    policies = ses.list_identity_policies(Identity=Identity)
    # klogger.debug("%s", policies)
    if 200 == policies["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",policies["PolicyNames"])
      if 'PolicyNames' in policies :
        results = policies['PolicyNames']
    else:
      klogger.error("call error : %d", policies["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("ses.list_identity_policies(),%s", othererr)
  finally:
    return results

def main(argv):

  list_identities()

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
