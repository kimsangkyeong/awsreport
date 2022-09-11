####################################################################################################
# 
# Purpose   : get list sns
# Source    : sns.py
# Usage     : python sns.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.11     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html
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


def list_topics():
  '''
    search sns
  '''
  klogger_dat.debug('sns topics')

  try:
    results = [] 
    sns=boto3.client('sns')
    topics = sns.list_topics()
    # klogger_dat.debug("%s", topics)
    if 200 == topics["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(topics["Topics"])
      if 'Topics' in topics and len(topics["Topics"]) > 0 :
        for topic in topics["Topics"]:
        #   klogger_dat.debug(topic)
          attributes = [];
          snsattributes = get_topic_attributes(topic['TopicArn'])
          if snsattributes != None :
            attributes.append(snsattributes)
          # list count sync with space
          utils.ListSyncCountWithSpace(attributes)

          results.append( { "TopicArn": topic['TopicArn'],
                            "Attributes" : attributes,
                          })
      else: # column list
        results.append( { "TopicArn": ' ',
                          "Attributes" : list(' '),
                        })
    else:
      klogger.error("call error : %d", topics["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "TopicArn": 'ERROR CHECK',
                        "Attributes" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("sns.list_topics(),%s", othererr)
    results.append( { "TopicArn": 'ERROR CHECK',
                      "Attributes" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_topic_attributes(TopicArn):
  '''
    search sns attributes
  '''
#   klogger_dat.debug('sns attributes')

  try:
    result = None
    sns=boto3.client('sns')
    # klogger.debug(f'{TopicArn}')
    attributes = sns.get_topic_attributes(TopicArn=TopicArn)
    # klogger.debug("%s", attributes)
    if 200 == attributes["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",attributes["Attributes"])
      if 'Attributes' in attributes :
        result = attributes['Attributes']
    else:
      klogger.error("call error : %d", attributes["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("sns.get_topic_attributes(),%s", othererr)
  finally:
    return result

def list_subscriptions():
  '''
    search sns subscriptions
  '''
  klogger_dat.debug('sns subscriptions')

  try:
    results = [] 
    sns=boto3.client('sns')
    subscriptions = sns.list_subscriptions()
    # klogger_dat.debug("%s", subscriptions)
    if 200 == subscriptions["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(subscriptions["Subscriptions"])
      if 'Subscriptions' in subscriptions and len(subscriptions["Subscriptions"]) > 0 :
        topicarns = []; subscriptionsarns = []; owners = []; protocols = []; endpoints = [];
        for subscription in subscriptions["Subscriptions"]:
        #   klogger_dat.debug(subscription)
          topicarns.append(subscription['TopicArn'] if 'TopicArn' in subscription else ' ')
          subscriptionsarns.append(subscription['SubscriptionArn'] if 'SubscriptionArn' in subscription else ' ')
          owners.append(subscription['Owner'] if 'Owner' in subscription else ' ')
          protocols.append(subscription['Protocol'] if 'Protocol' in subscription else ' ')
          endpoints.append(subscription['Endpoint'] if 'Endpoint' in subscription else ' ')
        # list count sync with space
        utils.ListSyncCountWithSpace(topicarns, subscriptionsarns, owners, protocols, endpoints)

        results.append( { "TopicArn" : topicarns,
                          "SubscriptionArn": subscriptionsarns,
                          "Owner" : owners,
                          "Protocol" : protocols,
                          "Endpoint" : endpoints,
                        })
      else: # column list
        results.append( { "TopicArn" : ' ',
                          "SubscriptionArn": ' ',
                          "Owner" : ' ',
                          "Protocol" : ' ',
                          "Endpoint" : list(' '),
                        })
    else:
      klogger.error("call error : %d", topics["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "TopicArn" : 'ERROR CHECK',
                        "SubscriptionArn": 'ERROR CHECK',
                        "Owner" : 'ERROR CHECK',
                        "Protocol" : 'ERROR CHECK',
                        "Endpoint" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("sns.list_topics(),%s", othererr)
    results.append( { "TopicArn" : 'ERROR CHECK',
                      "SubscriptionArn": 'ERROR CHECK',
                      "Owner" : 'ERROR CHECK',
                      "Protocol" : 'ERROR CHECK',
                      "Endpoint" : list('ERROR CHECK'),
                    })
  finally:
    return results
    
def main(argv):

  list_topics()

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
