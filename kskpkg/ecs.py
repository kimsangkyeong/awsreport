####################################################################################################
# 
# Purpose   : get list ecs info
# Source    : ecs.py
# Usage     : python eks.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.25     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html
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
    search ECS Clusters 
  '''
  klogger_dat.debug('ecs')
  try:
    results = [] 
    ecs=boto3.client('ecs')
    ecsclusters = ecs.list_clusters()
    # klogger_dat.debug(ecsclusters)
    if 200 == ecsclusters["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(ecsclusters["clusterArns"])
      if 'clusterArns' in ecsclusters and len(ecsclusters["clusterArns"]) > 0 : 
        for ecscluster in ecsclusters["clusterArns"]:
        #   klogger_dat.debug(ecscluster)
          cluster_desc = describe_clusters(ecscluster)
          if cluster_desc != None :
            # klogger.debug(cluster_desc)
            # ECS Cluster Tag중 Name 값
            tagname = 'Not Exist Name Tag'
            if 'tags' in cluster_desc:
              for tag in cluster_desc['tags']:
                if 'Name' == tag['key']:
                  tagname = tag['value']
                  break
            capacityproviders = [];
            if 'capacityProviders' in cluster_desc:
              capacityproviders = cluster_desc['capacityProviders']
            # list count sync with space
            utils.ListSyncCountWithSpace(capacityproviders)

            results.append( { "ClusterArn" : ecscluster,
                              "ECSClusterName" : cluster_desc['clusterName'],
                              "ECSClusterTName" : tagname,
                              "Status": cluster_desc['status'],
                              "RegisteredContainerInstancesCount": cluster_desc['registeredContainerInstancesCount'],
                              "RunningTasksCount": cluster_desc['runningTasksCount'],
                              "PendingTasksCount": cluster_desc['pendingTasksCount'],
                              "ActiveServicesCount": cluster_desc['activeServicesCount'],
                              "capacityProviders": capacityproviders,
                            })
          else: # Can't Describe Cluster Info
            results.append( { "ClusterArn" : ecscluster,
                              "ECSClusterName" : ' ',
                              "ECSClusterTName" : ' ',
                              "Status": ' ',
                              "RegisteredContainerInstancesCount": ' ',
                              "RunningTasksCount": ' ',
                              "PendingTasksCount": ' ',
                              "ActiveServicesCount": ' ',
                              "capacityProviders": list(' '),
                            })
      else: # Not Exists
        results.append( { "ClusterArn" : ' ',
                          "ECSClusterName" : ' ',
                          "ECSClusterTName" : ' ',
                          "Status": ' ',
                          "RegisteredContainerInstancesCount": ' ',
                          "RunningTasksCount": ' ',
                          "PendingTasksCount": ' ',
                          "ActiveServicesCount": ' ',
                          "capacityProviders": list(' '),
                        })
    else:
      klogger.error("call error : %d", ecsclusters["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "ClusterArn" : 'ERROR CHECK',
                        "ECSClusterName" : 'ERROR CHECK',
                        "ECSClusterTName" : 'ERROR CHECK',
                        "Status": 'ERROR CHECK',
                        "RegisteredContainerInstancesCount": 'ERROR CHECK',
                        "RunningTasksCount": 'ERROR CHECK',
                        "PendingTasksCount": 'ERROR CHECK',
                        "ActiveServicesCount": 'ERROR CHECK',
                        "capacityProviders": list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("ecs.list_clusters(),%s", othererr)
    results.append( { "ClusterArn" : 'ERROR CHECK',
                      "ECSClusterName" : 'ERROR CHECK',
                      "ECSClusterTName" : 'ERROR CHECK',
                      "Status": 'ERROR CHECK',
                      "RegisteredContainerInstancesCount": 'ERROR CHECK',
                      "RunningTasksCount": 'ERROR CHECK',
                      "PendingTasksCount": 'ERROR CHECK',
                      "ActiveServicesCount": 'ERROR CHECK',
                      "capacityProviders": list('ERROR CHECK'),
                    })
  finally:
    return results

def describe_clusters(cluster):
  '''
    describe ECS Cluster 
  '''
#   klogger_dat.debug('ecs-describe cluster')
  try:
    result = None
    ecs=boto3.client('ecs')
    ecsclusters = ecs.describe_clusters(clusters=[cluster])
    # klogger_dat.debug(ecsclusters)
    if 200 == ecsclusters["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger.debug(ecsclusters["clusters"])
      if ('failures' in ecsclusters) and (len(ecsclusters['failures']) > 0):
        klogger.debug(ecsclusters['failures'])
        return result
      if 'clusters' in ecsclusters: 
        result = ecsclusters['clusters'][0]
    else:
      klogger.error("call error : %d", ecsclusters["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("ecs.describe_clusters(),%s", othererr)
  finally:
    return result

def list_services(clusterArns):
  '''
    search ECS Cluster Services
  '''
  klogger_dat.debug('ecs service')
  try:
    results = [] 
    ecs=boto3.client('ecs')
    # klogger.debug(clusterArns)
    for clusterArn in clusterArns :
      if (clusterArn == ' ') : # Not Exist Cluster
        continue
      services = ecs.list_services(cluster=clusterArn)
      # klogger_dat.debug(services)
      if 200 == services["ResponseMetadata"]["HTTPStatusCode"]:
      #   klogger_dat.debug(services["serviceArns"])
        if 'serviceArns' in services and len(services["serviceArns"]) > 0 : 
          for service in services["serviceArns"]:
            # klogger_dat.debug(service)
            service_desc = describe_services(clusterArn, service)
            if service_desc != None :
              # klogger.debug(service_desc)
              # ECS Cluster Service Tag중 Name 값
              tagname = 'Not Exist Name Tag'
              if 'tags' in service_desc:
                for tag in service_desc['tags']:
                  if 'Name' == tag['key']:
                    tagname = tag['value']
                    break
              loadbalancers = service_desc['loadBalancers'] if 'loadBalancers' in service_desc else []
              serviceregistries = service_desc['serviceRegistries'] if 'serviceRegistries' in service_desc else []
              deployments = service_desc['deployments'] if 'deployments' in service_desc else []
              placementcontstraints = service_desc['placementConstraints'] if 'placementConstraints' in service_desc else []
              placementstrategy = service_desc['placementStrategy'] if 'placementStrategy' in service_desc else []
              subnetids = []; securitygroups = []; assignpublicip  = '';
              if 'networkConfiguration' in service_desc:
                if 'awsvpcConfiguration' in service_desc['networkConfiguration']:
                  subnetids = service_desc['networkConfiguration']['awsvpcConfiguration']['subnets']
                  securitygroups = service_desc['networkConfiguration']['awsvpcConfiguration']['securityGroups']
                  assignpublicip = service_desc['networkConfiguration']['awsvpcConfiguration']['assignPublicIp']
              # list count sync with space
              utils.ListSyncCountWithSpace(loadbalancers, serviceregistries, deployments, placementcontstraints,
                                           placementstrategy, subnetids, securitygroups)
  
              results.append( { "ClusterArn" : clusterArn,
                                "ECSClusterName" : ' ',
                                "ServiceArn" : ' ',
                                "ServiceName": service_desc['registeredContainerInstancesCount'],
                                "ServiceTName": tagname,
                                "Status": service_desc['status'],
                                "LoadBalancers": loadbalancers,
                                "ServiceRegistries": serviceregistries,
                                "DesiredCount": service_desc['desiredCount'] if 'desiredCount' in service_desc else ' ',
                                "RunningCount": service_desc['runningCount'] if 'runningCount' in service_desc else ' ',
                                "PendingCount": service_desc['pendingCount'] if 'pendingCount' in service_desc else ' ',
                                "LaunchType": service_desc['launchType'] if 'launchType' in service_desc else ' ',
                                "PlatformVersion": service_desc['platformVersion'] if 'platformVersion' in service_desc else ' ',
                                "PlatformFamily": service_desc['platformFamily'] if 'platformFamily' in service_desc else ' ',
                                "TaskDefinition": service_desc['taskDefinition'] if 'taskDefinition' in service_desc else ' ',
                                "Deployments": deployments,
                                "RoleArn": service_desc['roleArn'] if 'roleArn' in service_desc else ' ',
                                "PlacementConstraints": placementcontstraints,
                                "PlacementStrategy": placementstrategy,
                                "SubnetId": subnetids,
                                "SubnetTName": ' ',
                                "SecurityGroup": securitygroups,
                                "SecurityGroupName": ' ',
                                "AssignPublicIp": assignpublicip,
                                "CreatedBy": service_desc['createdBy'] if 'createdBy' in service_desc else ' ',
                              })
            else: # Can't Describe Cluster Service Info
              results.append( { "ClusterArn" : clusterArn,
                                "ECSClusterName" : ' ',
                                "ServiceArn" : ' ',
                                "ServiceName": ' ',
                                "ServiceTName": ' ',
                                "Status": ' ',
                                "LoadBalancers": ' ',
                                "ServiceRegistries": ' ',
                                "DesiredCount": ' ',
                                "RunningCount": ' ',
                                "PendingCount": ' ',
                                "LaunchType": ' ',
                                "PlatformVersion": ' ',
                                "PlatformFamily": ' ',
                                "TaskDefinition": ' ',
                                "Deployments": ' ',
                                "RoleArn": ' ',
                                "PlacementConstraints": ' ',
                                "PlacementStrategy": ' ',
                                "SubnetId": ' ',
                                "SubnetTName": ' ',
                                "SecurityGroup": ' ',
                                "SecurityGroupName": ' ',
                                "AssignPublicIp": ' ',
                                "CreatedBy": list(' '),
                              })
        else: # Not Exists Service Info
          results.append( { "ClusterArn" : clusterArn,
                            "ECSClusterName" : ' ',
                            "ServiceArn" : ' ',
                            "ServiceName": ' ',
                            "ServiceTName": ' ',
                            "Status": ' ',
                            "LoadBalancers": ' ',
                            "ServiceRegistries": ' ',
                            "DesiredCount": ' ',
                            "RunningCount": ' ',
                            "PendingCount": ' ',
                            "LaunchType": ' ',
                            "PlatformVersion": ' ',
                            "PlatformFamily": ' ',
                            "TaskDefinition": ' ',
                            "Deployments": ' ',
                            "RoleArn": ' ',
                            "PlacementConstraints": ' ',
                            "PlacementStrategy": ' ',
                            "SubnetId": ' ',
                            "SubnetTName": ' ',
                            "SecurityGroup": ' ',
                            "SecurityGroupName": ' ',
                            "AssignPublicIp": ' ',
                            "CreatedBy": list(' '),
                          })
      else:
        klogger.error("call error : %d", services["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "ClusterArn" : 'ERROR CHECK',
                          "ECSClusterName" : 'ERROR CHECK',
                          "ServiceArn" : 'ERROR CHECK',
                          "ServiceName": 'ERROR CHECK',
                          "ServiceTName": 'ERROR CHECK',
                          "Status": 'ERROR CHECK',
                          "LoadBalancers": 'ERROR CHECK',
                          "ServiceRegistries": 'ERROR CHECK',
                          "DesiredCount": 'ERROR CHECK',
                          "RunningCount": 'ERROR CHECK',
                          "PendingCount": 'ERROR CHECK',
                          "LaunchType": 'ERROR CHECK',
                          "PlatformVersion": 'ERROR CHECK',
                          "PlatformFamily": 'ERROR CHECK',
                          "TaskDefinition": 'ERROR CHECK',
                          "Deployments": 'ERROR CHECK',
                          "RoleArn": 'ERROR CHECK',
                          "PlacementConstraints": 'ERROR CHECK',
                          "PlacementStrategy": 'ERROR CHECK',
                          "SubnetId": 'ERROR CHECK',
                          "SubnetTName": 'ERROR CHECK',
                          "SecurityGroup": 'ERROR CHECK',
                          "SecurityGroupName": 'ERROR CHECK',
                          "AssignPublicIp": 'ERROR CHECK',
                          "CreatedBy": list('ERROR CHECK'),
                        })

    if results == []: # Not Exist Service
      results.append( { "ClusterArn" : clusterArns,
                        "ECSClusterName" : ' ',
                        "ServiceArn" : ' ',
                        "ServiceName": ' ',
                        "ServiceTName": ' ',
                        "Status": ' ',
                        "LoadBalancers": ' ',
                        "ServiceRegistries": ' ',
                        "DesiredCount": ' ',
                        "RunningCount": ' ',
                        "PendingCount": ' ',
                        "LaunchType": ' ',
                        "PlatformVersion": ' ',
                        "PlatformFamily": ' ',
                        "TaskDefinition": ' ',
                        "Deployments": ' ',
                        "RoleArn": ' ',
                        "PlacementConstraints": ' ',
                        "PlacementStrategy": ' ',
                        "SubnetId": ' ',
                        "SubnetTName": ' ',
                        "SecurityGroup": ' ',
                        "SecurityGroupName": ' ',
                        "AssignPublicIp": ' ',
                        "CreatedBy": ' ',
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("ecs.list_services(),%s", othererr)
    results.append( { "ClusterArn" : 'ERROR CHECK',
                      "ECSClusterName" : 'ERROR CHECK',
                      "ServiceArn" : 'ERROR CHECK',
                      "ServiceName": 'ERROR CHECK',
                      "ServiceTName": 'ERROR CHECK',
                      "Status": 'ERROR CHECK',
                      "LoadBalancers": 'ERROR CHECK',
                      "ServiceRegistries": 'ERROR CHECK',
                      "DesiredCount": 'ERROR CHECK',
                      "RunningCount": 'ERROR CHECK',
                      "PendingCount": 'ERROR CHECK',
                      "LaunchType": 'ERROR CHECK',
                      "PlatformVersion": 'ERROR CHECK',
                      "PlatformFamily": 'ERROR CHECK',
                      "TaskDefinition": 'ERROR CHECK',
                      "Deployments": 'ERROR CHECK',
                      "RoleArn": 'ERROR CHECK',
                      "PlacementConstraints": 'ERROR CHECK',
                      "PlacementStrategy": 'ERROR CHECK',
                      "SubnetId": 'ERROR CHECK',
                      "SubnetTName": 'ERROR CHECK',
                      "SecurityGroup": 'ERROR CHECK',
                      "SecurityGroupName": 'ERROR CHECK',
                      "AssignPublicIp": 'ERROR CHECK',
                      "CreatedBy": list('ERROR CHECK'),
                    })
  finally:
    return results

def describe_services(clusterArn, service):
  '''
    describe ECS Cluster Services
  '''
#   klogger_dat.debug('ecs-describe service')
  try:
    result = None
    ecs=boto3.client('ecs')
    services = ecs.describe_services(cluster=clusterArn, services=[service])
    # klogger_dat.debug(services)
    if 200 == services["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger.debug(services["services"])
      if ('failures' in services) and (len(services['failures']) > 0):
        klogger.debug(services['failures'])
        return result
      if 'services' in services: 
        result = services['services'][0]
    else:
      klogger.error("call error : %d", services["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("ecs.describe_services(),%s", othererr)
  finally:
    return result

def main(argv):

  list_clusters() 
  list_services([' '])

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
