####################################################################################################
# 
# Purpose : get list vpcs info
# Source  : ec.py
# Usage   : python ec.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2019.09.06     first create
#  1.1      2019.09.15     local klogger assign to klogger that made by main program.
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_vpcs 
#           result data info => Vpcs, result code info => ResponseMetadata 
#
#           API info : step1. logging config file setup : 'logging.conf'
#                      step2. logging.config.fileConfig('logging.conf')
#                      step3. klogger = logging.getLogger('logConsoleTypeA')
#                      step4. klogger.debug, info, warning, error, critical
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

def describe_internet_gateways(searchRegions):
  '''
    search igws in searchRegions
  '''
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      igws = ec2.describe_internet_gateways()
      if 200 == igws["ResponseMetadata"]["HTTPStatusCode"]:
        # klogger_dat.debug(igws["InternetGateways"])
        for igw in igws["InternetGateways"]:
          klogger_dat.debug(igw)
          # igw assigned vcpid 값
          attachedvpcid = "Not Assigned"
          if 'Attachments' in igw:
            for attached in igw['Attachments']:
              if attached['State'] == 'available':
                attachedvpcid = attached['VpcId']
                break
          # igw Tag중 Name 값 
          # * igw 정보는 모두 scalar 형식이라서 DataFrame 변환오류 회피위해 list 처리함
          tagname = ['Not Exist Name Tag']
          if 'Tags' in igw:
            for tag in igw['Tags']:
              if tag['Key'] == 'Name':
                tagname[0] = tag['Value']
                break
          results.append( { "InternetGatewayId": igw["InternetGatewayId"],
                            "InternetGatewayTName" : tagname,
                            "AttachedVpcId" : attachedvpcid ,
                            "VpcTName" : ''
                           })
        # klogger.debug(results)
      else:
        klogger.error("call error : %d", igws["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as othererr:
       klogger.error("ec2.describe_internet_gateways(),region[%s],%s", region, othererr)
  return results

def describe_vpcs(searchRegions):
  '''
    search vpcs in searchRegions
  '''
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      vpcs = ec2.describe_vpcs()
      if 200 == vpcs["ResponseMetadata"]["HTTPStatusCode"]:
        #klogger_dat.debug(vpcs["Vpcs"])
        for vpc in vpcs["Vpcs"]:
          # vpc 할당 CIDR 값
          associateCidr = []
          for cidr in vpc['CidrBlockAssociationSet']:
            if cidr['CidrBlockState']['State'] == 'associated' :
              associateCidr.append({cidr['CidrBlock']:'use'})
            else:
              associateCidr.append({cidr['CidrBlock']:'nouse'})

          # vpc Tag중 Name 값
          tagname = 'Not Exist Name Tag'
          if 'Tags' in vpc:
            for tag in vpc['Tags']:
              if tag['Key'] == 'Name':
                tagname = tag['Value']
                break
          results.append( { "VpcId": vpc["VpcId"],
                            "VpcTName" : tagname,
                            "Cidr" : associateCidr })
        #klogger.debug(results)
      else:
        klogger.error("call error : %d", vpcs["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as othererr:
       klogger.error("ec2.describe_vpcs(),region[%s],%s", region, othererr)
  return results

def describe_nat_gateways(searchRegions):
  '''
    search nat in searchRegions
  '''
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      nats = ec2.describe_nat_gateways()
      if 200 == nats["ResponseMetadata"]["HTTPStatusCode"]:
        klogger_dat.debug(nats["InternetGateways"])
        for nat in nats["NatGateways"]:
          # igw assigned vcpid 값
          natgatewayaddresses = []
          if 'NatGatewayAddresses' in nat:
            for nataddr in nat['NatGatewayAddresses']:
              natgatewayaddresses.append({'PrivateIp':nataddr['PrivateIp']})
              natgatewayaddresses.append({'PublicIp':nataddr['PublicIp']})
              
          # nat Tag중 Name 값 
          # * nat 정보가 모두 scalar 형식인 경우 대비 DataFrame 변환오류 회피위해 list 처리함
          tagname = ['Not Exist Name Tag']
          if 'Tags' in nat:
            for tag in nat['Tags']:
              if tag['Key'] == 'Name':
                tagname[0] = tag['Value']
                break
          results.append( { "NatGatewayId": nat["NatGatewayId"],
                            "NatGatewayTName" : tagname,
                            "State" : nat["State"],
                            "ConnectivityType" : nat["ConnectivityType"],
                            "NatGatewayAddresses" : natgatewayaddresses,
                            "SubnetId" : nat["SubnetId"],
                            "VpcId" : nat["VpcId"] ,
                            "VpcTName" : ''
                           })
        klogger.debug(results)
      else:
        klogger.error("call error : %d", nats["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as othererr:
       klogger.error("ec2.describe_nat_gateways(),region[%s],%s", region, othererr)
  return results

def describe_instances(searchRegions):
  '''
    search instances in searchRegions
  '''
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      inss = ec2.describe_instances()
      if 200 == inss["ResponseMetadata"]["HTTPStatusCode"]:
#        klogger_dat.debug("%s",inss["Reservations"])
        for rsv in inss["Reservations"]:
          for ins in rsv["Instances"]:
#            klogger_dat.debug("%s",ins) 
            # Platform 값
            if not "Platform" in ins :
              platform = "Not Setting"
            else:
              platform = ins["Platform"] 

            # ins Tag중 Name 값
            tagname = 'Not Exist Name Tag'
            if 'Tags' in ins:
              for tag in ins['Tags']:
                if tag['Key'] == 'Name':
                  tagname = tag['Value']
                  break

            # KeyName 값
            if "KeyName" in ins:
              keyname = ins["KeyName"]
            else:
              keyname = 'Not Setting'

            # pubipaddr 값
            if "PublicIpAddress" in ins:
              pubipaddr = ins["PublicIpAddress"]
            else:
              pubipaddr = 'Not Setting'

            # iaminsprofile 값
            if "IamInstanceProfile" in ins:
              iaminsprofile = ins["IamInstanceProfile"]["Arn"]
            else:
              iaminsprofile = 'Not Setting'

            # securitygroups 값
            securitygroups = []
            for sg in ins["SecurityGroups"]:
              securitygroups.append( {sg["GroupName"]:sg["GroupId"]} )

            results.append( { "InstanceId": ins["InstanceId"],
                              "InstanceTName" : tagname,
                              "Platform" : platform,
                              "Architecture" : ins["Architecture"],
                              "InstanceType" : ins["InstanceType"],
                              "KeyName" : keyname,
                              "Placement" : ins["Placement"]["AvailabilityZone"],
                              "PrivateIpAddress" : ins["PrivateIpAddress"],
                              "PublicIpAddress" : pubipaddr,
                              "SubnetId" : ins["SubnetId"],
                              "VpcId" : ins["VpcId"],
                              "VpcTName" : '',
                              "EbsOptimized" : ins["EbsOptimized"],
                              "IamInstanceProfile" : iaminsprofile,
                              "SecurityGroups" : securitygroups
                          })
        klogger.debug(results)
      else:
        klogger.error("call error : %d", inss["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as othererr:
       klogger.error("ec2.describe_instances(),region[%s],%s", region, othererr)
  return results

def main(argv):
  ###  set search region name to variable of searchRegions
  searchRegions = ['ap-northeast-2']
  describe_vpcs(searchRegions) 
  describe_internet_gateways(searchRegions) 
  describe_nat_gateways(searchRegions)
  describe_instances(searchRegions) 
  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
