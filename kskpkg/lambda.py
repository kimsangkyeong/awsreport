####################################################################################################
# 
# Purpose   : get list lambda
# Source    : lambda.py
# Usage     : python lambda.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.08     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html
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

def list_functions(filter):
  '''
    search lambda  
  '''
  if filter['Condition'] == 'Lambda@Edge' :
    klogger_dat.debug('lambda Edge')
  else:
    klogger_dat.debug('lambda')

  try:
    results = [] 
    lambdacli=boto3.client('lambda')
    if filter['Condition'] == 'Lambda@Edge' :
      functions = lambdacli.list_functions(MasterRegion=filter['Region'],FunctionVersion='ALL')
    else :
      functions = lambdacli.list_functions()
    # klogger_dat.debug(functions)
    if 200 == functions["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(functions["Functions"])
      if 'Functions' in functions and len(functions["Functions"]) > 0 :
        for function in functions["Functions"]:
          # klogger_dat.debug(function)
          vpcid = ' '; subnetids = []; securitygroups = []; variable = []; error = [];
          filesystemarns = []; filesystempaths = []; architectures = []; ephemeralstorage = [];
          if 'VpcConfig' in function :
            vpcid = function['VpcConfig']['VpcId']
            if 'SubnetIds' in function['VpcConfig'] :
              for subnet in function['VpcConfig']['SubnetIds']:
                subnetids.append(subnet)
            if 'SecurityGroupIds' in function['VpcConfig'] :
              for securitygroup in function['VpcConfig']['SecurityGroupIds']:
                securitygroups.append(securitygroup)
          if 'Environment' in function :
            variable.append(function['Environment']['Variables'] if 'Variables' in function['Environment'] else ' ')
            error.append(function['Environment']['Error'] if 'Error' in function['Environment'] else ' ')
          if 'FileSystemConfigs' in function :
            for config in function['FileSystemConfigs'] :
              filesystemarns.append(config['Arn'] if 'Arn' in config else ' ')
              filesystempaths.append(config['LocalMountPath'] if 'LocalMountPath' in config else ' ')
          if 'Architectures' in function :
            for item in function['Architectures'] :
              architectures.append(item)
          if 'EphemeralStorage' in function :
            ephemeralstorage.append(function['EphemeralStorage'])
            
          # list count sync with space
          utils.ListSyncCountWithSpace(subnetids, securitygroups, filesystemarns, filesystempaths, 
                                       architectures, variable, error, ephemeralstorage
                                      )

          results.append( { "FunctionName": function['FunctionName'],
                            "FunctionArn" : function['FunctionArn'],
                            "State" : function['State'] if 'State' in function else ' ',
                            "StateReason" :  function['StateReason'] if 'State' in function else ' ',
                            "Runtime" : function['Runtime'] if 'Runtime' in function else ' ',
                            "Role" : function['Role'] if 'Role' in function else ' ',
                            "Handler" : function['Handler'] if 'Handler' in function else ' ',
                            "CodeSize" : function['CodeSize'] if 'CodeSize' in function else ' ',
                            "Timeout" : function['Timeout'] if 'Timeout' in function else ' ',
                            "MemorySize" : function['MemorySize'] if 'MemorySize' in function else ' ',
                            "LastModified" : function['LastModified'] if 'LastModified' in function else ' ',
                            "VpcId" : vpcid,
                            "VpcTName" : ' ',
                            "SubnetId" : subnetids,
                            "SubnetTName" : ' ',
                            "SecurityGroup" : securitygroups,
                            "SecurityGroupName" : ' ',
                            "DeadLetterTargetArn" : function['DeadLetterTargetArn']['TargetArn'] if 'DeadLetterTargetArn' in function else ' ',
                            "Variables" : variable,
                            "Error" : error,
                            "KMSKeyArn" : function['KMSKeyArn'] if 'KMSKeyArn' in function else ' ',
                            "KeyAlias" : ' ',
                            "MasterArn" : function['MasterArn'] if 'MasterArn' in function else ' ',
                            "FileSystemArn": filesystemarns,
                            "FileSystemLocalMountPath" : filesystempaths,
                            "SigningProfileVersionArn": function['SigningProfileVersionArn'] if 'SigningProfileVersionArn' in function else ' ',
                            "Architectures" : architectures,
                            "EphemeralStorage" : ephemeralstorage,
                          })
      else: # column list
        results.append( { "FunctionName": ' ',
                          "FunctionArn" : ' ',
                          "State" : ' ',
                          "StateReason" : ' ',
                          "Runtime" : ' ',
                          "Role" : ' ',
                          "Handler" : ' ',
                          "CodeSize" : ' ',
                          "Timeout" : ' ',
                          "MemorySize" : ' ',
                          "LastModified" : ' ',
                          "VpcId" : ' ',
                          "VpcTName" : ' ',
                          "SubnetId" : ' ',
                          "SubnetTName" : ' ',
                          "SecurityGroup" : ' ',
                          "SecurityGroupName" : ' ',
                          "DeadLetterTargetArn" : ' ',
                          "Variables" : ' ',
                          "Error" : ' ',
                          "KMSKeyArn" : ' ',
                          "KeyAlias" : ' ',
                          "MasterArn" : ' ',
                          "FileSystemArn": ' ',
                          "FileSystemLocalMountPath" : ' ',
                          "SigningProfileVersionArn": ' ',
                          "Architectures" : ' ',
                          "EphemeralStorage" : list(' '),
                        })
    else:
      klogger.error("call error : %d", functions["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "FunctionName": 'ERROR CHECK',
                        "FunctionArn" : 'ERROR CHECK',
                        "State" : 'ERROR CHECK',
                        "StateReason" : 'ERROR CHECK',
                        "Runtime" : 'ERROR CHECK',
                        "Role" : 'ERROR CHECK',
                        "Handler" : 'ERROR CHECK',
                        "CodeSize" : 'ERROR CHECK',
                        "Timeout" : 'ERROR CHECK',
                        "MemorySize" : 'ERROR CHECK',
                        "LastModified" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : 'ERROR CHECK',
                        "SubnetId" : 'ERROR CHECK',
                        "SubnetTName" : 'ERROR CHECK',
                        "SecurityGroup" : 'ERROR CHECK',
                        "SecurityGroupName" : 'ERROR CHECK',
                        "DeadLetterTargetArn" : 'ERROR CHECK',
                        "Variables" : 'ERROR CHECK',
                        "Error" : 'ERROR CHECK',
                        "KMSKeyArn" : 'ERROR CHECK',
                        "KeyAlias" : 'ERROR CHECK',
                        "MasterArn" : 'ERROR CHECK',
                        "FileSystemArn": 'ERROR CHECK',
                        "FileSystemLocalMountPath" : 'ERROR CHECK',
                        "SigningProfileVersionArn": 'ERROR CHECK',
                        "Architectures" : 'ERROR CHECK',
                        "EphemeralStorage" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("lambdacli.list_functions(),%s", othererr)
    results.append( { "FunctionName": 'ERROR CHECK',
                      "FunctionArn" : 'ERROR CHECK',
                      "State" : 'ERROR CHECK',
                      "StateReason" : 'ERROR CHECK',
                      "Runtime" : 'ERROR CHECK',
                      "Role" : 'ERROR CHECK',
                      "Handler" : 'ERROR CHECK',
                      "CodeSize" : 'ERROR CHECK',
                      "Timeout" : 'ERROR CHECK',
                      "MemorySize" : 'ERROR CHECK',
                      "LastModified" : 'ERROR CHECK',
                      "VpcId" : 'ERROR CHECK',
                      "VpcTName" : 'ERROR CHECK',
                      "SubnetId" : 'ERROR CHECK',
                      "SubnetTName" : 'ERROR CHECK',
                      "SecurityGroup" : 'ERROR CHECK',
                      "SecurityGroupName" : 'ERROR CHECK',
                      "DeadLetterTargetArn" : 'ERROR CHECK',
                      "Variables" : 'ERROR CHECK',
                      "Error" : 'ERROR CHECK',
                      "KMSKeyArn" : 'ERROR CHECK',
                      "KeyAlias" : 'ERROR CHECK',
                      "MasterArn" : 'ERROR CHECK',
                      "FileSystemArn": 'ERROR CHECK',
                      "FileSystemLocalMountPath" : 'ERROR CHECK',
                      "SigningProfileVersionArn": 'ERROR CHECK',
                      "Architectures" : 'ERROR CHECK',
                      "EphemeralStorage" : list('ERROR CHECK'),
                    })
  finally:
    return results

def main(argv):

  list_functions({'Condition':'General','Region':''}) 
  list_functions({'Condition':'Lambda@Edge','Region':'ap-northeast-2'}) 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
