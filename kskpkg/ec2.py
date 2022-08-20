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
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
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
  klogger_dat.debug('internet gateway')
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      igws = ec2.describe_internet_gateways()
      if 200 == igws["ResponseMetadata"]["HTTPStatusCode"]:
        # klogger_dat.debug(igws["InternetGateways"])
        for igw in igws["InternetGateways"]:
          # klogger_dat.debug(igw)
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
  klogger_dat.debug('vpc')
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      vpcs = ec2.describe_vpcs()
      if 200 == vpcs["ResponseMetadata"]["HTTPStatusCode"]:
        #klogger_dat.debug(vpcs["Vpcs"])
        for vpc in vpcs["Vpcs"]:
          # vpc 할당 CIDR 값
          associateCidr = []; states = []
          for cidr in vpc['CidrBlockAssociationSet']:
            associateCidr.append(cidr['CidrBlock'])
            states.append(cidr['CidrBlockState']['State'])

          # vpc Tag중 Name 값
          tagname = 'Not Exist Name Tag'
          if 'Tags' in vpc:
            for tag in vpc['Tags']:
              if tag['Key'] == 'Name':
                tagname = tag['Value']
                break
          results.append( { "VpcId": vpc["VpcId"],
                            "VpcTName" : tagname,
                            "Cidr" : associateCidr,
                            "State" : states 
                          })
        #klogger.debug(results)
      else:
        klogger.error("call error : %d", vpcs["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as othererr:
       klogger.error("ec2.describe_vpcs(),region[%s],%s", region, othererr)
  return results

def describe_nat_gateways(searchRegions):
  '''
    search nats in searchRegions
  '''
  klogger_dat.debug('nat')
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      nats = ec2.describe_nat_gateways()
      if 200 == nats["ResponseMetadata"]["HTTPStatusCode"]:
        # klogger_dat.debug(nats["NatGateways"])
        for nat in nats["NatGateways"]:
          # nat assigned ip 값
          publicips = []; privateips = []
          if 'NatGatewayAddresses' in nat:
            for nataddr in nat['NatGatewayAddresses']:
              publicips.append(nataddr['PublicIp'])
              privateips.append(nataddr['PrivateIp'])
          # nat ConnectivityType 값
          connectivitytype = 'Not Setting'
          if 'ConnectivityType' in nat:
            connectivitytype = nat['ConnectivityType']
          # nat Tag중 Name 값 
          # * nat 정보가 모두 scalar 형식인 경우 대비 DataFrame 변환오류 회피위해 list 처리함
          tagname = [']Not Exist Name Tag']
          if 'Tags' in nat:
            for tag in nat['Tags']:
              if tag['Key'] == 'Name':
                tagname[0] = tag['Value']
                break
          results.append( { "NatGatewayId": nat["NatGatewayId"],
                            "NatGatewayTName" : tagname,
                            "State" : nat["State"],
                            "PublicIp" : publicips,
                            "PrivateIp" : privateips,
                            "ConnectivityType" : connectivitytype,
                            "SubnetId" : nat["SubnetId"],
                            "SubnetTName" : '',
                            "VpcId" : nat["VpcId"] ,
                            "VpcTName" : ''
                           })
        # klogger.debug(results)
      else:
        klogger.error("call error : %d", nats["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as othererr:
      klogger.error("ec2.describe_nat_gateways(),region[%s],%s", region, othererr)
  return results

def describe_subnets(searchRegions):
  '''
    search subnets in searchRegions
  '''
  klogger_dat.debug('subnet')
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      subnets = ec2.describe_subnets()
      if 200 == subnets["ResponseMetadata"]["HTTPStatusCode"]:
        # klogger_dat.debug(subnets["Subnets"])
        for subnet in subnets["Subnets"]:
          # subnet Tag중 Name 값 
          # * subnet 정보가 모두 scalar 형식인 경우 대비 DataFrame 변환오류 회피위해 list 처리함
          tagname = ['Not Exist Name Tag']
          if 'Tags' in subnet:
            for tag in subnet['Tags']:
              if tag['Key'] == 'Name':
                tagname[0] = tag['Value']
                break
          results.append( { "SubnetId": subnet["SubnetId"],
                            "SubnetTName" : tagname,
                            "State" : subnet["State"],
                            "CidrBlock" : subnet["CidrBlock"],
                            "AvailabilityZone" : subnet["AvailabilityZone"],
                            "AvailableIpAddressCount" : subnet["AvailableIpAddressCount"],
                            "VpcId" : subnet["VpcId"] ,
                            "VpcTName" : ''
                           })
        # klogger.debug(results)
      else:
        klogger.error("call error : %d", subnets["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as othererr:
      klogger.error("ec2.describe_subnets(),region[%s],%s", region, othererr)
  return results

def describe_route_tables(searchRegions):
  '''
    search route table in searchRegions
  '''
  klogger_dat.debug('route table')
  for region in searchRegions:
    try:
      results1 = []  # associate
      results2 = []  # route
      ec2=boto3.client('ec2', region )
      routers = ec2.describe_route_tables()
      if 200 == routers["ResponseMetadata"]["HTTPStatusCode"]:
        # klogger_dat.debug(routers["RouteTables"])
        for router in routers["RouteTables"]:
          # klogger_dat.debug(router)
          # results1  association
          rtbasids = []; routetableids = []; subnetids = []; gatewayids = []; states = []
          for associated in router["Associations"]:
            rtbasids.append(associated['RouteTableAssociationId'])
            routetableids.append(associated['RouteTableId'])
            states.append(associated['AssociationState']['State'])
            subnetids.append(associated["SubnetId"] if "SubnetId" in associated else 'Not Setting')
            gatewayids.append(associated["GatewayId"] if "GatewayId" in associated else 'Not Setting')

          # router Tag중 Name 값 
          tagname = 'Not Exist Name Tag'
          if 'Tags' in router:
            for tag in router['Tags']:
              if tag['Key'] == 'Name':
                tagname = tag['Value']
                break
          # RouteTable Assocations info
          results1.append( { "RouteTableId": router["RouteTableId"],
                             "RouteTableTName" : tagname,
                             "RouteTableAssociationId" : rtbasids,
                             "RouteTableId" : routetableids,
                             "SubnetId" : subnetids,
                             "SubnetTName" : subnetids,
                             "GatewayId" : gatewayids,
                             "State" : states,
                             "VpcId" : router["VpcId"] ,
                             "VpcTName" : ''
                            })
          # results2  route
          rstates = []; destcidrs = []; destplids = []; egressgwids = []; rgatewayids = [];
          instanceids = []; natids = []; tgwids = []; localgwids = []; carrgwids = [];
          networkinfids = []; vpcpeerids = []; corenarn = []; origins = [];
          for route in router['Routes']:
            rstates.append(route['State'])
            origins.append(route['Origin'])
            destcidrs.append(route["DestinationCidrBlock"] if "DestinationCidrBlock" in route else '')
            destplids.append(route["DestinationPrefixListId"] if "DestinationPrefixListId" in route else '')
            egressgwids.append(route["EgressOnlyInternetGatewayId"] if "EgressOnlyInternetGatewayId" in route else '')
            rgatewayids.append(route["GatewayId"] if "GatewayId" in route else '')
            instanceids.append(route["InstanceId"] if "InstanceId" in route else '')
            natids.append(route["NatGatewayId"] if "NatGatewayId" in route else '')
            tgwids.append(route["TransitGatewayId"] if "TransitGatewayId" in route else '')
            localgwids.append(route["LocalGatewayId"] if "LocalGatewayId" in route else '')
            carrgwids.append(route["CarrierGatewayId"] if "CarrierGatewayId" in route else '')
            networkinfids.append(route["NetworkInterfaceId"] if "NetworkInterfaceId" in route else '')
            vpcpeerids.append(route["VpcPeeringConnectionId"] if "VpcPeeringConnectionId" in route else '')
            corenarn.append(route["CoreNetworkArn"] if "CoreNetworkArn" in route else '')
          # RouteTable Route info
          results2.append( { "RouteTableId": router["RouteTableId"],
                             "RouteTableTName" : tagname,
                             "State" : rstates,
                             "DestinationCidrBlock" : destcidrs,
                             "GatewayId" : rgatewayids,
                             "NatGatewayId" : natids,
                             "DestinationPrefixListId" : destplids,
                             "EgressOnlyInternetGatewayId" : egressgwids,
                             "InstanceId" : instanceids,
                             "TransitGatewayId" : tgwids,
                             "LocalGatewayId" : localgwids,
                             "CarrierGatewayId" : carrgwids,
                             "NetworkInterfaceId" : networkinfids,
                             "VpcPeeringConnectionId" : vpcpeerids,
                             "CoreNetworkArn" : corenarn,
                             "Origin" : origins,
                             "VpcId" : router["VpcId"] ,
                             "VpcTName" : ''
                            })
        # klogger.debug(results1)
        # klogger.debug(results2)
      else:
        klogger.error("call error : %d", routers["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as othererr:
      klogger.error("ec2.describe_route_tables(),region[%s],%s", region, othererr)
  return results1, results2

def describe_instances(searchRegions):
  '''
    search instances in searchRegions
  '''
  klogger_dat.debug('ec2')
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
            platform = ins["Platform"] if "Platform" in ins else "Not Setting"
            # KeyName 값
            keyname = ins["KeyName"] if "KeyName" in ins else "Not Setting"
            # pubipaddr 값
            pubipaddr = ins["PublicIpAddress"] if "PublicIpAddress" in ins else "Not Setting"
            # iaminsprofile 값
            iaminsprofile = ins["IamInstanceProfile"]["Arn"] if "IamInstanceProfile" in ins else "Not Setting"
            # securitygroups 값
            securitygroups = []
            for sg in ins["SecurityGroups"]:
              securitygroups.append( {sg["GroupName"]:sg["GroupId"]} )
            # ins Tag중 Name 값
            tagname = 'Not Exist Name Tag'
            if 'Tags' in ins:
              for tag in ins['Tags']:
                if tag['Key'] == 'Name':
                  tagname = tag['Value']
                  break

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
                              "SubnetTName" : '',
                              "VpcId" : ins["VpcId"],
                              "VpcTName" : '',
                              "EbsOptimized" : ins["EbsOptimized"],
                              "IamInstanceProfile" : iaminsprofile,
                              "SecurityGroups" : securitygroups
                          })
        # klogger.debug(results)
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
  describe_subnets(searchRegions) 
  describe_route_tables(searchRegions) 
  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
