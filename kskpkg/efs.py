####################################################################################################
# 
# Purpose : get list EFS info
# Source  : efs.py
# Usage   : python efs.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.21     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/efs.html
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

def describe_file_systems():
  '''
    search EFS 
  '''
  klogger_dat.debug('efs')
  try:
    results = [] 
    efs=boto3.client('efs')
    filesystems = efs.describe_file_systems()
    # klogger_dat.debug(filesystems)
    if 200 == filesystems["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(filesystems["FileSystems"])
      if len(filesystems["FileSystems"]) > 0 :
        for filesystem in filesystems["FileSystems"]:
        #   klogger_dat.debug(filesystem)
          if 'SizeInBytes' in filesystem :
            sizevalue = filesystem['SizeInBytes']['Value'] if 'Value' in filesystem['SizeInBytes'] else ' '
            sizetimestamp = filesystem['SizeInBytes']['Timestamp'].strftime("%Y-%m-%d %H:%M") if 'Timestamp' in filesystem['SizeInBytes'] else ' '
            sizevalueinia = filesystem['SizeInBytes']['ValueInIA'] if 'ValueInIA' in filesystem['SizeInBytes'] else ' '
            sizevalueinstdard = filesystem['SizeInBytes']['ValueInStandard'] if 'ValueInStandard' in filesystem['SizeInBytes'] else ' '
          else:
            sizevalue = ' '
            sizetimestamp = ' '
            sizevalueinia = ' '
            sizevalueinstdard = ' '
          if 'Encrypted' in filesystem :
            encrypted = 'True' if filesystem['Encrypted'] else 'False'
          else:
            encrypted = 'False'
          # efs Tag중 Name 값 
          tagname = ['Not Exist Name Tag']
          if 'Tags' in filesystem:
            for tag in filesystem['Tags']:
              if tag['Key'] == 'Name':
                tagname[0] = tag['Value']
                break

          results.append( { "EFSName": filesystem['Name'] if 'Name' in filesystem else ' ',
                            "EFSTName": tagname,
                            "FileSystemId" : filesystem['FileSystemId'] if 'FileSystemId' in filesystem else ' ',
                            "FileSystemArn" : filesystem['FileSystemArn'] if 'FileSystemArn' in filesystem else ' ',
                            "AvailabilityZoneName" : filesystem['AvailabilityZoneName'] if 'AvailabilityZoneName' in filesystem else ' ',
                            "AvailabilityZoneId" : filesystem['AvailabilityZoneId'] if 'AvailabilityZoneId' in filesystem else ' ',
                            "NumberOfMountTargets" : filesystem['NumberOfMountTargets'] if 'NumberOfMountTargets' in filesystem else ' ',
                            "LifeCycleState" : filesystem['LifeCycleState'] if 'LifeCycleState' in filesystem else ' ',
                            "CreationTime" : filesystem['CreationTime'].strftime("%Y-%m-%d %H:%M") if 'CreationTime' in filesystem else ' ',
                            "Size_Value" : sizevalue,
                            "Size_Timestamp" : sizetimestamp,
                            "Size_ValueInIA" : sizevalueinia,
                            "Size_ValueInStandard" : sizevalueinstdard,
                            "Encrypted" : encrypted,
                            "KmsKeyAlias" : ' ',
                            "KmsKeyId" : filesystem['KmsKeyId'] if 'KmsKeyId' in filesystem else ' ',
                            "PerformanceMode" : filesystem['PerformanceMode'] if 'PerformanceMode' in filesystem else ' ',
                            "ThroughputMode" : filesystem['ThroughputMode'] if 'ThroughputMode' in filesystem else ' ',
                            "ProvisionedThroughputInMibps" : filesystem['ProvisionedThroughputInMibps'] if 'ProvisionedThroughputInMibps' in filesystem else ' ',
                           })
      else: # column list
        results.append( { "EFSName": ' ',
                          "EFSTName": ' ',
                          "FileSystemId" : ' ',
                          "FileSystemArn" : ' ',
                          "AvailabilityZoneName" : ' ',
                          "AvailabilityZoneId" : ' ',
                          "NumberOfMountTargets" : ' ',
                          "LifeCycleState" : ' ',
                          "CreationTime" : ' ',
                          "Size_Value" : ' ',
                          "Size_Timestamp" : ' ',
                          "Size_ValueInIA" : ' ',
                          "Size_ValueInStandard" : ' ',
                          "Encrypted" : ' ',
                          "KmsKeyAlias" : ' ',
                          "KmsKeyId" : ' ',
                          "PerformanceMode" : ' ',
                          "ThroughputMode" : ' ',
                          "ProvisionedThroughputInMibps" : list(' '),
                         })
    #   klogger.debug(results)
    else:
      klogger.error("call error : %d", filesystems["ResponseMetadata"]["HTTPStatusCode"])
  except Exception as othererr:
    klogger.error("efs.describe_file_systems(),%s", othererr)
  return results

def main(argv):

  describe_file_systems() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
