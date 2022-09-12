####################################################################################################
# 
# Purpose   : get list redshift info
# Source    : redshift.py
# Usage     : python redshift.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.11     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html
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

def describe_clusters():
  '''
    search REDSHIFT Clusters 
  '''
  klogger_dat.debug('redshift')
  try:
    results = [] 
    redshift=boto3.client('redshift')
    clusters = redshift.describe_clusters()
    # klogger_dat.debug(dbclusters)
    if 200 == clusters["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(dbclusters["Clusters"])
      if len(clusters["Clusters"]) > 0 :
        for cluster in clusters["Clusters"]:
        #   klogger_dat.debug(cluster)
          endpoints = []; allowversionupgrade = 'False'; publicaccessible = 'Flase'; encrpted = 'False'; enhancedvpcrouting = 'False';
          clustersgrps = []; clustersgrpstatus = []; vpcsgrpids = []; vpcsgrpstatus = []; clusterparamgrps = []; clusternodes = [];
          elasticipstatus = []; iamroles = []; snapshotscheduleinfos = []; reservednodeexchangestatus = []; numofnodes = [];
          clusterversions = []; dbnames = []; masterusernames = []; clusterctime = []; kmskeyids = []; clusterpubkey = [];
          if 'Endpoint' in cluster :
            endpoints.append(str(cluster['Endpoint']))
          if 'AllowVersionUpgrade' in cluster :
            if cluster['AllowVersionUpgrade'] :
              allowversionupgrade = 'True'
          if 'PubliclyAccessible' in cluster :
            if cluster['PubliclyAccessible'] :
              publicaccessible = 'True'
          if 'Encrypted' in cluster :
            if cluster['Encrypted'] :
              encrpted = 'True'
          if 'ClusterSecurityGroups' in cluster :
            for csgrp in cluster['ClusterSecurityGroups'] : 
              clustersgrps.append(csgrp['ClusterSecurityGroupName'] if 'ClusterSecurityGroupName' in csgrp else ' ')
              clustersgrpstatus.append(csgrp['Status'] if 'Status' in csgrp else ' ')
          if 'VpcSecurityGroups' in cluster :
            for vpcsgrp in cluster['VpcSecurityGroups'] :
              vpcsgrpids.append(vpcsgrp['VpcSecurityGroupId'] if 'VpcSecurityGroupId' in vpcsgrp else ' ')
              vpcsgrpstatus.append(vpcsgrp['Status'] if 'Status' in vpcsgrp else ' ')
          if 'ClusterParameterGroups' in cluster :
            for cparam in cluster['ClusterParameterGroups'] : 
              clusterparamgrps.append(str(cparam))
          if 'ClusterNodes' in cluster :
            for cnode in cluster['ClusterNodes'] :
              clusternodes.append(cnode)
          if 'ElasticIpStatus' in cluster :
            elasticipstatus.append(cluster['ElasticIpStatus'])
          if 'IamRoles' in cluster :
            for iamrole in cluster['IamRoles'] :
              iamroles.append(iamrole)
          snapshotscheduleinfo = {}
          if 'SnapshotScheduleIdentifier' in cluster :
            snapshotscheduleinfo['SnapshotScheduleIdentifier'] = cluster['SnapshotScheduleIdentifier']
          if 'SnapshotScheduleState' in cluster :
            snapshotscheduleinfo['SnapshotScheduleState'] = cluster['SnapshotScheduleState']
          if 'ExpectedNextSnapshotScheduleTime' in cluster :
            snapshotscheduleinfo['ExpectedNextSnapshotScheduleTime'] = cluster['ExpectedNextSnapshotScheduleTime']
          if 'ExpectedNextSnapshotScheduleTimeStatus' in cluster :
            snapshotscheduleinfo['ExpectedNextSnapshotScheduleTimeStatus'] = cluster['ExpectedNextSnapshotScheduleTimeStatus']
          snapshotscheduleinfos.append(snapshotscheduleinfo)
          if 'ReservedNodeExchangeStatus' in cluster :
            reservednodeexchangestatus.append(cluster['ReservedNodeExchangeStatus'])
          if 'EnhancedVpcRouting' in cluster :
            if cluster['EnhancedVpcRouting'] :
              enhancedvpcrouting = 'True'
          if 'NumberOfNodes' in cluster :
            numofnodes.append(cluster['NumberOfNodes'])
          if 'ClusterVersion' in cluster :
            clusterversions.append(cluster['ClusterVersion'])
          if 'DBName' in cluster :
            dbnames.append(cluster['DBName'])
          if 'MasterUsername' in cluster :
            masterusernames.append(cluster['MasterUsername'])
          if 'ClusterCreateTime' in cluster :
            clusterctime.append(cluster['ClusterCreateTime'].strftime("%Y-%m-%d"))
          if 'KmsKeyId' in cluster :
            kmskeyids.append(cluster['KmsKeyId'])
          if 'ClusterPublicKey' in cluster :
            clusterpubkey.append(cluster['ClusterPublicKey'])
          # redshift Tag중 Name 값 
          tagname = 'Not Exist Name Tag'
          if 'Tags' in cluster:
            for tag in cluster['Tags']:
              if tag['Key'] == 'Name':
                tagname = tag['Value']
                break
          # list count sync with space
          utils.ListSyncCountWithSpace(endpoints, clustersgrps, clustersgrpstatus, vpcsgrpids, vpcsgrpstatus, clusterparamgrps,
                                       clusternodes, elasticipstatus, iamroles, snapshotscheduleinfos, reservednodeexchangestatus,
                                       numofnodes, clusterversions, dbnames, masterusernames, clusterctime, kmskeyids, clusterpubkey
                                      )
          
          results.append( { "ClusterIdentifier" : cluster['ClusterIdentifier'] if 'ClusterIdentifier' in cluster else ' ',
                            "NumberOfNodes" : numofnodes,
                            "Endpoint" : endpoints,
                            "ClusterNodes" : clusternodes,
                            "DBName" : dbnames,
                            "MasterUsername" : masterusernames,
                            "NodeType": cluster['NodeType'] if 'NodeType' in cluster else ' ',
                            "ClusterVersion" : clusterversions,
                            "PubliclyAccessible" : publicaccessible,
                            "Encrypted" : encrpted,
                            "ClusterStatus": cluster['ClusterStatus'] if 'ClusterStatus' in cluster else ' ',
                            "ClusterCreateTime" : clusterctime,
                            "ClusterNamespaceArn" : cluster['ClusterNamespaceArn'] if 'ClusterNamespaceArn' in cluster else ' ',
                            "ClusterPublicKey" : clusterpubkey,
                            "ElasticIpStatus" : elasticipstatus,
                            "ClusterParameterGroups" : clusterparamgrps,
                            "TotalStorageCapacityInMegaBytes" : cluster['TotalStorageCapacityInMegaBytes'] if 'TotalStorageCapacityInMegaBytes' in cluster else ' ',
                            "ClusterAvailabilityStatus" : cluster['ClusterAvailabilityStatus'] if 'ClusterAvailabilityStatus' in cluster else ' ',
                            "IamRoles" : iamroles,
                            "DefaultIamRoleArn" : cluster['DefaultIamRoleArn'] if 'DefaultIamRoleArn' in cluster else ' ',
                            "KmsKeyId" : kmskeyids,
                            "KmsKeyAlias" : ' ',
                            "VpcId" : cluster['VpcId'] if 'VpcId' in cluster else ' ',
                            "VpcTName" : ' ',
                            "EnhancedVpcRouting" : enhancedvpcrouting,
                            "AvailabilityZone" : cluster['AvailabilityZone'] if 'AvailabilityZone' in cluster else ' ',
                            "ClusterSubnetGroupName" : cluster['ClusterSubnetGroupName'] if 'ClusterSubnetGroupName' in cluster else ' ',
                            "ClusterSecurityGroups" : clustersgrps,
                            "ClusterSecurityGroupStatus" : clustersgrpstatus,
                            "VpcSecurityGroupId" : vpcsgrpids,
                            "VpcSecurityGroupName" : ' ',
                            "VpcSecurityGroupStatus" : vpcsgrpstatus,
                            "ClusterTName": tagname,
                            "ModifyStatus" : cluster['ModifyStatus'] if 'ModifyStatus' in cluster else ' ',
                            "AvailabilityZoneRelocationStatus" : cluster['AvailabilityZoneRelocationStatus'] if 'AvailabilityZoneRelocationStatus' in cluster else ' ',
                            "AllowVersionUpgrade" : allowversionupgrade,
                            "MaintenanceTrackName" : cluster['MaintenanceTrackName'] if 'MaintenanceTrackName' in cluster else ' ',
                            "ElasticResizeNumberOfNodeOptions" : cluster['ElasticResizeNumberOfNodeOptions'] if 'ElasticResizeNumberOfNodeOptions' in cluster else ' ',
                            "SnapshotScheduleInfo" : snapshotscheduleinfos,
                            "ReservedNodeExchangeStatus" : reservednodeexchangestatus,
                           })
      else: # column list
        results.append( { "ClusterIdentifier" : ' ',
                          "NumberOfNodes" : ' ',
                          "Endpoint" : ' ',
                          "ClusterNodes" : ' ',
                          "DBName" : ' ',
                          "MasterUsername" : ' ',
                          "NodeType": ' ',
                          "ClusterVersion" : ' ',
                          "PubliclyAccessible" : ' ',
                          "Encrypted" : ' ',
                          "ClusterStatus": ' ',
                          "ClusterCreateTime" : ' ',
                          "ClusterNamespaceArn" : ' ',
                          "ClusterPublicKey" : ' ',
                          "ElasticIpStatus" : ' ',
                          "ClusterParameterGroups" : ' ',
                          "TotalStorageCapacityInMegaBytes" : ' ',
                          "ClusterAvailabilityStatus" : ' ',
                          "IamRoles" : ' ',
                          "DefaultIamRoleArn" : ' ',
                          "KmsKeyId" : ' ',
                          "KmsKeyAlias" : ' ',
                          "VpcId" : ' ',
                          "VpcTName" : ' ',
                          "EnhancedVpcRouting" : ' ',
                          "AvailabilityZone" : ' ',
                          "ClusterSubnetGroupName" : ' ',
                          "ClusterSecurityGroups" : ' ',
                          "ClusterSecurityGroupStatus" : ' ',
                          "VpcSecurityGroupId" : ' ',
                          "VpcSecurityGroupName" : ' ',
                          "VpcSecurityGroupStatus" : ' ',
                          "ClusterTName": ' ',
                          "ModifyStatus" : ' ',
                          "AvailabilityZoneRelocationStatus" : ' ',
                          "AllowVersionUpgrade" : ' ',
                          "MaintenanceTrackName" : ' ',
                          "ElasticResizeNumberOfNodeOptions" : ' ',
                          "SnapshotScheduleInfo" : ' ',
                          "ReservedNodeExchangeStatus" : list(' '),
                         })
    else:
      klogger.error("call error : %d", clusters["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "ClusterIdentifier" : 'ERROR CHECK',
                        "NumberOfNodes" : 'ERROR CHECK',
                        "Endpoint" : 'ERROR CHECK',
                        "ClusterNodes" : 'ERROR CHECK',
                        "DBName" : 'ERROR CHECK',
                        "MasterUsername" : 'ERROR CHECK',
                        "NodeType": 'ERROR CHECK',
                        "ClusterVersion" : 'ERROR CHECK',
                        "PubliclyAccessible" : 'ERROR CHECK',
                        "Encrypted" : 'ERROR CHECK',
                        "ClusterStatus": 'ERROR CHECK',
                        "ClusterCreateTime" : 'ERROR CHECK',
                        "ClusterNamespaceArn" : 'ERROR CHECK',
                        "ClusterPublicKey" : 'ERROR CHECK',
                        "ElasticIpStatus" : 'ERROR CHECK',
                        "ClusterParameterGroups" : 'ERROR CHECK',
                        "TotalStorageCapacityInMegaBytes" : 'ERROR CHECK',
                        "ClusterAvailabilityStatus" : 'ERROR CHECK',
                        "IamRoles" : 'ERROR CHECK',
                        "DefaultIamRoleArn" : 'ERROR CHECK',
                        "KmsKeyId" : 'ERROR CHECK',
                        "KmsKeyAlias" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : 'ERROR CHECK',
                        "EnhancedVpcRouting" : 'ERROR CHECK',
                        "AvailabilityZone" : 'ERROR CHECK',
                        "ClusterSubnetGroupName" : 'ERROR CHECK',
                        "ClusterSecurityGroups" : 'ERROR CHECK',
                        "ClusterSecurityGroupStatus" : 'ERROR CHECK',
                        "VpcSecurityGroupId" : 'ERROR CHECK',
                        "VpcSecurityGroupName" : 'ERROR CHECK',
                        "VpcSecurityGroupStatus" : 'ERROR CHECK',
                        "ClusterTName": 'ERROR CHECK',
                        "ModifyStatus" : 'ERROR CHECK',
                        "AvailabilityZoneRelocationStatus" : 'ERROR CHECK',
                        "AllowVersionUpgrade" : 'ERROR CHECK',
                        "MaintenanceTrackName" : 'ERROR CHECK',
                        "ElasticResizeNumberOfNodeOptions" : 'ERROR CHECK',
                        "SnapshotScheduleInfo" : 'ERROR CHECK',
                        "ReservedNodeExchangeStatus" : list('ERROR CHECK'),
                       })
    klogger.debug(results)
  except Exception as othererr:
    klogger.error("redshift.describe_clusters(),%s", othererr)
    results.append( { "ClusterIdentifier" : 'ERROR CHECK',
                      "NumberOfNodes" : 'ERROR CHECK',
                      "Endpoint" : 'ERROR CHECK',
                      "ClusterNodes" : 'ERROR CHECK',
                      "DBName" : 'ERROR CHECK',
                      "MasterUsername" : 'ERROR CHECK',
                      "NodeType": 'ERROR CHECK',
                      "ClusterVersion" : 'ERROR CHECK',
                      "PubliclyAccessible" : 'ERROR CHECK',
                      "Encrypted" : 'ERROR CHECK',
                      "ClusterStatus": 'ERROR CHECK',
                      "ClusterCreateTime" : 'ERROR CHECK',
                      "ClusterNamespaceArn" : 'ERROR CHECK',
                      "ClusterPublicKey" : 'ERROR CHECK',
                      "ElasticIpStatus" : 'ERROR CHECK',
                      "ClusterParameterGroups" : 'ERROR CHECK',
                      "TotalStorageCapacityInMegaBytes" : 'ERROR CHECK',
                      "ClusterAvailabilityStatus" : 'ERROR CHECK',
                      "IamRoles" : 'ERROR CHECK',
                      "DefaultIamRoleArn" : 'ERROR CHECK',
                      "KmsKeyId" : 'ERROR CHECK',
                      "KmsKeyAlias" : 'ERROR CHECK',
                      "VpcId" : 'ERROR CHECK',
                      "VpcTName" : 'ERROR CHECK',
                      "EnhancedVpcRouting" : 'ERROR CHECK',
                      "AvailabilityZone" : 'ERROR CHECK',
                      "ClusterSubnetGroupName" : 'ERROR CHECK',
                      "ClusterSecurityGroups" : 'ERROR CHECK',
                      "ClusterSecurityGroupStatus" : 'ERROR CHECK',
                      "VpcSecurityGroupId" : 'ERROR CHECK',
                      "VpcSecurityGroupName" : 'ERROR CHECK',
                      "VpcSecurityGroupStatus" : 'ERROR CHECK',
                      "ClusterTName": 'ERROR CHECK',
                      "ModifyStatus" : 'ERROR CHECK',
                      "AvailabilityZoneRelocationStatus" : 'ERROR CHECK',
                      "AllowVersionUpgrade" : 'ERROR CHECK',
                      "MaintenanceTrackName" : 'ERROR CHECK',
                      "ElasticResizeNumberOfNodeOptions" : 'ERROR CHECK',
                      "SnapshotScheduleInfo" : 'ERROR CHECK',
                      "ReservedNodeExchangeStatus" : list('ERROR CHECK'),
                     })
  finally:
    return results

def main(argv):

  describe_clusters() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
