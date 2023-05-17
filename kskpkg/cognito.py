####################################################################################################
# 
# Purpose   : get list cognito
# Source    : cognito.py
# Usage     : python cognito.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.11     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito.html
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


def list_identity_pools(MaxResults):
  '''
    search cognito-identity pools
  '''
  klogger_dat.debug('cognito-identity pools')

  try:
    results = [] 
    global COGNITOID_session

    COGNITOID_session = utils.get_session('cognito-identity')
    cognitoid = COGNITOID_session
    pools = cognitoid.list_identity_pools(MaxResults=MaxResults)
    # klogger_dat.debug("%s", pools)
    if 200 == pools["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug(pools["IdentityPools"])
      if 'IdentityPools' in pools and len(pools["IdentityPools"]) > 0 :
        for idpool in pools["IdentityPools"]:
          # klogger_dat.debug(idpool)
          identities = list_identities(idpool['IdentityPoolId'], 60, True)
          # klogger.debug(identities)
          ids = []; logins = []; createdates = []; lstmoddates = []; roles = []; rolemappings = [];
          for identity in identities :
            ids.append(identity['IdentityId'] if 'IdentityId' in identity else ' ')
            logins.append(identity['Logins'] if 'Logins' in identity else ' ')
            createdates.append(identity['CreationDate'].strftime('%Y-%m-%d') if 'CreationDate' in identity else ' ')
            lstmoddates.append(identity['LastModifiedDate'].strftime('%Y-%m-%d') if 'LastModifiedDate' in identity else ' ')

          role, rolemapping = get_identity_pool_roles(idpool['IdentityPoolId'])
          roles.append(role)
          rolemappings.append(rolemapping)
          # list count sync with space
          utils.ListSyncCountWithSpace(ids, logins, createdates, lstmoddates, roles, rolemappings)

          results.append( { "IdentityPoolId": idpool['IdentityPoolId'],
                            "IdentityPoolName" : idpool['IdentityPoolName'] if 'IdentityPoolName' in idpool else ' ',
                            "IdentityId" : ids,
                            "Logins" : logins,
                            "Roles" : roles,
                            "RoleMappings" : rolemappings,
                            "CreationDate" : createdates,
                            "LastModifiedDate" : lstmoddates,
                          })
      else: # column list
        results.append( { "IdentityPoolId": ' ',
                          "IdentityPoolName" : ' ',
                          "IdentityId" : ' ',
                          "Logins" : ' ',
                          "Roles" : ' ',
                          "RoleMappings" : ' ',
                          "CreationDate" : ' ',
                          "LastModifiedDate" : list(' '),
                        })
    else:
      klogger.error("call error : %d", pools["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "IdentityPoolId": 'ERROR CHECK',
                        "IdentityPoolName" : 'ERROR CHECK',
                        "IdentityId" : 'ERROR CHECK',
                        "Logins" : 'ERROR CHECK',
                        "Roles" : 'ERROR CHECK',
                        "RoleMappings" : 'ERROR CHECK',
                        "CreationDate" : 'ERROR CHECK',
                        "LastModifiedDate" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("cognito.list_identity_pools(),%s", othererr)
    results.append( { "IdentityPoolId": 'ERROR CHECK',
                      "IdentityPoolName" : 'ERROR CHECK',
                      "IdentityId" : 'ERROR CHECK',
                      "Logins" : 'ERROR CHECK',
                      "Roles" : 'ERROR CHECK',
                      "RoleMappings" : 'ERROR CHECK',
                      "CreationDate" : 'ERROR CHECK',
                      "LastModifiedDate" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_identity_pool_roles(IdentityPoolId):
  '''
    search cognito id pool roles
  '''
#   klogger_dat.debug('cognito-identity pools roles')

  try:
    result1 = {}; result2 = {} 
    cognitoid = COGNITOID_session
    # klogger.debug("%s", IdentityPoolId)
    roles = cognitoid.get_identity_pool_roles(IdentityPoolId=IdentityPoolId)
    # klogger.debug("%s", roles)
    if 200 == roles["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",roles["Roles"])
      if 'Roles' in roles :
        result1 = roles['Roles']
      if 'RoleMappings' in roles :
        result2 = roles['RoleMappings']
    else:
      klogger.error("call error : %d", roles["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result1, result2)
  except Exception as othererr:
    klogger.error("cognito.get_identity_pool_roles(),%s", othererr)
  finally:
    return result1, result2

def list_identities(IdentityPoolId, MaxResults, HideDisabled):
  '''
    search cognito id pool id list
  '''
#   klogger_dat.debug('cognito-identity pools id list')

  try:
    results = [] 
    cognitoid = COGNITOID_session
    # klogger.debug("%s, %d, %s", IdentityPoolId, MaxResults, HideDisabled)
    ids = cognitoid.list_identities(IdentityPoolId=IdentityPoolId, MaxResults=MaxResults, HideDisabled=HideDisabled)
    # klogger.debug(ids)
    if 200 == ids["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug(ids["Identities"])
      if 'Identities' in ids and len(ids["Identities"]) > 0 :
        results = ids['Identities']
    else:
      klogger.error("call error : %d", ids["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("cognito.list_identities(),%s", othererr)
  finally:
    return results

def list_user_pools(MaxResults):
  '''
    search cognito-idp user pools
  '''
  klogger_dat.debug('cognito-idp user pools')

  try:
    results = [] 
    global COGNITOIDP_session
    
    COGNITOIDP_session = utils.get_session('cognito-idp')
    cognitoidp = COGNITOIDP_session
    pools = cognitoidp.list_user_pools(MaxResults=MaxResults)
    # klogger.debug(pools)
    if 200 == pools["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(pools["UserPools"])
      if 'UserPools' in pools and len(pools["UserPools"]) > 0 :
        for userpool in pools["UserPools"]:
          # # klogger_dat.debug(userpool)
          lambdacfgs = [];
          lambdacfgs.append(userpool['LambdaConfig'] if 'LambdaConfig' in userpool else ' ')
          # list count sync with space
          utils.ListSyncCountWithSpace(lambdacfgs)

          results.append( { "UserPoolId": userpool['Id'],
                            "UserPoolName" : userpool['Name'] if 'Name' in userpool else ' ',
                            "Status" : userpool['Status'] if 'Status' in userpool else ' ',
                            "LambdaConfig" : lambdacfgs,
                            "CreationDate" : userpool['CreationDate'].strftime('%Y-%m-%d') if 'CreationDate' in userpool else ' ',
                            "LastModifiedDate" : userpool['LastModifiedDate'].strftime('%Y-%m-%d') if 'LastModifiedDate' in userpool else ' ',
                          })
      else: # column list
        results.append( { "UserPoolId": ' ',
                          "UserPoolName" : ' ',
                          "Status" : ' ',
                          "LambdaConfig" : ' ',
                          "CreationDate" : ' ',
                          "LastModifiedDate" : list(' '),
                        })
    else:
      klogger.error("call error : %d", pools["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "UserPoolId": 'ERROR CHECK',
                        "UserPoolName" : 'ERROR CHECK',
                        "Status" : 'ERROR CHECK',
                        "LambdaConfig" : 'ERROR CHECK',
                        "CreationDate" : 'ERROR CHECK',
                        "LastModifiedDate" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("cognito.list_user_pools(),%s", othererr)
    results.append( { "UserPoolId": 'ERROR CHECK',
                      "UserPoolName" : 'ERROR CHECK',
                      "Status" : 'ERROR CHECK',
                      "LambdaConfig" : 'ERROR CHECK',
                      "CreationDate" : 'ERROR CHECK',
                      "LastModifiedDate" : list('ERROR CHECK'),
                    })
  finally:
    return results

def main(argv):

  list_identity_pools(60) 
  list_user_pools(60)

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
