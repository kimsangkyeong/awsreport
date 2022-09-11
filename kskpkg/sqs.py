####################################################################################################
# 
# Purpose   : get list sqs
# Source    : sqs.py
# Usage     : python sqs.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.11     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html
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


def list_queues(MaxResults):
  '''
    search sqs
  '''
  klogger_dat.debug('sqs')

  try:
    results = [] 
    sqs=boto3.client('sqs')
    queues = sqs.list_queues(MaxResults=MaxResults)
    # klogger_dat.debug("%s", queues)
    if 200 == queues["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug(queues["QueueUrls"])
      if 'QueueUrls' in queues and len(queues["QueueUrls"]) > 0 :
        for qurl in queues["QueueUrls"]:
        #   klogger_dat.debug(qurl)
          attributes = [];
          queattributes = get_queue_attributes(qurl, ['All'])
          if queattributes != None :
            attributes.append(queattributes)
          # list count sync with space
          utils.ListSyncCountWithSpace(attributes)

          results.append( { "QueueUrls": qurl,
                            "Attributes" : attributes,
                          })
      else: # column list
        results.append( { "QueueUrls": ' ',
                          "Attributes" : list(' '),
                        })
    else:
      klogger.error("call error : %d", queues["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "QueueUrls": 'ERROR CHECK',
                        "Attributes" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("sqs.list_queues(),%s", othererr)
    results.append( { "QueueUrls": 'ERROR CHECK',
                      "Attributes" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_queue_attributes(QueueUrl, AttributeNames):
  '''
    search queue attributes
  '''
#   klogger_dat.debug('queue attributes')

  try:
    result = None
    sqs=boto3.client('sqs')
    # klogger.debug(f'{QueueUrl}, {AttributeNames}')
    attributes = sqs.get_queue_attributes(QueueUrl=QueueUrl, AttributeNames=AttributeNames)
    # klogger.debug("%s", attributes)
    if 200 == attributes["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",attributes["Attributes"])
      if 'Attributes' in attributes :
        result = attributes['Attributes']
    else:
      klogger.error("call error : %d", attributes["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("sqs.get_queue_attributes(),%s", othererr)
  finally:
    return result

def main(argv):

  list_queues(1000) 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
