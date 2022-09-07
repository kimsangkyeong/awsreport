####################################################################################################
# 
# Purpose   : get list rds info
# Source    : rds.py
# Usage     : python rds.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.22     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html
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

def describe_db_clusters():
  '''
    search RDS Clusters 
  '''
  klogger_dat.debug('rds')
  try:
    results = [] 
    rds=boto3.client('rds')
    dbclusters = rds.describe_db_clusters()
    # klogger_dat.debug(dbclusters)
    if 200 == dbclusters["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(dbclusters["DBClusters"])
      if len(dbclusters["DBClusters"]) > 0 :
        for dbcluster in dbclusters["DBClusters"]:
        #   klogger_dat.debug(dbcluster)
          availablezones = []; multiaz = 'FALSE'; dbclusteroptgname = []; dbclusteroptgstatus = [];
          vsgid = []; vsgstatus = []; associaterole = []; iamauthenabled = 'FALSE'; delprotection = 'FALSE';
          pubaccessible = 'FALSE'; autoupgrade = 'FALSE'; perfinenabled = 'FALSE'; 
          if 'AvailabilityZones' in dbcluster :
            for availablezone in dbcluster['AvailabilityZones']:
              availablezones.append(availablezone)
          if 'MultiAZ' in dbcluster:
            if dbcluster['MultiAZ']:
              multiaz = 'TRUE'
          if 'DBClusterOptionGroupMemberships' in dbcluster:
            for item in dbcluster['DBClusterOptionGroupMemberships']:
              dbclusteroptgname.append(item['DBClusterOptionGroupName'] if 'DBClusterOptionGroupName' in item else ' ')
              dbclusteroptgstatus.append(item['Status'] if 'Status' in item else ' ')
          if 'VpcSecurityGroups' in dbcluster:
            for vsg in dbcluster['VpcSecurityGroups']:
              vsgid.append(vsg['VpcSecurityGroupId'] if 'VpcSecurityGroupId' in vsg else ' ')
              vsgstatus.append(vsg['Status'] if 'Status' in vsg else ' ')
          if 'AssociatedRoles' in dbcluster:
            for assrole in dbcluster['AssociatedRoles']:
              associaterole.apend(assrole)
          if 'IAMDatabaseAuthenticationEnabled' in dbcluster:
            if dbcluster['IAMDatabaseAuthenticationEnabled']:
              iamauthenabled = 'TRUE'
          if 'DeletionProtection' in dbcluster:
            if dbcluster['DeletionProtection']:
              delprotection = 'TRUE'
          if 'PubliclyAccessible' in dbcluster:
            if dbcluster['PubliclyAccessible']:
              pubaccessible = 'TRUE'
          if 'AutoMinorVersionUpgrade' in dbcluster:
            if dbcluster['AutoMinorVersionUpgrade']:
              autoupgrade = 'TRUE'
          if 'PerformanceInsightsEnabled' in dbcluster:
            if dbcluster['PerformanceInsightsEnabled']:
              perfinenabled = 'TRUE'
          # rds Tag중 Name 값 
          tagname = 'Not Exist Name Tag'
          if 'TagList' in dbcluster:
            for tag in dbcluster['TagList']:
              if tag['Key'] == 'Name':
                tagname = tag['Value']
                break
          # list count sync with space
          utils.ListSyncCountWithSpace(availablezones, dbclusteroptgname, dbclusteroptgstatus,
                                       vsgid, vsgstatus, associaterole)
          
          results.append( { "DBClusterIdentifier" : dbcluster['DBClusterIdentifier'] if 'DBClusterIdentifier' in dbcluster else ' ',
                            "DBClusterTName": tagname,
                            "DatabaseName": dbcluster['DatabaseName'] if 'DatabaseName' in dbcluster else ' ',
                            "CharacterSetName": dbcluster['CharacterSetName'] if 'CharacterSetName' in dbcluster else ' ',
                            "AvailabilityZones" : availablezones,
                            "Status" : dbcluster['Status'] if 'Status' in dbcluster else ' ',
                            "DBClusterParameterGroup" : dbcluster['DBClusterParameterGroup'] if 'DBClusterParameterGroup' in dbcluster else ' ',
                            "DBSubnetGroup" : dbcluster['DBSubnetGroup'] if 'DBSubnetGroup' in dbcluster else ' ',
                            "BackupRetentionPeriod" : dbcluster['BackupRetentionPeriod'] if 'BackupRetentionPeriod' in dbcluster else ' ',
                            "AllocatedStorage" : dbcluster['AllocatedStorage'] if 'AllocatedStorage' in dbcluster else ' ',
                            "MultiAZ" : multiaz,
                            "Engine" : dbcluster['Engine'] if 'Engine' in dbcluster else ' ',
                            "EngineVersion" : dbcluster['EngineVersion'] if 'EngineVersion' in dbcluster else ' ',
                            "Port" : dbcluster['Port'] if 'Port' in dbcluster else ' ',
                            "Endpoint" : dbcluster['Endpoint'] if 'Endpoint' in dbcluster else ' ',
                            "ReaderEndpoint" : dbcluster['ReaderEndpoint'] if 'ReaderEndpoint' in dbcluster else ' ',
                            "MasterUsername" : dbcluster['MasterUsername'] if 'MasterUsername' in dbcluster else ' ',
                            "DBClusterOptionGroupName" : dbclusteroptgname,
                            "DBClusterOptionGroupStatus" : dbclusteroptgstatus,
                            "VpcSecurityGroupName" : ' ',
                            "VpcSecurityGroupId" : vsgid,
                            "VpcSecurityGroupStatus" : vsgstatus,
                            "KmsKeyAlias" : ' ',
                            "KmsKeyId" : dbcluster['KmsKeyId'] if 'KmsKeyId' in dbcluster else ' ',
                            "AssociatedRole" : associaterole,
                            "IAMDatabaseAuthenticationEnabled" : iamauthenabled,
                            "ClusterCreateTime" : dbcluster['ClusterCreateTime'].strftime("%Y-%m-%d %H:%M") if 'ClusterCreateTime' in dbcluster else ' ',
                            "Capacity" : dbcluster['Capacity'] if 'Capacity' in dbcluster else ' ',
                            "EngineMode" : dbcluster['EngineMode'] if 'EngineMode' in dbcluster else ' ',
                            "DeletionProtection" : delprotection,
                            "ActivityStreamMode" : dbcluster['ActivityStreamMode'] if 'ActivityStreamMode' in dbcluster else ' ',
                            "ActivityStreamStatus" : dbcluster['ActivityStreamStatus'] if 'ActivityStreamStatus' in dbcluster else ' ',
                            "ActivityStreamKmsKeyAlias" : ' ',
                            "ActivityStreamKmsKeyId" : dbcluster['ActivityStreamKmsKeyId'] if 'ActivityStreamKmsKeyId' in dbcluster else ' ',
                            "ActivityStreamKinesisStreamName" : dbcluster['ActivityStreamKinesisStreamName'] if 'ActivityStreamKinesisStreamName' in dbcluster else ' ',
                            "DBClusterInstanceClass" : dbcluster['DBClusterInstanceClass'] if 'DBClusterInstanceClass' in dbcluster else ' ',
                            "StorageType" : dbcluster['StorageType'] if 'StorageType' in dbcluster else ' ',
                            "Iops" : dbcluster['Iops'] if 'Iops' in dbcluster else ' ',
                            "PubliclyAccessible" : pubaccessible,
                            "AutoMinorVersionUpgrade" : autoupgrade,
                            "PerformanceInsightsEnabled" : perfinenabled,
                            "PerformanceInsightsKMSKeyAlias" : ' ',
                            "PerformanceInsightsKMSKeyId" : dbcluster['PerformanceInsightsKMSKeyId'] if 'PerformanceInsightsKMSKeyId' in dbcluster else ' ',
                            "PerformanceInsightsRetentionPeriod" : dbcluster['PerformanceInsightsRetentionPeriod'] if 'PerformanceInsightsRetentionPeriod' in dbcluster else ' ',
                            "ServerlessV2ScalingConfiguration" : dbcluster['ServerlessV2ScalingConfiguration'] if 'ServerlessV2ScalingConfiguration' in dbcluster else ' ',
                            "NetworkType" : dbcluster['NetworkType'] if 'NetworkType' in dbcluster else ' ',
                           })
      else: # column list
        results.append( { "DBClusterIdentifier" : ' ',
                          "DBClusterTName": ' ',
                          "DatabaseName": ' ',
                          "CharacterSetName": ' ',
                          "AvailabilityZones" : ' ',
                          "Status" : ' ',
                          "DBClusterParameterGroup" : ' ',
                          "DBSubnetGroup" : ' ',
                          "BackupRetentionPeriod" : ' ',
                          "AllocatedStorage" : ' ',
                          "MultiAZ" : ' ',
                          "Engine" : ' ',
                          "EngineVersion" : ' ',
                          "Port" : ' ',
                          "Endpoint" : ' ',
                          "ReaderEndpoint" : ' ',
                          "MasterUsername" : ' ',
                          "DBClusterOptionGroupName" : ' ',
                          "DBClusterOptionGroupStatus" : ' ',
                          "VpcSecurityGroupName" : ' ',
                          "VpcSecurityGroupId" : ' ',
                          "VpcSecurityGroupStatus" : ' ',
                          "KmsKeyAlias" : ' ',
                          "KmsKeyId" : ' ',
                          "AssociatedRole" : ' ',
                          "IAMDatabaseAuthenticationEnabled" : ' ',
                          "ClusterCreateTime" : ' ',
                          "Capacity" : ' ',
                          "EngineMode" : ' ',
                          "DeletionProtection" : ' ',
                          "ActivityStreamMode" : ' ',
                          "ActivityStreamStatus" : ' ',
                          "ActivityStreamKmsKeyAlias" : ' ',
                          "ActivityStreamKmsKeyId" : ' ',
                          "ActivityStreamKinesisStreamName" : ' ',
                          "DBClusterInstanceClass" : ' ',
                          "StorageType" : ' ',
                          "Iops" : ' ',
                          "PubliclyAccessible" : ' ',
                          "AutoMinorVersionUpgrade" : ' ',
                          "PerformanceInsightsEnabled" : ' ',
                          "PerformanceInsightsKMSKeyAlias" : ' ',
                          "PerformanceInsightsKMSKeyId" : ' ',
                          "PerformanceInsightsRetentionPeriod" : ' ',
                          "ServerlessV2ScalingConfiguration" : ' ',
                          "NetworkType" : list(' '),
                         })
    else:
      klogger.error("call error : %d", dbclusters["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "DBClusterIdentifier" : 'ERROR CHECK',
                        "DBClusterTName": 'ERROR CHECK',
                        "DatabaseName": 'ERROR CHECK',
                        "CharacterSetName": 'ERROR CHECK',
                        "AvailabilityZones" : 'ERROR CHECK',
                        "Status" : 'ERROR CHECK',
                        "DBClusterParameterGroup" : 'ERROR CHECK',
                        "DBSubnetGroup" : 'ERROR CHECK',
                        "BackupRetentionPeriod" : 'ERROR CHECK',
                        "AllocatedStorage" : 'ERROR CHECK',
                        "MultiAZ" : 'ERROR CHECK',
                        "Engine" : 'ERROR CHECK',
                        "EngineVersion" : 'ERROR CHECK',
                        "Port" : 'ERROR CHECK',
                        "Endpoint" : 'ERROR CHECK',
                        "ReaderEndpoint" : 'ERROR CHECK',
                        "MasterUsername" : 'ERROR CHECK',
                        "DBClusterOptionGroupName" : 'ERROR CHECK',
                        "DBClusterOptionGroupStatus" : 'ERROR CHECK',
                        "VpcSecurityGroupName" : 'ERROR CHECK',
                        "VpcSecurityGroupId" : 'ERROR CHECK',
                        "VpcSecurityGroupStatus" : 'ERROR CHECK',
                        "KmsKeyAlias" : 'ERROR CHECK',
                        "KmsKeyId" : 'ERROR CHECK',
                        "AssociatedRole" : 'ERROR CHECK',
                        "IAMDatabaseAuthenticationEnabled" : 'ERROR CHECK',
                        "ClusterCreateTime" : 'ERROR CHECK',
                        "Capacity" : 'ERROR CHECK',
                        "EngineMode" : 'ERROR CHECK',
                        "DeletionProtection" : 'ERROR CHECK',
                        "ActivityStreamMode" : 'ERROR CHECK',
                        "ActivityStreamStatus" : 'ERROR CHECK',
                        "ActivityStreamKmsKeyAlias" : 'ERROR CHECK',
                        "ActivityStreamKmsKeyId" : 'ERROR CHECK',
                        "ActivityStreamKinesisStreamName" : 'ERROR CHECK',
                        "DBClusterInstanceClass" : 'ERROR CHECK',
                        "StorageType" : 'ERROR CHECK',
                        "Iops" : 'ERROR CHECK',
                        "PubliclyAccessible" : 'ERROR CHECK',
                        "AutoMinorVersionUpgrade" : 'ERROR CHECK',
                        "PerformanceInsightsEnabled" : 'ERROR CHECK',
                        "PerformanceInsightsKMSKeyAlias" : 'ERROR CHECK',
                        "PerformanceInsightsKMSKeyId" : 'ERROR CHECK',
                        "PerformanceInsightsRetentionPeriod" : 'ERROR CHECK',
                        "ServerlessV2ScalingConfiguration" : 'ERROR CHECK',
                        "NetworkType" : list('ERROR CHECK'),
                       })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("rds.describe_db_clusters(),%s", othererr)
    results.append( { "DBClusterIdentifier" : 'ERROR CHECK',
                      "DBClusterTName": 'ERROR CHECK',
                      "DatabaseName": 'ERROR CHECK',
                      "CharacterSetName": 'ERROR CHECK',
                      "AvailabilityZones" : 'ERROR CHECK',
                      "Status" : 'ERROR CHECK',
                      "DBClusterParameterGroup" : 'ERROR CHECK',
                      "DBSubnetGroup" : 'ERROR CHECK',
                      "BackupRetentionPeriod" : 'ERROR CHECK',
                      "AllocatedStorage" : 'ERROR CHECK',
                      "MultiAZ" : 'ERROR CHECK',
                      "Engine" : 'ERROR CHECK',
                      "EngineVersion" : 'ERROR CHECK',
                      "Port" : 'ERROR CHECK',
                      "Endpoint" : 'ERROR CHECK',
                      "ReaderEndpoint" : 'ERROR CHECK',
                      "MasterUsername" : 'ERROR CHECK',
                      "DBClusterOptionGroupName" : 'ERROR CHECK',
                      "DBClusterOptionGroupStatus" : 'ERROR CHECK',
                      "VpcSecurityGroupName" : 'ERROR CHECK',
                      "VpcSecurityGroupId" : 'ERROR CHECK',
                      "VpcSecurityGroupStatus" : 'ERROR CHECK',
                      "KmsKeyAlias" : 'ERROR CHECK',
                      "KmsKeyId" : 'ERROR CHECK',
                      "AssociatedRole" : 'ERROR CHECK',
                      "IAMDatabaseAuthenticationEnabled" : 'ERROR CHECK',
                      "ClusterCreateTime" : 'ERROR CHECK',
                      "Capacity" : 'ERROR CHECK',
                      "EngineMode" : 'ERROR CHECK',
                      "DeletionProtection" : 'ERROR CHECK',
                      "ActivityStreamMode" : 'ERROR CHECK',
                      "ActivityStreamStatus" : 'ERROR CHECK',
                      "ActivityStreamKmsKeyAlias" : 'ERROR CHECK',
                      "ActivityStreamKmsKeyId" : 'ERROR CHECK',
                      "ActivityStreamKinesisStreamName" : 'ERROR CHECK',
                      "DBClusterInstanceClass" : 'ERROR CHECK',
                      "StorageType" : 'ERROR CHECK',
                      "Iops" : 'ERROR CHECK',
                      "PubliclyAccessible" : 'ERROR CHECK',
                      "AutoMinorVersionUpgrade" : 'ERROR CHECK',
                      "PerformanceInsightsEnabled" : 'ERROR CHECK',
                      "PerformanceInsightsKMSKeyAlias" : 'ERROR CHECK',
                      "PerformanceInsightsKMSKeyId" : 'ERROR CHECK',
                      "PerformanceInsightsRetentionPeriod" : 'ERROR CHECK',
                      "ServerlessV2ScalingConfiguration" : 'ERROR CHECK',
                      "NetworkType" : list('ERROR CHECK'),
                     })
  finally:
    return results

def main(argv):

  describe_db_clusters() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
