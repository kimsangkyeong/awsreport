####################################################################################################
# 
# Purpose : get list acm info
# Source  : acm.py
# Usage   : python acm.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.20     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/acm.html
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

def list_certificates():
  '''
    search certicate
  '''
  klogger_dat.debug('acm')
  try:
    results = [] 
    acm=boto3.client('acm')
    certlists = acm.list_certificates()
    # klogger.debug(certlists)
    if 200 == certlists["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger.debug(certlists["CertificateSummaryList"])
      domainnames =[]; certarns = [];
      if len(certlists["CertificateSummaryList"]) > 0 :
        for certificate in certlists["CertificateSummaryList"]:
          domainnames.append(certificate['DomainName'] if 'DomainName' in certificate else ' ')
          certarns.append(certificate['CertificateArn'] if 'CertificateArn' in certificate else ' ')

        results.append({ "DomainName": domainnames,
                          "CertificateArn" : certarns,
                       })
      else: # column list
        results.append({ "DomainName": ' ',
                         "CertificateArn" : list(' '),
                       })
    else:
      klogger.error("call error : %d", certlists["ResponseMetadata"]["HTTPStatusCode"])
      results.append({ "DomainName": 'ERROR CHECK',
                       "CertificateArn" : list('ERROR CHECK'),
                     })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("acm.list_certificates(),%s", othererr)
    results.append({ "DomainName": 'ERROR CHECK',
                     "CertificateArn" : list('ERROR CHECK'),
                   })
  finally:
    return results

def main(argv):

  list_certificates() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
