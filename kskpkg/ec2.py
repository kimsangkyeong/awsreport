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
#   import utils  오류
#  * global 변수를 공유하는 package 내의 모듈을 Main으로 실행할 때 import 하는 방법 확인 필요.

else:
  # Module 실행으로 상대 경로 
  from .config import awsglobal
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
  from . import utils

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
        if len(igws["InternetGateways"]) > 0:
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
                              "VpcTName" : '',
                            })
        else:  # column list
          results.append( { "InternetGatewayId": ' ',
                            "InternetGatewayTName" : ' ',
                            "AttachedVpcId" : ' ',
                            "VpcTName" : list(' '),
                          })
      else:
        klogger.error("call error : %d", igws["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "InternetGatewayId": 'ERROR CHECK',
                          "InternetGatewayTName" : 'ERROR CHECK',
                          "AttachedVpcId" : 'ERROR CHECK',
                          "VpcTName" : list('ERROR CHECK'),
                        })
      # klogger.debug(results)
    except Exception as othererr:
      klogger.error("ec2.describe_internet_gateways(),region[%s],%s", region, othererr)
      results.append( { "InternetGatewayId": 'ERROR CHECK',
                        "InternetGatewayTName" : 'ERROR CHECK',
                        "AttachedVpcId" : 'ERROR CHECK',
                        "VpcTName" : list('ERROR CHECK'),
                      })
    finally:
      pass
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
        if len(vpcs["Vpcs"]) > 0:
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
        else:  # column list
          results.append( { "VpcId": ' ',
                            "VpcTName" : ' ',
                            "Cidr" : ' ',
                            "State" : list(' '),
                          })
      else:
        klogger.error("call error : %d", vpcs["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "VpcId": 'ERROR CHECK',
                          "VpcTName" : 'ERROR CHECK',
                          "Cidr" : 'ERROR CHECK',
                          "State" : list('ERROR CHECK'),
                        })
      #klogger.debug(results)
    except Exception as othererr:
      klogger.error("ec2.describe_vpcs(),region[%s],%s", region, othererr)
      results.append( { "VpcId": 'ERROR CHECK',
                        "VpcTName" : 'ERROR CHECK',
                        "Cidr" : 'ERROR CHECK',
                        "State" : list('ERROR CHECK'),
                      })
    finally:
      pass
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
        if len(nats["NatGateways"]) > 0:
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
            tagname = ['Not Exist Name Tag']
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
        else:  # column list
          results.append( { "NatGatewayId": ' ',
                            "NatGatewayTName" : ' ',
                            "State" : ' ',
                            "PublicIp" : ' ',
                            "PrivateIp" : ' ',
                            "ConnectivityType" : ' ',
                            "SubnetId" : ' ',
                            "SubnetTName" : ' ',
                            "VpcId" : ' ',
                            "VpcTName" : list(' '),
                          })
      else:
        klogger.error("call error : %d", nats["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "NatGatewayId": 'ERROR CHECK',
                          "NatGatewayTName" : 'ERROR CHECK',
                          "State" : 'ERROR CHECK',
                          "PublicIp" : 'ERROR CHECK',
                          "PrivateIp" : 'ERROR CHECK',
                          "ConnectivityType" : 'ERROR CHECK',
                          "SubnetId" : 'ERROR CHECK',
                          "SubnetTName" : 'ERROR CHECK',
                          "VpcId" : 'ERROR CHECK',
                          "VpcTName" : list('ERROR CHECK'),
                        })
      # klogger.debug(results)
    except Exception as othererr:
      klogger.error("ec2.describe_nat_gateways(),region[%s],%s", region, othererr)
      results.append( { "NatGatewayId": 'ERROR CHECK',
                        "NatGatewayTName" : 'ERROR CHECK',
                        "State" : 'ERROR CHECK',
                        "PublicIp" : 'ERROR CHECK',
                        "PrivateIp" : 'ERROR CHECK',
                        "ConnectivityType" : 'ERROR CHECK',
                        "SubnetId" : 'ERROR CHECK',
                        "SubnetTName" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : list('ERROR CHECK'),
                      })
    finally:
      pass
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
        if len(subnets["Subnets"]) > 0:
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
        else:  # column list
          results.append( { "SubnetId": ' ',
                            "SubnetTName" : ' ',
                            "State" : ' ',
                            "CidrBlock" : ' ',
                            "AvailabilityZone" : ' ',
                            "AvailableIpAddressCount" : ' ',
                            "VpcId" : ' ',
                            "VpcTName" : list(' '),
                          })
      else:
        klogger.error("call error : %d", subnets["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "SubnetId": 'ERROR CHECK',
                          "SubnetTName" : 'ERROR CHECK',
                          "State" : 'ERROR CHECK',
                          "CidrBlock" : 'ERROR CHECK',
                          "AvailabilityZone" : 'ERROR CHECK',
                          "AvailableIpAddressCount" : 'ERROR CHECK',
                          "VpcId" : 'ERROR CHECK',
                          "VpcTName" : list('ERROR CHECK'),
                        })
      # klogger.debug(results)
    except Exception as othererr:
      klogger.error("ec2.describe_subnets(),region[%s],%s", region, othererr)
      results.append( { "SubnetId": 'ERROR CHECK',
                        "SubnetTName" : 'ERROR CHECK',
                        "State" : 'ERROR CHECK',
                        "CidrBlock" : 'ERROR CHECK',
                        "AvailabilityZone" : 'ERROR CHECK',
                        "AvailableIpAddressCount" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : list('ERROR CHECK'),
                      })
    finally:
      pass
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
        if len(routers["RouteTables"]) > 0:
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
        else:  # column list
          results1.append( { "RouteTableId": ' ',
                             "RouteTableTName" : ' ',
                             "RouteTableAssociationId" : ' ',
                             "RouteTableId" : ' ',
                             "SubnetId" : ' ',
                             "SubnetTName" : ' ',
                             "GatewayId" : ' ',
                             "State" : ' ',
                             "VpcId" : ' ',
                             "VpcTName" : list(' '),
                            })
          results2.append( { "RouteTableId": ' ',
                            "RouteTableTName" : ' ',
                            "State" : ' ',
                            "DestinationCidrBlock" : ' ',
                            "GatewayId" : ' ',
                            "NatGatewayId" : ' ',
                            "DestinationPrefixListId" : ' ',
                            "EgressOnlyInternetGatewayId" : ' ',
                            "InstanceId" : ' ',
                            "TransitGatewayId" : ' ',
                            "LocalGatewayId" : ' ',
                            "CarrierGatewayId" : ' ',
                            "NetworkInterfaceId" : ' ',
                            "VpcPeeringConnectionId" : ' ',
                            "CoreNetworkArn" : ' ',
                            "Origin" : ' ',
                            "VpcId" : ' ',
                            "VpcTName" : list(' '),
                          })
      else:
        klogger.error("call error : %d", routers["ResponseMetadata"]["HTTPStatusCode"])
        results1.append( { "RouteTableId": 'ERROR CHECK',
                           "RouteTableTName" : 'ERROR CHECK',
                           "RouteTableAssociationId" : 'ERROR CHECK',
                           "RouteTableId" : 'ERROR CHECK',
                           "SubnetId" : 'ERROR CHECK',
                           "SubnetTName" : 'ERROR CHECK',
                           "GatewayId" : 'ERROR CHECK',
                           "State" : 'ERROR CHECK',
                           "VpcId" : 'ERROR CHECK',
                           "VpcTName" : list('ERROR CHECK'),
                          })
        results2.append( { "RouteTableId": 'ERROR CHECK',
                          "RouteTableTName" : 'ERROR CHECK',
                          "State" : 'ERROR CHECK',
                          "DestinationCidrBlock" : 'ERROR CHECK',
                          "GatewayId" : 'ERROR CHECK',
                          "NatGatewayId" : 'ERROR CHECK',
                          "DestinationPrefixListId" : 'ERROR CHECK',
                          "EgressOnlyInternetGatewayId" : 'ERROR CHECK',
                          "InstanceId" : 'ERROR CHECK',
                          "TransitGatewayId" : 'ERROR CHECK',
                          "LocalGatewayId" : 'ERROR CHECK',
                          "CarrierGatewayId" : 'ERROR CHECK',
                          "NetworkInterfaceId" : 'ERROR CHECK',
                          "VpcPeeringConnectionId" : 'ERROR CHECK',
                          "CoreNetworkArn" : 'ERROR CHECK',
                          "Origin" : 'ERROR CHECK',
                          "VpcId" : 'ERROR CHECK',
                          "VpcTName" : list('ERROR CHECK'),
                        })
      # klogger.debug(results1)
      # klogger.debug(results2)
    except Exception as othererr:
      klogger.error("ec2.describe_route_tables(),region[%s],%s", region, othererr)
      results1.append( { "RouteTableId": 'ERROR CHECK',
                         "RouteTableTName" : 'ERROR CHECK',
                         "RouteTableAssociationId" : 'ERROR CHECK',
                         "RouteTableId" : 'ERROR CHECK',
                         "SubnetId" : 'ERROR CHECK',
                         "SubnetTName" : 'ERROR CHECK',
                         "GatewayId" : 'ERROR CHECK',
                         "State" : 'ERROR CHECK',
                         "VpcId" : 'ERROR CHECK',
                         "VpcTName" : list('ERROR CHECK'),
                        })
      results2.append( { "RouteTableId": 'ERROR CHECK',
                        "RouteTableTName" : 'ERROR CHECK',
                        "State" : 'ERROR CHECK',
                        "DestinationCidrBlock" : 'ERROR CHECK',
                        "GatewayId" : 'ERROR CHECK',
                        "NatGatewayId" : 'ERROR CHECK',
                        "DestinationPrefixListId" : 'ERROR CHECK',
                        "EgressOnlyInternetGatewayId" : 'ERROR CHECK',
                        "InstanceId" : 'ERROR CHECK',
                        "TransitGatewayId" : 'ERROR CHECK',
                        "LocalGatewayId" : 'ERROR CHECK',
                        "CarrierGatewayId" : 'ERROR CHECK',
                        "NetworkInterfaceId" : 'ERROR CHECK',
                        "VpcPeeringConnectionId" : 'ERROR CHECK',
                        "CoreNetworkArn" : 'ERROR CHECK',
                        "Origin" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : list('ERROR CHECK'),
                      })
    finally:
      pass
  return results1, results2

def describe_security_groups(searchRegions):
  '''
    search security groups in searchRegions
  '''
  klogger_dat.debug('security groups')
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      sgs = ec2.describe_security_groups()
      if 200 == sgs["ResponseMetadata"]["HTTPStatusCode"]:
        # klogger_dat.debug("%s",sgs["SecurityGroups"])
        if len(sgs["SecurityGroups"]) > 0:
          for sg in sgs["SecurityGroups"]:
            # klogger_dat.debug("%s",sg)
            in_fromport = []; in_protocol = []; in_cidrip = []; in_desc = [];
            in_prefixlistid = []; in_pldesc =[]; in_toport = []; 
            in_grp_desc =[]; in_grp_groupid =[]; in_grp_groupname =[]; in_grp_peer =[]; 
            in_grp_userid =[]; in_grp_vpcid =[]; in_grp_vpcpeer =[];  
            out_fromport = []; out_protocol = []; out_cidrip = []; out_desc = [];
            out_prefixlistid = []; out_pldesc =[]; out_toport = []; 
            out_grp_desc =[]; out_grp_groupid =[]; out_grp_groupname =[]; out_grp_peer =[]; 
            out_grp_userid =[]; out_grp_vpcid =[]; out_grp_vpcpeer =[];  
            len_intotal  = 0; len_outtotal = 0;
            len_IpRanges = 0; len_PrefixListIds = 0; len_UserIdGroupPairs = 0;
            len_oIpRanges = 0; len_oPrefixListIds = 0; len_oUserIdGroupPairs = 0;
            
            if ('IpPermissions' in sg) and (len(sg['IpPermissions']) > 0) :
              for inrule in sg['IpPermissions']:
                in_fromport.append(inrule['FromPort'] if 'FromPort' in inrule else ' ')
                if 'IpProtocol' in inrule :
                  if inrule['IpProtocol'] == '-1' :
                    in_protocol.append('ALL')
                  else:
                    in_protocol.append(inrule['IpProtocol'])
                else:
                  in_protocol.append(' ')
                if 'IpRanges' in inrule :
                  len_IpRanges = len(inrule['IpRanges'])
                  for iprange in inrule['IpRanges']:
                    in_cidrip.append(iprange['CidrIp'] if 'CidrIp' in iprange else ' ')
                    in_desc.append(iprange['Description'] if 'Description' in iprange else ' ')
                else:
                  in_cidrip.append(' ')
                  in_desc.append(' ')
                if 'PrefixListIds' in inrule :
                  len_PrefixListIds = len(inrule['PrefixListIds'])
                  for prefixlist in inrule['PrefixListIds']:
                    in_prefixlistid.append(prefixlist['PrefixListId'] if 'PrefixListId' in prefixlist else ' ')
                    in_pldesc.append(prefixlist['Description'] if 'Description' in prefixlist else ' ')
                else:
                  in_prefixlistid.append(' ')
                  in_pldesc.append(' ')
                in_toport.append(inrule['ToPort'] if 'ToPort' in inrule else ' ')
                if 'UserIdGroupPairs' in inrule :
                  len_UserIdGroupPairs = len(inrule['UserIdGroupPairs'])
                  for grouppair in inrule['UserIdGroupPairs']:
                    in_grp_desc.append(grouppair['Description'] if 'Description' in grouppair else ' ')
                    in_grp_groupid.append(grouppair['GroupId'] if 'GroupId' in grouppair else ' ')
                    in_grp_groupname.append(grouppair['GroupName'] if 'GroupName' in grouppair else ' ')
                    in_grp_peer.append(grouppair['PeeringStatus'] if 'PeeringStatus' in grouppair else ' ')
                    in_grp_userid.append(grouppair['UserId'] if 'UserId' in grouppair else ' ')
                    in_grp_vpcid.append(grouppair['VpcId'] if 'VpcId' in grouppair else ' ')
                    in_grp_vpcpeer.append(grouppair['VpcPeeringConnectionId'] 
                                          if 'VpcPeeringConnectionId' in grouppair else ' ')
                else:
                  in_grp_desc.append(' ')
                  in_grp_groupid.append(' ')
                  in_grp_groupname.append(' ')
                  in_grp_peer.append(' ')
                  in_grp_userid.append(' ')
                  in_grp_vpcid.append(' ')
                  in_grp_vpcpeer.append(' ')
  
                max_len = max(len_IpRanges, len_PrefixListIds, len_UserIdGroupPairs)
                len_intotal = len_intotal + max(1, max_len)
                # klogger.debug(" in : intotal - %d,  max - %d, ip - %d, pr -%d, grp - %d", 
                #                 len_intotal, max_len, len_IpRanges, len_PrefixListIds, len_UserIdGroupPairs)
                # depth 1 필드, 갯수 보정하기
                for ix in range(1, max_len):
                  in_fromport.append(inrule['FromPort'] if 'FromPort' in inrule else ' ')
                  if 'IpProtocol' in inrule :
                    if inrule['IpProtocol'] == '-1' :
                      in_protocol.append('ALL')
                    else:
                      in_protocol.append(inrule['IpProtocol'])
                  else:
                    in_protocol.append(' ')
                  in_toport.append(inrule['ToPort'] if 'ToPort' in inrule else ' ')
                # dept 2 IpRanges 필드, 갯수 보정하기
                for ix in range(len_IpRanges, max_len):
                  in_cidrip.append(' ')
                  in_desc.append(' ')
                # dept 2 PrefixListIds 필드, 갯수 보정하기
                for ix in range(len_PrefixListIds, max_len):
                  in_prefixlistid.append(' ')
                  in_pldesc.append(' ')
                # dept 2 UserIdGroupPairs 필드, 갯수 보정하기
                for ix in range(len_UserIdGroupPairs, max_len):
                  in_grp_desc.append(' ')
                  in_grp_groupid.append(' ')
                  in_grp_groupname.append(' ')
                  in_grp_peer.append(' ')
                  in_grp_userid.append(' ')
                  in_grp_vpcid.append(' ')
                  in_grp_vpcpeer.append(' ')
            else: # Inbound Rule Not Exist
              len_intotal = 1;
              in_fromport.append(' ')
              in_protocol.append(' ')
              in_toport.append(' ')
              in_cidrip.append(' ')
              in_desc.append(' ')
              in_prefixlistid.append(' ')
              in_pldesc.append(' ')
              in_grp_desc.append(' ')
              in_grp_groupid.append(' ')
              in_grp_groupname.append(' ')
              in_grp_peer.append(' ')
              in_grp_userid.append(' ')
              in_grp_vpcid.append(' ')
              in_grp_vpcpeer.append(' ')
            if ('IpPermissionsEgress' in sg) and (len(sg['IpPermissionsEgress']) > 0) :
              for outrule in sg['IpPermissionsEgress']:
                out_fromport.append(outrule['FromPort'] if 'FromPort' in outrule else ' ')
                if 'IpProtocol' in outrule :
                  if outrule['IpProtocol'] == '-1' :
                    out_protocol.append('ALL')
                  else:
                    out_protocol.append(outrule['IpProtocol'])
                else:
                  out_protocol.append(' ')
                if 'IpRanges' in outrule :
                  len_oIpRanges = len(outrule['IpRanges'])
                  for iprange in outrule['IpRanges']:
                    out_cidrip.append(iprange['CidrIp'] if 'CidrIp' in iprange else ' ')
                    out_desc.append(iprange['Description'] if 'Description' in iprange else ' ')
                else:
                  out_cidrip.append(' ')
                  out_desc.append(' ')
                if 'PrefixListIds' in outrule :
                  len_oPrefixListIds = len(outrule['PrefixListIds'])
                  for prefixlist in outrule['PrefixListIds']:
                    out_prefixlistid.append(prefixlist['PrefixListId'] if 'PrefixListId' in prefixlist else ' ')
                    out_pldesc.append(prefixlist['Description'] if 'Description' in prefixlist else ' ')
                else:
                  out_prefixlistid.append(' ')
                  out_pldesc.append(' ')
                out_toport.append(outrule['ToPort'] if 'ToPort' in outrule else ' ')
                if 'UserIdGroupPairs' in outrule :
                  len_oUserIdGroupPairs = len(outrule['UserIdGroupPairs'])
                  for grouppair in outrule['UserIdGroupPairs']:
                    out_grp_desc.append(grouppair['Description'] if 'Description' in grouppair else ' ')
                    out_grp_groupid.append(grouppair['GroupId'] if 'GroupId' in grouppair else ' ')
                    out_grp_groupname.append(grouppair['GroupName'] if 'GroupName' in grouppair else ' ')
                    out_grp_peer.append(grouppair['PeeringStatus'] if 'PeeringStatus' in grouppair else ' ')
                    out_grp_userid.append(inrgrouppairule['UserId'] if 'UserId' in grouppair else ' ')
                    out_grp_vpcid.append(grouppair['VpcId'] if 'VpcId' in grouppair else ' ')
                    out_grp_vpcpeer.append(grouppair['VpcPeeringConnectionId'] 
                                          if 'VpcPeeringConnectionId' in grouppair else ' ')
                else:
                  out_grp_desc.append(' ')
                  out_grp_groupid.append(' ')
                  out_grp_groupname.append(' ')
                  out_grp_peer.append(' ')
                  out_grp_userid.append(' ')
                  out_grp_vpcid.append(' ')
                  out_grp_vpcpeer.append(' ')
                max_len = max(len_oIpRanges, len_oPrefixListIds, len_oUserIdGroupPairs)
                len_outtotal = len_outtotal + max(1, max_len)
                # klogger.debug(" in : outtotal - %d,  max - %d, ip - %d, pr -%d, grp - %d", 
                #                 len_outtotal, max_len, len_oIpRanges, len_oPrefixListIds, len_oUserIdGroupPairs)
                # depth 1 필드, 갯수 보정하기
                for ix in range(1, max_len):
                  out_fromport.append(outrule['FromPort'] if 'FromPort' in outrule else ' ')
                  if 'IpProtocol' in outrule :
                    if outrule['IpProtocol'] == '-1' :
                      out_protocol.append('ALL')
                    else:
                      out_protocol.append(outrule['IpProtocol'])
                  else:
                    out_protocol.append(' ')
                  out_toport.append(outrule['ToPort'] if 'ToPort' in outrule else ' ')
                # dept 2 IpRanges 필드, 갯수 보정하기
                for ix in range(len_oIpRanges, max_len):
                  out_cidrip.append(' ')
                  out_desc.append(' ')
                # dept 2 PrefixListIds 필드, 갯수 보정하기
                for ix in range(len_oPrefixListIds, max_len):
                  out_prefixlistid.append(' ')
                  out_pldesc.append(' ')
                # dept 2 UserIdGroupPairs 필드, 갯수 보정하기
                for ix in range(len_oUserIdGroupPairs, max_len):
                  out_grp_desc.append(' ')
                  out_grp_groupid.append(' ')
                  out_grp_groupname.append(' ')
                  out_grp_peer.append(' ')
                  out_grp_userid.append(' ')
                  out_grp_vpcid.append(' ')
                  out_grp_vpcpeer.append(' ')
            else: # Outbound Rule Not Exist
              len_outtotal = 1; 
              out_fromport.append(' ')
              out_protocol.append(' ')
              out_toport.append(' ')
              out_cidrip.append(' ')
              out_desc.append(' ')
              out_prefixlistid.append(' ')
              out_pldesc.append(' ')
              out_grp_desc.append(' ')
              out_grp_groupid.append(' ')
              out_grp_groupname.append(' ')
              out_grp_peer.append(' ')
              out_grp_userid.append(' ')
              out_grp_vpcid.append(' ')
              out_grp_vpcpeer.append(' ')

            # klogger.debug(" intotal : %d, outtotla : %d", len_intotal, len_outtotal)
            # 전체 in , out data gap 보정하기
            for ix in range(len_intotal, max(len_intotal, len_outtotal)):
              in_fromport.append(' ')
              in_protocol.append(' ')
              in_toport.append(' ')
              in_cidrip.append(' ')
              in_desc.append(' ')
              in_prefixlistid.append(' ')
              in_pldesc.append(' ')
              in_grp_desc.append(' ')
              in_grp_groupid.append(' ')
              in_grp_groupname.append(' ')
              in_grp_peer.append(' ')
              in_grp_userid.append(' ')
              in_grp_vpcid.append(' ')
              in_grp_vpcpeer.append(' ')            
            for ix in range(len_outtotal, max(len_intotal, len_outtotal)):
              out_fromport.append(' ')
              out_protocol.append(' ')
              out_toport.append(' ')
              out_cidrip.append(' ')
              out_desc.append(' ')
              out_prefixlistid.append(' ')
              out_pldesc.append(' ')
              out_grp_desc.append(' ')
              out_grp_groupid.append(' ')
              out_grp_groupname.append(' ')
              out_grp_peer.append(' ')
              out_grp_userid.append(' ')
              out_grp_vpcid.append(' ')
              out_grp_vpcpeer.append(' ')            
  
            sgdesc = sg["Description"] if 'Description' in sg else ' '
            # sg Tag중 Name 값
            tagname = 'Not Exist Name Tag'
            if 'Tags' in sg:
              for tag in sg['Tags']:
                if tag['Key'] == 'Name':
                  tagname = tag['Value']
                  break
            results.append( { "SGroupId": sg["GroupId"],
                              "SGroupName" : sg["GroupName"],
                              "SGroupTName" : tagname,
                              "Description" : sgdesc,
                              "In_IpProtocol" : in_protocol,
                              "In_FromPort" : in_fromport,
                              "In_ToPort" : in_toport,
                              "In_CidrIp" : in_cidrip,
                              "In_GroupId" : in_grp_groupid,
                              "In_GroupName" : in_grp_groupname,
                              "In_UserIdGroupPairs_Description" : in_grp_desc,
                              "In_Description" : in_desc,
                              "In_PrefixListId" : in_prefixlistid,
                              "In_PLDescription" : in_pldesc,
                              "In_PeeringStatus" : in_grp_peer,
                              "In_UserId" : in_grp_userid,
                              "In_VpcId" : in_grp_vpcid,
                              "In_VpcPeeringConnectionId" : in_grp_vpcpeer,
                              "Out_IpProtocol" : out_protocol,
                              "Out_FromPort" : out_fromport,
                              "Out_ToPort" : out_toport,
                              "Out_CidrIp" : out_cidrip,
                              "Out_Description" : out_desc,
                              "Out_GroupId" : out_grp_groupid,
                              "Out_GroupName" : out_grp_groupname,
                              "Out_UserIdGroupPairs_Description" : out_grp_desc,
                              "Out_PrefixListId" : out_prefixlistid,
                              "Out_PLDescription" : out_pldesc,
                              "Out_PeeringStatus" : out_grp_peer,
                              "Out_UserId" : out_grp_userid,
                              "Out_VpcId" : out_grp_vpcid,
                              "Out_VpcPeeringConnectionId" : out_grp_vpcpeer,
                              "VpcId" : sg["VpcId"],
                              "VpcTName" : '',
                          })
        else:  # column list
          results.append( { "SGroupId": ' ',
                            "SGroupName" : ' ',
                            "SGroupTName" : ' ',
                            "Description" : ' ',
                            "In_IpProtocol" : ' ',
                            "In_FromPort" : ' ',
                            "In_ToPort" : ' ',
                            "In_CidrIp" : ' ',
                            "In_GroupId" : ' ',
                            "In_GroupName" : ' ',
                            "In_UserIdGroupPairs_Description" : ' ',
                            "In_Description" : ' ',
                            "In_PrefixListId" : ' ',
                            "In_PLDescription" : ' ',
                            "In_PeeringStatus" : ' ',
                            "In_UserId" : ' ',
                            "In_VpcId" : ' ',
                            "In_VpcPeeringConnectionId" : ' ',
                            "Out_IpProtocol" : ' ',
                            "Out_FromPort" : ' ',
                            "Out_ToPort" : ' ',
                            "Out_CidrIp" : ' ',
                            "Out_Description" : ' ',
                            "Out_GroupId" : ' ',
                            "Out_GroupName" : ' ',
                            "Out_UserIdGroupPairs_Description" : ' ',
                            "Out_PrefixListId" : ' ',
                            "Out_PLDescription" : ' ',
                            "Out_PeeringStatus" : ' ',
                            "Out_UserId" : ' ',
                            "Out_VpcId" : ' ',
                            "Out_VpcPeeringConnectionId" : ' ',
                            "VpcId" : ' ',
                            "VpcTName" : list(' '),
                        })
      else:
        klogger.error("call error : %d", sgs["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "SGroupId": 'ERROR CHECK',
                          "SGroupName" : 'ERROR CHECK',
                          "SGroupTName" : 'ERROR CHECK',
                          "Description" : 'ERROR CHECK',
                          "In_IpProtocol" : 'ERROR CHECK',
                          "In_FromPort" : 'ERROR CHECK',
                          "In_ToPort" : 'ERROR CHECK',
                          "In_CidrIp" : 'ERROR CHECK',
                          "In_GroupId" : 'ERROR CHECK',
                          "In_GroupName" : 'ERROR CHECK',
                          "In_UserIdGroupPairs_Description" : 'ERROR CHECK',
                          "In_Description" : 'ERROR CHECK',
                          "In_PrefixListId" : 'ERROR CHECK',
                          "In_PLDescription" : 'ERROR CHECK',
                          "In_PeeringStatus" : 'ERROR CHECK',
                          "In_UserId" : 'ERROR CHECK',
                          "In_VpcId" : 'ERROR CHECK',
                          "In_VpcPeeringConnectionId" : 'ERROR CHECK',
                          "Out_IpProtocol" : 'ERROR CHECK',
                          "Out_FromPort" : 'ERROR CHECK',
                          "Out_ToPort" : 'ERROR CHECK',
                          "Out_CidrIp" : 'ERROR CHECK',
                          "Out_Description" : 'ERROR CHECK',
                          "Out_GroupId" : 'ERROR CHECK',
                          "Out_GroupName" : 'ERROR CHECK',
                          "Out_UserIdGroupPairs_Description" : 'ERROR CHECK',
                          "Out_PrefixListId" : 'ERROR CHECK',
                          "Out_PLDescription" : 'ERROR CHECK',
                          "Out_PeeringStatus" : 'ERROR CHECK',
                          "Out_UserId" : 'ERROR CHECK',
                          "Out_VpcId" : 'ERROR CHECK',
                          "Out_VpcPeeringConnectionId" : 'ERROR CHECK',
                          "VpcId" : 'ERROR CHECK',
                          "VpcTName" : list('ERROR CHECK'),
                      })
      # klogger_dat.debug(results)
    except Exception as othererr:
      klogger.error("ec2.describe_security_groups(),region[%s],%s", region, othererr)
      results.append( { "SGroupId": 'ERROR CHECK',
                        "SGroupName" : 'ERROR CHECK',
                        "SGroupTName" : 'ERROR CHECK',
                        "Description" : 'ERROR CHECK',
                        "In_IpProtocol" : 'ERROR CHECK',
                        "In_FromPort" : 'ERROR CHECK',
                        "In_ToPort" : 'ERROR CHECK',
                        "In_CidrIp" : 'ERROR CHECK',
                        "In_GroupId" : 'ERROR CHECK',
                        "In_GroupName" : 'ERROR CHECK',
                        "In_UserIdGroupPairs_Description" : 'ERROR CHECK',
                        "In_Description" : 'ERROR CHECK',
                        "In_PrefixListId" : 'ERROR CHECK',
                        "In_PLDescription" : 'ERROR CHECK',
                        "In_PeeringStatus" : 'ERROR CHECK',
                        "In_UserId" : 'ERROR CHECK',
                        "In_VpcId" : 'ERROR CHECK',
                        "In_VpcPeeringConnectionId" : 'ERROR CHECK',
                        "Out_IpProtocol" : 'ERROR CHECK',
                        "Out_FromPort" : 'ERROR CHECK',
                        "Out_ToPort" : 'ERROR CHECK',
                        "Out_CidrIp" : 'ERROR CHECK',
                        "Out_Description" : 'ERROR CHECK',
                        "Out_GroupId" : 'ERROR CHECK',
                        "Out_GroupName" : 'ERROR CHECK',
                        "Out_UserIdGroupPairs_Description" : 'ERROR CHECK',
                        "Out_PrefixListId" : 'ERROR CHECK',
                        "Out_PLDescription" : 'ERROR CHECK',
                        "Out_PeeringStatus" : 'ERROR CHECK',
                        "Out_UserId" : 'ERROR CHECK',
                        "Out_VpcId" : 'ERROR CHECK',
                        "Out_VpcPeeringConnectionId" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : list('ERROR CHECK'),
                    })
    finally:
      pass
  return results

def describe_network_interfaces(searchRegions):
  '''
    search eni in searchRegions
  '''
  klogger_dat.debug('ec2-eni')
  for region in searchRegions:
    try:
      results = [] 
      ec2=boto3.client('ec2', region )
      nets = ec2.describe_network_interfaces()
      if 200 == nets["ResponseMetadata"]["HTTPStatusCode"]:
        # klogger_dat.debug("%s",nets["NetworkInterfaces"])
        if len(nets["NetworkInterfaces"]) > 0:
          for net in nets["NetworkInterfaces"]:
              desc = net['Description'] if 'Description' in net else ''
              if 'Association' in net :
                publicip = net['Association']['PublicIp'] if 'PublicIp' in net['Association'] else ' '
                publicdnsname = net['Association']['PublicDnsName'] if 'PublicDnsName' in net['Association'] else ' '
              else:
                publicip = ''
                publicdnsname = ''
              if 'Attachment' in net :
                attach_instanceid = net['Attachment']['InstanceId'] if 'InstanceId' in net['Attachment'] else ' '
                attach_instanceownerid = net['Attachment']['InstanceOwnerId'] if 'InstanceOwnerId' in net['Attachment'] else ' '
                attach_deviceindex = net['Attachment']['DeviceIndex'] if 'DeviceIndex' in net['Attachment'] else ' '
                attach_networkcardindex = net['Attachment']['NetworkCardIndex'] if 'NetworkCardIndex' in net['Attachment'] else ' '
              else:
                attach_instanceid = ''
                attach_deviceindex = ''
                attach_networkcardindex = ''
                attach_instanceownerid = ''
              privateipaddrs = []; len_privateipaddrs = 1;
              if 'PrivateIpAddresses' in net :
                for ipaddr in net['PrivateIpAddresses']:
                  if 'Association' in ipaddr:
                    privateipaddrs.append({'Primary':ipaddr['Primary'], 
                                           'PrivateIpAddress':ipaddr['PrivateIpAddress'],
                                           'PublicIp':ipaddr['Association']['PublicIp'],
                                           'PublicDnsName':ipaddr['Association']['PublicDnsName']})
                  else:
                    privateipaddrs.append({'Primary':ipaddr['Primary'], 
                                           'PrivateIpAddress':ipaddr['PrivateIpAddress']})
              else:
                privateipaddrs.append(' ')
              sgroupids = []; sgroupnames = []; len_sgroups = 1;
              if 'Groups' in net :
                for sgroup in net['Groups']:
                  sgroupids.append(sgroup['GroupId'])
                  sgroupnames.append(sgroup['GroupName'])
              else:
                sgroupids.append(' ')
                sgroupnames.append(' ')
              # list count sync with space
              utils.ListSyncCountWithSpace(privateipaddrs, sgroupids, sgroupnames)              

              # net Tag중 Name 값
              tagname = 'Not Exist Name Tag'
              if 'TagSet' in net:
                for tag in net['TagSet']:
                  if tag['Key'] == 'Name':
                    tagname = tag['Value']
                    break
              results.append( { "NetworkInterfaceId": net["NetworkInterfaceId"],
                                "Status" : net["Status"],
                                "InterfaceType" : net["InterfaceType"],
                                "Description" : desc,
                                "AvailabilityZone" : net["AvailabilityZone"],
                                "PrivateIpAddress" : net["PrivateIpAddress"],
                                "PublicIp" : publicip,
                                "PublicDnsName" : publicdnsname,
                                "Attach_InstanceID" : attach_instanceid,
                                "Attach_InstanceOwnerID" : attach_instanceownerid,
                                "Attach_DeviceIndex" : attach_deviceindex,
                                "Attach_NetworkCardIndex" : attach_networkcardindex,
                                "ENITName" : tagname,
                                "PrivateIpAddresses" : privateipaddrs,
                                "SGroupId" : sgroupids,
                                "SGroupName": sgroupnames,
                                "SubnetId" : net["SubnetId"],
                                "SubnetTName" : '',
                                "VpcId" : net["VpcId"],
                                "VpcTName" : '',
                            })
        else:  # column list
          results.append( { "NetworkInterfaceId": ' ',
                            "Status" : ' ',
                            "InterfaceType" : ' ',
                            "Description" : ' ',
                            "AvailabilityZone" : ' ',
                            "PrivateIpAddress" : ' ',
                            "PublicIp" : ' ',
                            "PublicDnsName" : ' ',
                            "Attach_InstanceID" : ' ',
                            "Attach_InstanceOwnerID" : ' ',
                            "Attach_DeviceIndex" : ' ',
                            "Attach_NetworkCardIndex" : ' ',
                            "ENITName" : ' ',
                            "PrivateIpAddresses" : ' ',
                            "SGroupId" : ' ',
                            "SGroupName": ' ',
                            "SubnetId" : ' ',
                            "SubnetTName" : ' ',
                            "VpcId" : ' ',
                            "VpcTName" : list(' '),
                          })
      else:
        klogger.error("call error : %d", nets["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "NetworkInterfaceId": 'ERROR CHECK',
                          "Status" : 'ERROR CHECK',
                          "InterfaceType" : 'ERROR CHECK',
                          "Description" : 'ERROR CHECK',
                          "AvailabilityZone" : 'ERROR CHECK',
                          "PrivateIpAddress" : 'ERROR CHECK',
                          "PublicIp" : 'ERROR CHECK',
                          "PublicDnsName" : 'ERROR CHECK',
                          "Attach_InstanceID" : 'ERROR CHECK',
                          "Attach_InstanceOwnerID" : 'ERROR CHECK',
                          "Attach_DeviceIndex" : 'ERROR CHECK',
                          "Attach_NetworkCardIndex" : 'ERROR CHECK',
                          "ENITName" : 'ERROR CHECK',
                          "PrivateIpAddresses" : 'ERROR CHECK',
                          "SGroupId" : 'ERROR CHECK',
                          "SGroupName": 'ERROR CHECK',
                          "SubnetId" : 'ERROR CHECK',
                          "SubnetTName" : 'ERROR CHECK',
                          "VpcId" : 'ERROR CHECK',
                          "VpcTName" : list('ERROR CHECK'),
                        })
      # klogger.debug(results)
    except Exception as othererr:
      klogger.error("ec2.describe_network_interfaces(),region[%s],%s", region, othererr)
      results.append( { "NetworkInterfaceId": 'ERROR CHECK',
                        "Status" : 'ERROR CHECK',
                        "InterfaceType" : 'ERROR CHECK',
                        "Description" : 'ERROR CHECK',
                        "AvailabilityZone" : 'ERROR CHECK',
                        "PrivateIpAddress" : 'ERROR CHECK',
                        "PublicIp" : 'ERROR CHECK',
                        "PublicDnsName" : 'ERROR CHECK',
                        "Attach_InstanceID" : 'ERROR CHECK',
                        "Attach_InstanceOwnerID" : 'ERROR CHECK',
                        "Attach_DeviceIndex" : 'ERROR CHECK',
                        "Attach_NetworkCardIndex" : 'ERROR CHECK',
                        "ENITName" : 'ERROR CHECK',
                        "PrivateIpAddresses" : 'ERROR CHECK',
                        "SGroupId" : 'ERROR CHECK',
                        "SGroupName": 'ERROR CHECK',
                        "SubnetId" : 'ERROR CHECK',
                        "SubnetTName" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : list('ERROR CHECK'),
                      })
    finally:
      pass
  return results


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
        # klogger_dat.debug("%s",inss["Reservations"])
        if len(inss["Reservations"]) > 0 :
          for rsv in inss["Reservations"]:
            for ins in rsv["Instances"]:
              # klogger_dat.debug("%s",ins) 
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
        else:  # column list
          results.append( { "InstanceId": ' ',
                            "InstanceTName" : ' ',
                            "Platform" : ' ',
                            "Architecture" : ' ',
                            "InstanceType" : ' ',
                            "KeyName" : ' ',
                            "Placement" : ' ',
                            "PrivateIpAddress" : ' ',
                            "PublicIpAddress" : ' ',
                            "SubnetId" : ' ',
                            "SubnetTName" : ' ',
                            "VpcId" : ' ',
                            "VpcTName" : ' ',
                            "EbsOptimized" : ' ',
                            "IamInstanceProfile" : ' ',
                            "SecurityGroups" : list(' '),
                          })
      else:
        klogger.error("call error : %d", inss["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "InstanceId": 'ERROR CHECK',
                          "InstanceTName" : 'ERROR CHECK',
                          "Platform" : 'ERROR CHECK',
                          "Architecture" : 'ERROR CHECK',
                          "InstanceType" : 'ERROR CHECK',
                          "KeyName" : 'ERROR CHECK',
                          "Placement" : 'ERROR CHECK',
                          "PrivateIpAddress" : 'ERROR CHECK',
                          "PublicIpAddress" : 'ERROR CHECK',
                          "SubnetId" : 'ERROR CHECK',
                          "SubnetTName" : 'ERROR CHECK',
                          "VpcId" : 'ERROR CHECK',
                          "VpcTName" : 'ERROR CHECK',
                          "EbsOptimized" : 'ERROR CHECK',
                          "IamInstanceProfile" : 'ERROR CHECK',
                          "SecurityGroups" : list('ERROR CHECK'),
                        })
      # klogger.debug(results)
    except Exception as othererr:
      klogger.error("ec2.describe_instances(),region[%s],%s", region, othererr)
      results.append( { "InstanceId": 'ERROR CHECK',
                        "InstanceTName" : 'ERROR CHECK',
                        "Platform" : 'ERROR CHECK',
                        "Architecture" : 'ERROR CHECK',
                        "InstanceType" : 'ERROR CHECK',
                        "KeyName" : 'ERROR CHECK',
                        "Placement" : 'ERROR CHECK',
                        "PrivateIpAddress" : 'ERROR CHECK',
                        "PublicIpAddress" : 'ERROR CHECK',
                        "SubnetId" : 'ERROR CHECK',
                        "SubnetTName" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : 'ERROR CHECK',
                        "EbsOptimized" : 'ERROR CHECK',
                        "IamInstanceProfile" : 'ERROR CHECK',
                        "SecurityGroups" : list('ERROR CHECK'),
                      })
    finally:
      pass
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
  describe_security_groups(searchRegions) 
  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
