####################################################################################################
# 
# Purpose : get list s3 info
# Source  : s3.py
# Usage   : python s3.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.20     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
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

def list_buckets():
  '''
    search bucket list
  '''
  klogger_dat.debug('s3')
  try:
    results = [] 
    s3=boto3.client('s3')
    buckets = s3.list_buckets()
    # klogger.debug(buckets)
    if 200 == buckets["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger.debug(buckets["Buckets"])
      if len(buckets["Buckets"]) > 0 :
        bucketnames = []; createdates = []; locations = [];
        for bucket in buckets["Buckets"]:
          bucketnames.append(bucket['Name'] if 'Name' in bucket else ' ')
          locations.append(get_bucket_location(bucket['Name']) if 'Name' in bucket else ' ')
          createdates.append(bucket['CreationDate'].strftime("%Y-%m-%d %H:%M") 
                             if 'CreationDate' in bucket else ' ')

        results.append({ "Name": bucketnames,
                         "Location": locations,
                         "CreationDate" : createdates,
                       })
      else: # column list
        results.append({ "Name": ' ',
                         "Location" : ' ',
                         "CreationDate" : list(' '),
                       })
    #   klogger.debug(results)
    else:
      klogger.error("call error : %d", buckets["ResponseMetadata"]["HTTPStatusCode"])
  except Exception as othererr:
    klogger.error("s3.list_buckets(),%s", othererr)
  return results

def get_bucket_location(bucket):
  '''
    search bucket location
  '''
#   klogger_dat.debug('s3-location')
  try:
    result = '' 
    s3=boto3.client('s3')
    location = s3.get_bucket_location(Bucket=bucket)
    # klogger.debug(location)
    if 200 == location["ResponseMetadata"]["HTTPStatusCode"]:
      if type(location['LocationConstraint']) != type('str') :
        result = 'us-east-1'
      else :
        result = location['LocationConstraint']
    #   klogger.debug(result)
    else:
      klogger.error("call error : %d", location["ResponseMetadata"]["HTTPStatusCode"])
  except Exception as othererr:
    klogger.error("s3.get_bucket_location(),%s", othererr)
  return result

def main(argv):

  list_buckets() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
