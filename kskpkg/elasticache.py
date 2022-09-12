####################################################################################################
# 
# Purpose   : get list elasticache
# Source    : elasticache.py
# Usage     : python elasticache.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.08     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html
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

def describe_cache_clusters():
  '''
    search elasticache  
  '''
  klogger_dat.debug('elasticache')

  try:
    results = [] 
    elasticache=boto3.client('elasticache')
    clusters = elasticache.describe_cache_clusters()
    # klogger_dat.debug(clusters)
    if 200 == clusters["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(clusters["CacheClusters"])
      if 'CacheClusters' in clusters and len(clusters["CacheClusters"]) > 0 :
        for cachecluster in clusters["CacheClusters"]:
        #   klogger_dat.debug(cachecluster)
          
          configurationendpoint = []; notificationconf = []; cachesgnames = []; cacheparams = [];
          cachenodes = []; securitygrps = []; cachesgstatus = []; sgrpstatus = [];
          if 'ConfigurationEndpoint' in cachecluster :
            configurationendpoint.append(cachecluster['ConfigurationEndpoint'])
          if 'NotificationConfiguration' in cachecluster :
            notificationconf.append(cachecluster['NotificationConfiguration'])
          if 'CacheSecurityGroups' in cachecluster :
            for sgrp in cachecluster['CacheSecurityGroups'] :
              cachesgnames.append(sgrp['CacheSecurityGroupName'] if 'CacheSecurityGroupName' in sgrp else ' ')
              cachesgstatus.append(sgrp['Status'] if 'Status' in sgrp else ' ')
          if 'CacheParameterGroup' in cachecluster :
            cacheparams.append(cachecluster['CacheParameterGroup'])
          if 'CacheNodes' in cachecluster :
            for node in cachecluster['CacheNodes'] :
              cachenodes.append(node)
          if 'SecurityGroups' in cachecluster :
            for sgrp in cachecluster['SecurityGroups'] :
              securitygrps.append(sgrp['SecurityGroupId'] if 'SecurityGroupId' in sgrp else ' ')
              sgrpstatus.append(sgrp['Status'] if 'Status' in sgrp else ' ')

          # list count sync with space
          utils.ListSyncCountWithSpace(configurationendpoint, notificationconf, cachesgnames, cacheparams,
                                       cachenodes, securitygrps, cachesgstatus, sgrpstatus
                                       )

          results.append( { "CacheClusterId": cachecluster['CacheClusterId'],
                            "ConfigurationEndpoint" : configurationendpoint,
                            "ClientDownloadLandingPage" : cachecluster['ClientDownloadLandingPage'] if 'ClientDownloadLandingPage' in cachecluster else ' ',
                            "CacheNodeType" : cachecluster['CacheNodeType'] if 'CacheNodeType' in cachecluster else ' ',
                            "Engine" : cachecluster['Engine'] if 'Engine' in cachecluster else ' ',
                            "EngineVersion" : cachecluster['EngineVersion'] if 'EngineVersion' in cachecluster else ' ',
                            "CacheClusterStatus" : cachecluster['CacheClusterStatus'] if 'CacheClusterStatus' in cachecluster else ' ',
                            "NumCacheNodes" : cachecluster['NumCacheNodes'] if 'NumCacheNodes' in cachecluster else ' ',
                            "PreferredAvailabilityZone" : cachecluster['PreferredAvailabilityZone'] if 'PreferredAvailabilityZone' in cachecluster else ' ',
                            "CacheClusterCreateTime" : cachecluster['CacheClusterCreateTime'].strftime('%Y-%m-%d') if 'CacheClusterCreateTime' in cachecluster else ' ',
                            "PreferredMaintenanceWindow" : cachecluster['PreferredMaintenanceWindow'] if 'PreferredMaintenanceWindow' in cachecluster else ' ',
                            "NotificationConfiguration" : notificationconf,
                            "CacheSecurityGroup" : cachesgnames,
                            "CacheSGroupTName" : ' ',
                            "CacheSGroupStatus" : cachesgstatus,
                            "CacheParameterGroup" : cacheparams,
                            "CacheSubnetGroupName" : cachecluster['CacheSubnetGroupName'] if 'CacheSubnetGroupName' in cachecluster else ' ',
                            "CacheNodes" : cachenodes,
                            "SecurityGroup" : securitygrps,
                            "SGroupTName" : ' ',
                            "SGroupStatus" : sgrpstatus,
                            "ReplicationGroupId" : cachecluster['ReplicationGroupId'] if 'ReplicationGroupId' in cachecluster else ' ',
                            "Arn" : cachecluster['ARN'] if 'ARN' in cachecluster else ' ',
                          })
      else: # column list
        results.append( { "CacheClusterId": ' ',
                          "ConfigurationEndpoint" : ' ',
                          "ClientDownloadLandingPage" : ' ',
                          "CacheNodeType" : ' ',
                          "Engine" : ' ',
                          "EngineVersion" : ' ',
                          "CacheClusterStatus" : ' ',
                          "NumCacheNodes" : ' ',
                          "PreferredAvailabilityZone" : ' ',
                          "CacheClusterCreateTime" : ' ',
                          "PreferredMaintenanceWindow" : ' ',
                          "NotificationConfiguration" : ' ',
                          "CacheSecurityGroup" : ' ',
                          "CacheSGroupTName" : ' ',
                          "CacheSGroupStatus" : ' ',
                          "CacheParameterGroup" : ' ',
                          "CacheSubnetGroupName" : ' ',
                          "CacheNodes" : ' ',
                          "SecurityGroup" : ' ',
                          "SGroupTName" : ' ',
                          "SGroupStatus" : ' ',
                          "ReplicationGroupId" : ' ',
                          "Arn" : list(' '),
                        })
    else:
      klogger.error("call error : %d", clusters["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "CacheClusterId": 'ERROR CHECK',
                        "ConfigurationEndpoint" : 'ERROR CHECK',
                        "ClientDownloadLandingPage" : 'ERROR CHECK',
                        "CacheNodeType" : 'ERROR CHECK',
                        "Engine" : 'ERROR CHECK',
                        "EngineVersion" : 'ERROR CHECK',
                        "CacheClusterStatus" : 'ERROR CHECK',
                        "NumCacheNodes" : 'ERROR CHECK',
                        "PreferredAvailabilityZone" : 'ERROR CHECK',
                        "CacheClusterCreateTime" : 'ERROR CHECK',
                        "PreferredMaintenanceWindow" : 'ERROR CHECK',
                        "NotificationConfiguration" : 'ERROR CHECK',
                        "CacheSecurityGroup" : 'ERROR CHECK',
                        "CacheSGroupTName" : 'ERROR CHECK',
                        "CacheSGroupStatus" : 'ERROR CHECK',
                        "CacheParameterGroup" : 'ERROR CHECK',
                        "CacheSubnetGroupName" : 'ERROR CHECK',
                        "CacheNodes" : 'ERROR CHECK',
                        "SecurityGroup" : 'ERROR CHECK',
                        "SGroupTName" : 'ERROR CHECK',
                        "SGroupStatus" : 'ERROR CHECK',
                        "ReplicationGroupId" : 'ERROR CHECK',
                        "Arn" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("elasticache.describe_cache_clusters(),%s", othererr)
    results.append( { "CacheClusterId": 'ERROR CHECK',
                      "ConfigurationEndpoint" : 'ERROR CHECK',
                      "ClientDownloadLandingPage" : 'ERROR CHECK',
                      "CacheNodeType" : 'ERROR CHECK',
                      "Engine" : 'ERROR CHECK',
                      "EngineVersion" : 'ERROR CHECK',
                      "CacheClusterStatus" : 'ERROR CHECK',
                      "NumCacheNodes" : 'ERROR CHECK',
                      "PreferredAvailabilityZone" : 'ERROR CHECK',
                      "CacheClusterCreateTime" : 'ERROR CHECK',
                      "PreferredMaintenanceWindow" : 'ERROR CHECK',
                      "NotificationConfiguration" : 'ERROR CHECK',
                      "CacheSecurityGroups" : 'ERROR CHECK',
                      "CacheSGroupTName" : 'ERROR CHECK',
                      "CacheSGroupStatus" : 'ERROR CHECK',
                      "CacheParameterGroup" : 'ERROR CHECK',
                      "CacheSubnetGroupName" : 'ERROR CHECK',
                      "CacheNodes" : 'ERROR CHECK',
                      "SecurityGroup" : 'ERROR CHECK',
                      "SGroupTName" : 'ERROR CHECK',
                      "SGroupStatus" : 'ERROR CHECK',
                      "ReplicationGroupId" : 'ERROR CHECK',
                      "Arn" : list('ERROR CHECK'),
                    })
  finally:
    return results

def main(argv):

  describe_cache_clusters() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
