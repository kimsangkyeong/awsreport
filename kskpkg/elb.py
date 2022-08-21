####################################################################################################
# 
# Purpose : get list ElasticLoadBalancer info
# Source  : elb.py
# Usage   : python elb.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.20     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elb.html
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

def describe_load_balancers():
  '''
    search load_balancers
  '''
  klogger_dat.debug('ELB')
  try:
    results = [] 
    elb=boto3.client('elbv2')
    loadbalancers = elb.describe_load_balancers()
    # klogger_dat.debug(loadbalancers)
    if 200 == loadbalancers["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(loadbalancers["LoadBalancers"])
      if len(loadbalancers["LoadBalancers"]) > 0 :
        for loadbalancer in loadbalancers["LoadBalancers"]:
        #   klogger_dat.debug(loadbalancer)
          availzons = []; availsubnetids = []; availsubnetnames = []; eip_ipaddrs = []; 
          eip_allocateids = []; privateaddrs = []; securitygroups = []; sgrpnames = [];
          if 'AvailabilityZones' in loadbalancer :
            for availzone in loadbalancer['AvailabilityZones'] :
              availzons.append(availzone['ZoneName'] if 'ZoneName' in availzone else ' ')
              availsubnetids.append(availzone['SubnetId'] if 'SubnetId' in availzone else ' ')
              availsubnetnames.append(' ')
              if 'LoadBalancerAddresses' in availzone:
                for eip in availzone['LoadBalancerAddresses']:
                  eip_ipaddrs.append(eip['IpAddress'] if 'IpAddress' in eip else ' ')
                  eip_allocateids.append(eip['AllocationId'] if 'AllocationId' in eip else ' ')
                  privateaddrs.append(eip['PrivateIPv4Address'] if 'PrivateIPv4Address' in eip else ' ')
          if 'SecurityGroups' in loadbalancer :
            for sg in loadbalancer['SecurityGroups']:
              securitygroups.append(sg)
              sgrpnames.append(' ')
          # list count sync
          len_availzons       = len(availzons)
          len_eip_ipaddrs     = len(eip_ipaddrs)
          len_securitygroups  = len(securitygroups)
          max_len = max(len_availzons,len_eip_ipaddrs,len_securitygroups)
          for ix in range(len_availzons, max_len):
            availzons.append(' ')
            availsubnetids.append(' ')
            availsubnetnames.append(' ')
          for ix in range(len_eip_ipaddrs, max_len):
            eip_ipaddrs.append(' ')
            eip_allocateids.append(' ')
            privateaddrs.append(' ')
          for ix in range(len_securitygroups, max_len):
            securitygroups.append(' ')
            sgrpnames.append(' ')
  
          results.append( { "LoadBalancerName": loadbalancer['LoadBalancerName'],
                            "Scheme" : loadbalancer['Scheme'],
                            "Type" : loadbalancer['Type'],
                            "Scheme" : loadbalancer['Scheme'],
                            "IpAddressType" : loadbalancer['IpAddressType'],
                            "State" : loadbalancer['State']['Code'],
                            "AvailableZoneName" : availzons,
                            "SubnetId" : availsubnetids,
                            "SubnetTName" : availsubnetnames,
                            "EIP_IpAddress" : eip_ipaddrs,
                            "EIP_AllocationId" : eip_allocateids,
                            "PrivateIPv4Address" : privateaddrs,
                            "SecurityGroupId" : securitygroups,
                            "SecurityGroupName" : sgrpnames,
                            "VpcId" : loadbalancer['VpcId'],
                            "VpcTName" : '',
                            "DNSName" : loadbalancer['DNSName'],
                            "CreatedTime" : loadbalancer['CreatedTime'].strftime("%Y-%m-%d %H:%M"),
                           })
      else: # column list
        results.append( { "LoadBalancerName": ' ',
                          "Scheme" : ' ',
                          "Type" : ' ',
                          "Scheme" : ' ',
                          "IpAddressType" : ' ',
                          "State" : ' ',
                          "AvailableZoneName" : ' ',
                          "SubnetId" : ' ',
                          "SubnetTName" : ' ',
                          "ELB_IpAddress" : ' ',
                          "ELB_AllocationId" : ' ',
                          "PrivateIPv4Address" : ' ',
                          "SecurityGroupId" : ' ',
                          "SecurityGroupName" : ' ',
                          "VpcId" : ' ',
                          "VpcTName" : ' ',
                          "DNSName" : ' ',
                          "CreatedTime" : list(' '),
                         })
        
    #   klogger.debug(results)
    else:
      klogger.error("call error : %d", loadbalancers["ResponseMetadata"]["HTTPStatusCode"])
  except Exception as othererr:
    klogger.error("elb.describe_load_balancers(),%s", othererr)
  return results

def main(argv):

  describe_load_balancers() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
