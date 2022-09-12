####################################################################################################
# 
# Purpose   : get list ssm info
# Source    : ssm.py
# Usage     : python ssm.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.06     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html
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

def describe_parameters():
  '''
    search ssm parameter store 
  '''
  klogger_dat.debug('ssm-parameter store')
  try:
    results = [] 
    ssm=boto3.client('ssm')
    parameters = ssm.describe_parameters()
    # klogger_dat.debug(parameters)
    if 200 == parameters["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(parameters["Parameters"])
      if 'Parameters' in parameters and len(parameters["Parameters"]) > 0 :
        for parameter in parameters["Parameters"]:
        #   klogger_dat.debug(parameter)
          name = []
          name.append(parameter['Name'])
          info = get_parameter(parameter['Name'])
          # klogger.debug(info)
          if info != None :
            value = info['Value']
          else:
            value = ''
          results.append( { "Name": name,
                            "Type" : parameter['Type'] if 'Type' in parameter else '',
                            "KeyId" : parameter['KeyId'] if 'KeyId' in parameter else '',
                            "Description": parameter['Description'] if 'Description' in parameter else '',
                            "Value" : value,
                            "AllowedPattern": parameter['AllowedPattern'] if 'AllowedPattern' in parameter else '',
                            "DataType" : parameter['DataType'] if 'DataType' in parameter else '',
                            "LastModifiedUser": parameter['LastModifiedUser'] if 'LastModifiedUser' in parameter else '',
                            "LastModifiedDate" : parameter['LastModifiedDate'].strftime("%Y-%m-%d") if 'LastModifiedDate' in parameter else '' ,
                          })
      else: # column list
        results.append( { "Name": ' ',
                          "Type" : ' ',
                          "KeyId" : ' ',
                          "Description": ' ',
                          "Value": ' ',
                          "AllowedPattern": ' ',
                          "DataType" : ' ',
                          "LastModifiedUser": ' ',
                          "LastModifiedDate" : list(' '),
                        })
    else:
      klogger.error("call error : %d", parameters["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "Name": 'ERROR CHECK',
                        "Type" : 'ERROR CHECK',
                        "KeyId" : 'ERROR CHECK',
                        "Description": 'ERROR CHECK',
                        "Value": 'ERROR CHECK',
                        "AllowedPattern": 'ERROR CHECK',
                        "DataType" : 'ERROR CHECK',
                        "LastModifiedUser": 'ERROR CHECK',
                        "LastModifiedDate" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("ssm.describe_parameters(),%s", othererr)
    results.append( { "Name": 'ERROR CHECK',
                      "Type" : 'ERROR CHECK',
                      "KeyId" : 'ERROR CHECK',
                      "Description": 'ERROR CHECK',
                      "Value": 'ERROR CHECK',
                      "AllowedPattern": 'ERROR CHECK',
                      "DataType" : 'ERROR CHECK',
                      "LastModifiedUser": 'ERROR CHECK',
                      "LastModifiedDate" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_parameter(name):
  '''
    search ssm parameter store info
  '''
  # klogger_dat.debug('ssm-parameter store info')
  try:
    result = None 
    ssm=boto3.client('ssm')
    parameter = ssm.get_parameter(Name=name)
    # klogger_dat.debug(parameter)
    if 200 == parameter["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(parameter["Parameter"])
      result = parameter["Parameter"]
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("ssm.get_parameter(),%s", othererr)
  finally:
    return result

def main(argv):

  describe_parameters() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
