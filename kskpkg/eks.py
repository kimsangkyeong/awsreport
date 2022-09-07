####################################################################################################
# 
# Purpose   : get list eks info
# Source    : eks.py
# Usage     : python eks.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.22     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks.html
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
    search EKS Clusters 
  '''
  klogger_dat.debug('eks')
  try:
    results = [] 
    eks=boto3.client('eks')
    eksclusters = eks.list_clusters()
    # klogger_dat.debug(eksclusters)
    if 200 == eksclusters["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(eksclusters["clusters"])
      if len(eksclusters["clusters"]) > 0 : 
        for ekscluster in eksclusters["clusters"]:
        #   klogger_dat.debug(ekscluster)
          cluster_desc = describe_cluster(ekscluster)
          if cluster_desc != None :
            # klogger.debug(cluster_desc)
            subnetids = []; securitygrps = []; endpubaccess = 'FALSE'; endprivateaccess = 'FALSE';
            kubecidrs = ' '; pubacccidrs = ' '; oidcissuer = []; encryptkeyarn = [];
            if 'resourcesVpcConfig' in cluster_desc :
              if ('subnetIds' in cluster_desc['resourcesVpcConfig']) and (len(cluster_desc['resourcesVpcConfig']['subnetIds']) > 0):
                for subnetid in cluster_desc['resourcesVpcConfig']['subnetIds']:
                  subnetids.append(subnetid)
              if ('securityGroupIds' in cluster_desc['resourcesVpcConfig']) and (len(cluster_desc['resourcesVpcConfig']['securityGroupIds']) > 0):
                for securitygrp in cluster_desc['resourcesVpcConfig']['securityGroupIds']:
                  securitygrps.append(securitygrp)
              clustersgid = cluster_desc['resourcesVpcConfig']['clusterSecurityGroupId'] if 'clusterSecurityGroupId' in cluster_desc['resourcesVpcConfig'] else ' '
              vpcid = cluster_desc['resourcesVpcConfig']['vpcId'] if 'vpcId' in cluster_desc['resourcesVpcConfig'] else ' '
              if 'endpointPublicAccess' in cluster_desc['resourcesVpcConfig']:
                if cluster_desc['resourcesVpcConfig']['endpointPublicAccess']:
                  endpubaccess = "TRUE"
              if 'endpointPrivateAccess' in cluster_desc['resourcesVpcConfig']:
                if cluster_desc['resourcesVpcConfig']['endpointPrivateAccess']:
                  endprivateaccess = "TRUE"
              if ('publicAccessCidrs' in cluster_desc['resourcesVpcConfig']) and (len(cluster_desc['resourcesVpcConfig']['publicAccessCidrs']) > 0) :
                for cidr in cluster_desc['resourcesVpcConfig']['publicAccessCidrs']:
                  if pubacccidrs == ' ' :
                    pubacccidrs = cidr
                  else:
                    pubacccidrs = pubacccidrs + ',' + cidr
            if 'kubernetesNetworkConfig' in cluster_desc:
              if 'serviceIpv4Cidr' in cluster_desc['kubernetesNetworkConfig'] :
                kubecidrs = cluster_desc['kubernetesNetworkConfig']['serviceIpv4Cidr'] 
            if 'identity' in cluster_desc:
              oidcissuer.append(cluster_desc['identity']['oidc']['issuer'] if 'oidc' in cluster_desc['identity'] else ' ')
            if ('encryptionConfig' in cluster_desc) and ( len(cluster_desc['encryptionConfig']) > 0):
              for encryptconf in cluster_desc['encryptionConfig'] :
                if 'provider' in encryptconf : 
                  encryptkeyarn.append(encryptconf['provider']['keyArn'])
            # EKS Cluster Tag중 Name 값
            tagname = 'Not Exist Name Tag'
            if 'tags' in cluster_desc:
              if 'Name' in cluster_desc['tags']:
                tagname = cluster_desc['tags']['Name']
            rolearn = [];version = []; endpoint = [];
            rolearn.append(cluster_desc['roleArn'] if 'roleArn' in cluster_desc else ' ')
            version.append(cluster_desc['version'])
            endpoint.append(cluster_desc['endpoint'])
            # list count sync with space
            utils.ListSyncCountWithSpace(version, endpoint, rolearn, subnetids, securitygrps, 
                               oidcissuer, encryptkeyarn)
            results.append( { "EKSCluster" : cluster_desc['name'],
                              "Status": cluster_desc['status'],
                              "Arn": cluster_desc['arn'],
                              "Version": version,
                              "Endpoint": endpoint,
                              "RoleArn": rolearn,
                              "SubnetId": subnetids,
                              "SubnetTName": ' ',
                              "SecurityGroup": securitygrps,
                              "SecurityGroupName": ' ',
                              "ClusterSecurityGroupId": clustersgid,
                              "ClusterSecurityGroupName": ' ',
                              "VpcId": vpcid,
                              "VpcTName": ' ',
                              "EndpointPublicAccess": endpubaccess,
                              "EndpointPrivateAccess": endprivateaccess,
                              "PublicAccessCidrs" : pubacccidrs,
                              "KubernetesNetworkCidrs": kubecidrs,
                              "OIDCIssuer": oidcissuer,
                              "PlatformVersion": cluster_desc['platformVersion'] if 'platformVersion' in cluster_desc else ' ',
                              "EKSClusterTName": tagname,
                              "EncryptKeyAlias": '',
                              "EncryptKeyArn": encryptkeyarn
                            })
          else: # Can't Describe Cluster Info
            results.append( { "EKSCluster" : ekscluster,
                              "Status": ' ',
                              "Arn": ' ',
                              "Version": ' ',
                              "Endpoint": ' ',
                              "RoleArn": ' ',
                              "SubnetId": ' ',
                              "SubnetTName": ' ',
                              "SecurityGroup": ' ',
                              "SecurityGroupName": ' ',
                              "ClusterSecurityGroupId": ' ',
                              "ClusterSecurityGroupName": ' ',
                              "VpcId": ' ',
                              "VpcTName": ' ',
                              "EndpointPublicAccess": ' ',
                              "EndpointPrivateAccess": ' ',
                              "PublicAccessCidrs" : ' ',
                              "KubernetesNetworkCidrs": ' ',
                              "OIDCIssuer": ' ',
                              "PlatformVersion": ' ',
                              "Tags": ' ',
                              "EncryptKeyAlias": ' ',
                              "EncryptKeyArn": list(' '),
                            })
      else: # Not Exists
        results.append( { "EKSCluster" : ' ',
                          "Status": ' ',
                          "Arn": ' ',
                          "Version": ' ',
                          "Endpoint": ' ',
                          "RoleArn": ' ',
                          "SubnetId": ' ',
                          "SubnetTName": ' ',
                          "SecurityGroup": ' ',
                          "SecurityGroupName": ' ',
                          "ClusterSecurityGroupId": ' ',
                          "ClusterSecurityGroupName": ' ',
                          "VpcId": ' ',
                          "VpcTName": ' ',
                          "EndpointPublicAccess": ' ',
                          "EndpointPrivateAccess": ' ',
                          "PublicAccessCidrs" : ' ',
                          "KubernetesNetworkCidrs": ' ',
                          "OIDCIssuer": ' ',
                          "PlatformVersion": ' ',
                          "Tags": ' ',
                          "EncryptKeyAlias": ' ',
                          "EncryptKeyArn": list(' '),
                        })
    else:
      klogger.error("call error : %d", eksclusters["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "EKSCluster" : 'ERROR CHECK',
                        "Status": 'ERROR CHECK',
                        "Arn": 'ERROR CHECK',
                        "Version": 'ERROR CHECK',
                        "Endpoint": 'ERROR CHECK',
                        "RoleArn": 'ERROR CHECK',
                        "SubnetId": 'ERROR CHECK',
                        "SubnetTName": 'ERROR CHECK',
                        "SecurityGroup": 'ERROR CHECK',
                        "SecurityGroupName": 'ERROR CHECK',
                        "ClusterSecurityGroupId": 'ERROR CHECK',
                        "ClusterSecurityGroupName": 'ERROR CHECK',
                        "VpcId": 'ERROR CHECK',
                        "VpcTName": 'ERROR CHECK',
                        "EndpointPublicAccess": 'ERROR CHECK',
                        "EndpointPrivateAccess": 'ERROR CHECK',
                        "PublicAccessCidrs" : 'ERROR CHECK',
                        "KubernetesNetworkCidrs": 'ERROR CHECK',
                        "OIDCIssuer": 'ERROR CHECK',
                        "PlatformVersion": 'ERROR CHECK',
                        "Tags": 'ERROR CHECK',
                        "EncryptKeyAlias": 'ERROR CHECK',
                        "EncryptKeyArn": list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("eks.list_clusters(),%s", othererr)
    results.append( { "EKSCluster" : 'ERROR CHECK',
                      "Status": 'ERROR CHECK',
                      "Arn": 'ERROR CHECK',
                      "Version": 'ERROR CHECK',
                      "Endpoint": 'ERROR CHECK',
                      "RoleArn": 'ERROR CHECK',
                      "SubnetId": 'ERROR CHECK',
                      "SubnetTName": 'ERROR CHECK',
                      "SecurityGroup": 'ERROR CHECK',
                      "SecurityGroupName": 'ERROR CHECK',
                      "ClusterSecurityGroupId": 'ERROR CHECK',
                      "ClusterSecurityGroupName": 'ERROR CHECK',
                      "VpcId": 'ERROR CHECK',
                      "VpcTName": 'ERROR CHECK',
                      "EndpointPublicAccess": 'ERROR CHECK',
                      "EndpointPrivateAccess": 'ERROR CHECK',
                      "PublicAccessCidrs" : 'ERROR CHECK',
                      "KubernetesNetworkCidrs": 'ERROR CHECK',
                      "OIDCIssuer": 'ERROR CHECK',
                      "PlatformVersion": 'ERROR CHECK',
                      "Tags": 'ERROR CHECK',
                      "EncryptKeyAlias": 'ERROR CHECK',
                      "EncryptKeyArn": list('ERROR CHECK'),
                    })
  finally:
    return results

def describe_cluster(cluster):
  '''
    describe EKS Cluster 
  '''
#   klogger_dat.debug('eks-describe cluster')
  try:
    result = None
    eks=boto3.client('eks')
    ekscluster = eks.describe_cluster(name=cluster)
    # klogger_dat.debug(eksclusters)
    if 200 == ekscluster["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger.debug(ekscluster["cluster"])
      if 'cluster' in ekscluster: 
        result = ekscluster['cluster']
    else:
      klogger.error("call error : %d", ekscluster["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("eks.describe_cluster(),%s", othererr)
  finally:
    return result

def main(argv):

  list_clusters() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
