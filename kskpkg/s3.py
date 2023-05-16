####################################################################################################
# 
# Purpose   : get list s3 info
# Source    : s3.py
# Usage     : python s3.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.20     first create
#  1.1      2023.05.16     add session handling logic
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
  profile_flag = awsglobal.profile_flag
  profile      = awsglobal.profile

#   import utils  오류
#  * global 변수를 공유하는 package 내의 모듈을 Main으로 실행할 때 import 하는 방법 확인 필요.

else:
  # Module 실행으로 상대 경로 
  from .config import awsglobal
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
  profile_flag = awsglobal.profile_flag
  profile      = awsglobal.profile
  from . import utils

def get_session(AWSService):
  if profile_flag :
    session = boto3.Session(profile_name=profile)
    return session.client(AWSService)
  else :
    return boto3.client(AWSService)

def list_buckets():
  '''
    search bucket list
  '''
  klogger_dat.debug('s3')
  try:
    results = [] 
    global S3_session

    S3_session = get_session('s3')
    s3 = S3_session
    buckets = s3.list_buckets()
    # klogger.debug(buckets)
    if 200 == buckets["ResponseMetadata"]["HTTPStatusCode"]:
      klogger.debug(buckets["Buckets"])
      if 'Buckets' in buckets and len(buckets["Buckets"]) > 0 :
        bucketnames = []; createdates = []; locations = []; blockacl = []; ignoreacl = [];
        blockpolicy = []; restrictpublic = []; bucketkeyenabled = []; kmsmasterkeyid = [];
        ssealgorithm = [];
        for bucket in buckets["Buckets"]:
          bucketnames.append(bucket['Name'] if 'Name' in bucket else ' ')
          locations.append(get_bucket_location(bucket['Name']) if 'Name' in bucket else ' ')
          createdates.append(bucket['CreationDate'].strftime("%Y-%m-%d %H:%M") 
                             if 'CreationDate' in bucket else ' ')
          accessblock = get_public_access_block(bucket['Name'])
          blockacl.append(accessblock['BlockPublicAcls'])
          ignoreacl.append(accessblock['IgnorePublicAcls'])
          blockpolicy.append(accessblock['BlockPublicPolicy'])
          restrictpublic.append(accessblock['RestrictPublicBuckets'])

          bucketkmss = get_bucket_encryption(bucket['Name'])
          for bucketkms in bucketkmss:
            bucketkeyenabled.append(bucketkms['BucketKeyEnabled'])
            kmsmasterkeyid.append(bucketkms['KMSMasterKeyID'])
            ssealgorithm.append(bucketkms['SSEAlgorithm'])
        # list count sync with space
        utils.ListSyncCountWithSpace(bucketnames, locations, blockacl, ignoreacl, blockpolicy, 
                    restrictpublic, ssealgorithm, bucketkeyenabled, kmsmasterkeyid, createdates)              
        results.append({ "Name": bucketnames,
                         "Location": locations,
                         "BlockPublicAcls" : blockacl,
                         "IgnorePublicAcls" : ignoreacl,
                         "BlockPublicPolicy" : blockpolicy,
                         "RestrictPublicBuckets" : restrictpublic,
                         "SSEAlgorithm" : ssealgorithm,
                         "BucketKeyEnabled" : bucketkeyenabled,
                         "KMSMasterKeyAlias" : ' ',
                         "KMSMasterKeyID" : kmsmasterkeyid,
                         "CreationDate" : createdates,
                       })
      else: # column list
        results.append({ "Name": ' ',
                         "Location" : ' ',
                         "BlockPublicAcls" : ' ',
                         "IgnorePublicAcls" : ' ',
                         "BlockPublicPolicy" : ' ',
                         "RestrictPublicBuckets" : ' ',
                         "SSEAlgorithm" : ' ',
                         "BucketKeyEnabled" : ' ',
                         "KMSMasterKeyAlias" : ' ',
                         "KMSMasterKeyID" : ' ',
                         "CreationDate" : list(' '),
                       })
    else:
      klogger.error("call error : %d", buckets["ResponseMetadata"]["HTTPStatusCode"])
      results.append({ "Name": 'ERROR CHECK',
                       "Location" : 'ERROR CHECK',
                       "BlockPublicAcls" : 'ERROR CHECK',
                       "IgnorePublicAcls" : 'ERROR CHECK',
                       "BlockPublicPolicy" : 'ERROR CHECK',
                       "RestrictPublicBuckets" : 'ERROR CHECK',
                       "SSEAlgorithm" : 'ERROR CHECK',
                       "BucketKeyEnabled" : 'ERROR CHECK',
                       "KMSMasterKeyAlias" : 'ERROR CHECK',
                       "KMSMasterKeyID" : 'ERROR CHECK',
                       "CreationDate" : list('ERROR CHECK'),
                     })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("s3.list_buckets(),%s", othererr)
    results.append({ "Name": 'ERROR CHECK',
                     "Location" : 'ERROR CHECK',
                     "BlockPublicAcls" : 'ERROR CHECK',
                     "IgnorePublicAcls" : 'ERROR CHECK',
                     "BlockPublicPolicy" : 'ERROR CHECK',
                     "RestrictPublicBuckets" : 'ERROR CHECK',
                     "SSEAlgorithm" : 'ERROR CHECK',
                     "BucketKeyEnabled" : 'ERROR CHECK',
                     "KMSMasterKeyAlias" : 'ERROR CHECK',
                     "KMSMasterKeyID" : 'ERROR CHECK',
                     "CreationDate" : list('ERROR CHECK'),
                   })
  finally:
    return results

def get_bucket_location(bucket):
  '''
    search bucket location
  '''
#   klogger_dat.debug('s3-location')
  try:
    result = 'Error Check' 
    s3 = S3_session
    location = s3.get_bucket_location(Bucket=bucket)
    klogger.debug(location)
    if 200 == location["ResponseMetadata"]["HTTPStatusCode"]:
      if type(location['LocationConstraint']) != type('str') :
        result = 'us-east-1'
      else :
        result = location['LocationConstraint']
    else:
      klogger.error("call error : %d", location["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("s3.get_bucket_location(),%s", othererr)
  finally:
    return result

def get_public_access_block(bucket):
  '''
    search bucket public access block
  '''
#   klogger_dat.debug('s3-public access block')
  try:
    result = {
        "BlockPublicAcls" : "Error Check",
        "IgnorePublicAcls" : "Error Check",
        "BlockPublicPolicy" : "Error Check",
        "RestrictPublicBuckets" : "Error Check"
      }
    s3 = S3_session
    klogger.debug(bucket)
    accessblock = s3.get_public_access_block(Bucket=bucket)
    # klogger.debug(accessblock)
    if 200 == accessblock["ResponseMetadata"]["HTTPStatusCode"]:
      result = {
        "BlockPublicAcls" : "True" if accessblock['PublicAccessBlockConfiguration']['BlockPublicAcls'] else "False",
        "IgnorePublicAcls" : "True" if accessblock['PublicAccessBlockConfiguration']['IgnorePublicAcls'] else "False",
        "BlockPublicPolicy" : "True" if accessblock['PublicAccessBlockConfiguration']['BlockPublicPolicy'] else "False",
        "RestrictPublicBuckets" : "True" if accessblock['PublicAccessBlockConfiguration']['RestrictPublicBuckets'] else "False"
      }
    else:
      klogger.error("call error : %d", accessblock["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    if str(othererr.args).count('NoSuchPublicAccessBlockConfiguration') > 0 :
      result = {
          "BlockPublicAcls" : "False",
          "IgnorePublicAcls" : "False",
          "BlockPublicPolicy" : "False",
          "RestrictPublicBuckets" : "False"
        }
    else:
      klogger.error("s3.get_public_access_block(),%s", othererr)
  finally:
    return result

def get_bucket_encryption(bucket):
  '''
    search bucket encryption
  '''
#   klogger_dat.debug('s3-encryption')
  try:
    results = []
    s3 = S3_session
    klogger_dat.debug("-------%s",bucket)
    encrypt = s3.get_bucket_encryption(Bucket=bucket)
    # klogger_dat.debug(encrypt)
    if 200 == encrypt["ResponseMetadata"]["HTTPStatusCode"]:
      if 'ServerSideEncryptionConfiguration' in encrypt :
        for rule in encrypt['ServerSideEncryptionConfiguration']['Rules']:
          if 'ApplyServerSideEncryptionByDefault' in rule :
            kmsmasterkeyid = rule['ApplyServerSideEncryptionByDefault']['KMSMasterKeyID'] if 'KMSMasterKeyID' in rule['ApplyServerSideEncryptionByDefault'] else ' '
            ssealgorithm = rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] if 'SSEAlgorithm' in rule['ApplyServerSideEncryptionByDefault'] else ' '
          else:
            kmsmasterkeyid = ' '
            ssealgorithm = ' '
          if 'BucketKeyEnabled' in rule :
            bucketkeyenabled = "True" if rule['BucketKeyEnabled'] else "False"
          else:
            bucketkeyenabled = "False"
          results.append({
              "SSEAlgorithm" : ssealgorithm,
              "BucketKeyEnabled" : bucketkeyenabled,
              "KMSMasterKeyID" : kmsmasterkeyid
            })
      else:
        results.append({
            "SSEAlgorithm" : " ",
            "BucketKeyEnabled" : "False",
            "KMSMasterKeyID" : " "
         })
    else:
      klogger.error("call error : %d", encrypt["ResponseMetadata"]["HTTPStatusCode"])
      results.append({
          "SSEAlgorithm" : "Error Check",
          "BucketKeyEnabled" : "Error Check",
          "KMSMasterKeyID" : "Error Check"
        })
    # klogger.debug(results)
  except Exception as othererr:
    if str(othererr.args).count('ServerSideEncryptionConfigurationNotFoundError') > 0 :
      # klogger.error("##################")
      results.append({
          "SSEAlgorithm" : " ",
          "BucketKeyEnabled" : "False",
          "KMSMasterKeyID" : " "
        })
    else:
      results.append({
          "SSEAlgorithm" : "Error Check",
          "BucketKeyEnabled" : "Error Check",
          "KMSMasterKeyID" : "Error Check"
        })
      klogger.error("s3.get_bucket_encryption(),%s", othererr)
  finally:
    return results

def main(argv):

  list_buckets() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
