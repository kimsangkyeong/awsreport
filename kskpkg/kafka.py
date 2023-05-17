####################################################################################################
# 
# Purpose   : get list kafka info
# Source    : kafka.py
# Usage     : python kafka.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2023.05.07     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kafka.html
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

def list_clusters():
  '''
    search KAFKA clusters
  '''
  klogger_dat.debug('kafka clusters')
  try:
    results = [] 
    kafka=boto3.client('kafka')
    clusters = kafka.list_clusters()
    # klogger_dat.debug(clusters)
    if 200 == clusters["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(clusters["ClusterInfoList"])
      if 'ClusterInfoList' in clusters and len(clusters["ClusterInfoList"]) > 0 :
        for ClusterInfo in clusters["ClusterInfoList"]:
        #   klogger_dat.debug(ClusterInfo)

          # Kafka Tag중 Name 값 
          tagname = 'Not Exist Name Tag'
          if 'Tags' in ClusterInfo:
              tag = ClusterInfo['Tags']
              if tag['Name'] != None:
                tagname = tag['Name']
          createdtm = ClusterInfo['CreationTime'].strftime('%Y-%m-%d %H:%M') if 'CreationTime' in ClusterInfo else ' '
          datavolumekmskeyid = []; brokerazdist = []; instancetype = []; numbrokernodes = []; enhancemonitor = [];
          openmonitoring = []; encryptintransit = []; currbswinfo = []; cliauth = []; clientsubnets = []; subnetTName = [];
          sgrp = []; sgrpTName = []; storageinfo = []; connectinfo = []; zoneids = []; loginfo = [];
          storagemode = []; zookeeperconnstr = []; zookeeperconnstrtls = []; currversion = [];
          if 'CurrentBrokerSoftwareInfo' in ClusterInfo :
            currbswinfo.append(ClusterInfo['CurrentBrokerSoftwareInfo'])

          if 'OpenMonitoring' in ClusterInfo :
            openmonitoring.append(ClusterInfo['OpenMonitoring'])
          
          if 'EncryptionInfo'  in ClusterInfo :
            if 'EncryptionAtRest' in ClusterInfo['EncryptionInfo'] :
              if 'DataVolumeKMSKeyId' in ClusterInfo['EncryptionInfo']['EncryptionAtRest'] :
                datavolumekmskeyid.append(ClusterInfo['EncryptionInfo']['EncryptionAtRest']['DataVolumeKMSKeyId'])
            if 'EncryptionInTransit' in ClusterInfo['EncryptionInfo'] :
                encryptintransit.append(ClusterInfo['EncryptionInfo']['EncryptionInTransit'])

          if 'BrokerNodeGroupInfo' in ClusterInfo :
            brokerazdist.append(ClusterInfo['BrokerNodeGroupInfo']['BrokerAZDistribution'] if 'BrokerAZDistribution' in ClusterInfo['BrokerNodeGroupInfo'] else '')
            instancetype.append(ClusterInfo['BrokerNodeGroupInfo']['InstanceType'] if 'InstanceType' in ClusterInfo['BrokerNodeGroupInfo'] else '')
            if 'ClientSubnets' in ClusterInfo['BrokerNodeGroupInfo'] and len(ClusterInfo['BrokerNodeGroupInfo']['ClientSubnets']) > 0 :
              clientsubnets = ClusterInfo['BrokerNodeGroupInfo']['ClientSubnets']
            if 'SecurityGroups' in ClusterInfo['BrokerNodeGroupInfo'] and len(ClusterInfo['BrokerNodeGroupInfo']['SecurityGroups']) > 0 :
              sgrp = ClusterInfo['BrokerNodeGroupInfo']['SecurityGroups']
            if 'StorageInfo' in ClusterInfo['BrokerNodeGroupInfo'] :
              storageinfo.append(ClusterInfo['BrokerNodeGroupInfo']['StorageInfo'])
            if 'ConnectivityInfo' in ClusterInfo['BrokerNodeGroupInfo'] :
              connectinfo.append(ClusterInfo['BrokerNodeGroupInfo']['ConnectivityInfo'])
            if 'ZoneIds' in ClusterInfo['BrokerNodeGroupInfo'] and len(ClusterInfo['BrokerNodeGroupInfo']['ZoneIds']) > 0 :
              zoneids = ClusterInfo['BrokerNodeGroupInfo']['ZoneIds']

          if 'ClientAuthentication' in ClusterInfo :
            cliauth.append(ClusterInfo['ClientAuthentication'])

          if 'LoggingInfo' in ClusterInfo :
            loginfo.append(ClusterInfo['LoggingInfo'])

          numbrokernodes.append(str(ClusterInfo['NumberOfBrokerNodes'] if 'NumberOfBrokerNodes' in ClusterInfo else ' '))
          currversion.append(ClusterInfo['CurrentVersion'] if 'CurrentVersion' in ClusterInfo else ' ')
          enhancemonitor.append(ClusterInfo['EnhancedMonitoring'] if 'EnhancedMonitoring' in ClusterInfo else ' ')
          zookeeperconnstr.append(ClusterInfo['ZookeeperConnectString'] if 'ZookeeperConnectString' in ClusterInfo else ' ')
          zookeeperconnstrtls.append(ClusterInfo['ZookeeperConnectStringTls'] if 'ZookeeperConnectStringTls' in ClusterInfo else ' ')
          storagemode.append(ClusterInfo['StorageMode'] if 'StorageMode' in ClusterInfo else ' ')

          # list count sync with space
          utils.ListSyncCountWithSpace(openmonitoring, encryptintransit, currbswinfo, cliauth, clientsubnets, 
                                       subnetTName, sgrp, sgrpTName, storageinfo, connectinfo, zoneids, loginfo,
                                       datavolumekmskeyid, brokerazdist, instancetype, numbrokernodes, enhancemonitor,
                                       zookeeperconnstr, zookeeperconnstrtls, storagemode, currversion
                                      )

          results.append({ "ClusterName" : ClusterInfo['ClusterName'] if 'ClusterName' in ClusterInfo else ' ',
                           "ClusterTName" : tagname,
                           "CreationTime" : createdtm,
                           "CurrentVersion" : currversion,
                           "CurrentBrokerSoftwareInfo" : currbswinfo,
                           "BrokerAZDistribution" : brokerazdist,
                           "NumberOfBrokerNodes" : numbrokernodes,
                           "State" : ClusterInfo['State'] if 'State' in ClusterInfo else ' ',
                           "InstanceType" : instancetype,
                           "StorageInfo(GiB)" : storageinfo,
                           "ClientSubnet" : clientsubnets,
                           "ClientSubnetTName" : subnetTName,
                           "SecurityGroupId" : sgrp,
                           "SecurityGroupTName" : sgrpTName,
                           "DataVolumeKMSKeyId" : datavolumekmskeyid,
                           "DataVolumeKMSTName" : '',
                           "EncryptionInTransit" : encryptintransit,
                           "ClientAuthentication" : cliauth,
                           "ConnectivityInfo" : connectinfo,
                           "ZoneIds" : zoneids,
                           "EnhancedMonitoring" : enhancemonitor,
                           "OpenMonitoring" : openmonitoring,
                           "LoggingInfo" : loginfo,
                           "ZookeeperConnectString" : zookeeperconnstr,
                           "ZookeeperConnectStringTls" : zookeeperconnstrtls,
                           "StorageMode" : storagemode
                         })
      else: # column list
        results.append({ "ClusterName" : ' ',
                         "ClusterTName" : ' ',
                         "CreationTime" : ' ',
                         "CurrentVersion" : ' ',
                         "CurrentBrokerSoftwareInfo" : ' ',
                         "BrokerAZDistribution" : ' ',
                         "NumberOfBrokerNodes" : ' ',
                         "State" : ' ',
                         "InstanceType" : ' ',
                         "StorageInfo" : ' ',
                         "ClientSubnet" : ' ',
                         "ClientSubnetTName" : ' ',
                         "SecurityGroupId" : ' ',
                         "SecurityGroupTName" : ' ',
                         "DataVolumeKMSKeyId" : ' ',
                         "DataVolumeKMSTName" : ' ',
                         "ClientAuthentication" : ' ',
                         "EncryptionInTransit" : ' ',
                         "ClientAuthentication" : ' ',
                         "ConnectivityInfo" : ' ',
                         "ZoneIds" : ' ',
                         "EnhancedMonitoring" : ' ',
                         "OpenMonitoring" : ' ',
                         "LoggingInfo" : ' ',
                         "ZookeeperConnectString" : ' ',
                         "ZookeeperConnectStringTls" : ' ',
                         "StorageMode" : list(' ')
                       })
    else:
      klogger.error("call error : %d", clusters["ResponseMetadata"]["HTTPStatusCode"])
      results.append({ "ClusterName" : 'ERROR CHECK',
                       "ClusterTName" : 'ERROR CHECK',
                       "CreationTime" : 'ERROR CHECK',
                       "CurrentVersion" : 'ERROR CHECK',
                       "CurrentBrokerSoftwareInfo" : 'ERROR CHECK',
                       "BrokerAZDistribution" : 'ERROR CHECK',
                       "NumberOfBrokerNodes" : 'ERROR CHECK',
                       "State" : 'ERROR CHECK',
                       "InstanceType" : 'ERROR CHECK',
                       "StorageInfo" : 'ERROR CHECK',
                       "ClientSubnet" : 'ERROR CHECK',
                       "ClientSubnetTName" : 'ERROR CHECK',
                       "SecurityGroupId" : 'ERROR CHECK',
                       "SecurityGroupTName" : 'ERROR CHECK',
                       "DataVolumeKMSKeyId" : 'ERROR CHECK',
                       "DataVolumeKMSTName" : 'ERROR CHECK',
                       "EncryptionInTransit" : 'ERROR CHECK',
                       "ClientAuthentication" : 'ERROR CHECK',
                       "ClientAuthentication" : 'ERROR CHECK',
                       "ConnectivityInfo" : 'ERROR CHECK',
                       "ZoneIds" : 'ERROR CHECK',
                       "EnhancedMonitoring" : 'ERROR CHECK',
                       "OpenMonitoring" : 'ERROR CHECK',
                       "LoggingInfo" : 'ERROR CHECK',
                       "ZookeeperConnectString" : 'ERROR CHECK',
                       "ZookeeperConnectStringTls" : 'ERROR CHECK',
                       "StorageMode" : list(' ')
                     })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("kafka.list_clusters(),%s", othererr)
    results.append({ "ClusterName" : 'ERROR CHECK',
                     "ClusterTName" : 'ERROR CHECK',
                     "CreationTime" : 'ERROR CHECK',
                     "CurrentVersion" : 'ERROR CHECK',
                     "CurrentBrokerSoftwareInfo" : 'ERROR CHECK',
                     "BrokerAZDistribution" : 'ERROR CHECK',
                     "NumberOfBrokerNodes" : 'ERROR CHECK',
                     "State" : 'ERROR CHECK',
                     "InstanceType" : 'ERROR CHECK',
                     "StorageInfo" : 'ERROR CHECK',
                     "ClientSubnet" : 'ERROR CHECK',
                     "ClientSubnetTName" : 'ERROR CHECK',
                     "SecurityGroupId" : 'ERROR CHECK',
                     "SecurityGroupTName" : 'ERROR CHECK',
                     "DataVolumeKMSKeyId" : 'ERROR CHECK',
                     "DataVolumeKMSTName" : 'ERROR CHECK',
                     "EncryptionInTransit" : 'ERROR CHECK',
                     "ClientAuthentication" : 'ERROR CHECK',
                     "ClientAuthentication" : 'ERROR CHECK',
                     "ConnectivityInfo" : 'ERROR CHECK',
                     "ZoneIds" : 'ERROR CHECK',
                     "EnhancedMonitoring" : 'ERROR CHECK',
                     "OpenMonitoring" : 'ERROR CHECK',
                     "LoggingInfo" : 'ERROR CHECK',
                     "ZookeeperConnectString" : 'ERROR CHECK',
                     "ZookeeperConnectStringTls" : 'ERROR CHECK',
                     "StorageMode" : list(' ')
                   })
  finally:
    return results

def describe_cluster(clusterArn):
  '''
    search kafka cluster v2
  '''
#   klogger_dat.debug('kafka cluster')

  try:
    result = None
    kafka=boto3.client('kafka')
    klogger.debug(f'{clusterArn}')
    clusterInfo = kafka.describe_cluster(ClusterArn=clusterArn)
    # klogger.debug("%s", clusterInfo)
    if 200 == clusterInfo["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",clusterInfo["ClusterInfo"])
      if 'ClusterInfo' in clusterInfo :
        result = clusterInfo['ClusterInfo']
    else:
      klogger.error("call error : %d", clusterInfo["ResponseMetadata"]["HTTPStatusCode"])
    klogger.debug(result)
  except Exception as othererr:
    klogger.error("kafka.describe_cluster(),%s", othererr)
  finally:
    return result

def main(argv):

  list_clusters()

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
