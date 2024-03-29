####################################################################################################
# 
# Purpose   : get list servicediscovery info
# Source    : servicediscovery.py
# Usage     : python servicediscovery.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.20     first create
#  1.1      2023.05.17     add session handling logic
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/servicediscovery.html
#          
####################################################################################################
### This first line is for modules to work with Python 2 or 3
from __future__ import print_function
import os, sys, getopt
import json
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
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
else:
  # Module 실행으로 상대 경로 
  from .config import awsglobal
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
  from . import utils

def list_namespaces():
  '''
    search service discovery namespaces
  '''
  klogger_dat.debug('servicediscovery:cloudmap')
  try:
    results = [] 
    global SERVICEDISCOVERY_session

    SERVICEDISCOVERY_session = utils.get_session('servicediscovery')
    servicediscovery = SERVICEDISCOVERY_session
    namespaces = servicediscovery.list_namespaces()
    # klogger_dat.debug(namespaces)
    if 200 == namespaces["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(namespaces["Namespaces"])
      if 'Namespaces' in namespaces and  len(namespaces["Namespaces"]) > 0 :
        for namespace in namespaces["Namespaces"]:
          dnsproperties = list(namespace['DnsProperties']['HostedZoneId'] 
                               if 'DnsProperties' in namespace else ' ')
          httpproperties = list(namespace['HttpProperties']['HttpName']
                               if 'HttpProperties' in namespace else ' ')
          servicecount = namespace["ServiceCount"] if 'ServiceCount' in namespace else ''
  
          results.append( { "Id": namespace["Id"],
                            "Name" : namespace['Name'] if 'Name' in namespace else ' ',
                            "Type" : namespace['Type'] if 'Type' in namespace else ' ',
                            "Description" : namespace["Description"] if 'Description' in namespace else ' ',
                            "ServiceCount" : servicecount,
                            "DnsProperties" : dnsproperties,
                            "HttpProperties" : httpproperties,
                            "CreateDate" : namespace['CreateDate'].strftime("%Y-%m-%d %H:%M") if 'CreateDate' in namespace else ' ',
                           })
      else: # column list
        results.append( { "Id": ' ',
                          "Name" : ' ',
                          "Type" : ' ',
                          "Description" : ' ',
                          "ServiceCount" : ' ',
                          "DnsProperties" : ' ',
                          "HttpProperties" : ' ',
                          "CreateDate" : list(' '),
                         })
        
    else:
      klogger.error("call error : %d", namespaces["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "Id": 'ERROR CHECK',
                        "Name" : 'ERROR CHECK',
                        "Type" : 'ERROR CHECK',
                        "Description" : 'ERROR CHECK',
                        "ServiceCount" : 'ERROR CHECK',
                        "DnsProperties" : 'ERROR CHECK',
                        "HttpProperties" : 'ERROR CHECK',
                        "CreateDate" : list('ERROR CHECK'),
                       })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("route53.list_hosted_zones(),%s", othererr)
    results.append( { "Id": 'ERROR CHECK',
                      "Name" : 'ERROR CHECK',
                      "Type" : 'ERROR CHECK',
                      "Description" : 'ERROR CHECK',
                      "ServiceCount" : 'ERROR CHECK',
                      "DnsProperties" : 'ERROR CHECK',
                      "HttpProperties" : 'ERROR CHECK',
                      "CreateDate" : list('ERROR CHECK'),
                     })
  finally:
    return results

def main(argv):

  list_namespaces() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
