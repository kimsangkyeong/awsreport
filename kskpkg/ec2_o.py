####################################################################################################
# 
# Purpose : get list vpcs info
# Source  : ec.py
# Usage   : python ec.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2019.09.06     first create
#  1.1      2019.09.15     local logger assign to logger that made by main program.
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_vpcs 
#           result data info => Vpcs, result code info => ResponseMetadata 
#
#           API info : step1. logging config file setup : 'logging.conf'
#                      step2. logging.config.fileConfig('logging.conf')
#                      step3. logger = logging.getLogger('logConsoleTypeA')
#                      step4. logger.debug, info, warning, error, critical
#          
####################################################################################################
### This first line is for modules to work with Python 2 or 3
from __future__ import print_function
import os, sys, getopt
import json
import boto3
from config import awsglobal
import dictlist

### module global logger variable
global logger     
global logger_dat 
logger     = awsglobal.logger
logger_dat = awsglobal.logger_dat

def search_vpcid_from_tagname(ec2client,vpctagname):
  '''
    search VpcId from tag Name 
  '''
  try:
    vpcs = ec2client.describe_vpcs(Filters=[{'Name':'tag:Name', 'Values':[vpctagname]}])
    #print(vpcs)
    if 200 == vpcs["ResponseMetadata"]["HTTPStatusCode"]:
      for vpc in vpcs['Vpcs']:
        return vpc['VpcId'] 
    else:
      logger.error("call error : %d", vpcs["ResponseMetadata"]["HTTPStatusCode"])

  except Exception as othererr:
    logger.error("search_vpcid_from_tagname() %s", othererr)
    return ''

def search_tagname_from_vpcid(ec2client,vpcid):
  '''
    search tag Name from VpcId
  '''
  try:
    vpcs = ec2client.describe_vpcs(Filters=[{'Name':'vpc-id', 'Values':[vpcid]}])
    #print(vpcs)
    if 200 == vpcs["ResponseMetadata"]["HTTPStatusCode"]:
      for vpc in vpcs['Vpcs']:
        if 'Tags' in vpc:
          for tag in vpc['Tags']:
            if 'Name' == tag['Key']:
              return tag['Value']
      return ''
    else:
      logger.error("call error : %d", vpcs["ResponseMetadata"]["HTTPStatusCode"])
      return ''

  except Exception as othererr:
    logger.error("search_vpcid_from_tagname() %s", othererr)
    return False

vpcinfo = {'VpcId':'','CidrBlock':'','TagName':'','State':'','OwnerId':''}
def search_vpcid_and_tagname(vpc):
  '''
    search tag Name and VpcId
  '''
  try:
    vpcinfo['VpcId']      = vpc['VpcId']
    vpcinfo['CidrBlock']  = vpc['CidrBlock']
    vpcinfo['State']      = vpc['State']
    vpcinfo['OwnerId']    = vpc['OwnerId']
    for tag in  vpc['Tags']:
      if tag['Key'] == 'Name':
        vpcinfo['TagName'] = tag['Value']

    logger_dat.debug("%s %s %s %s %s", vpcinfo['VpcId'], vpcinfo['TagName'], vpcinfo['CidrBlock'], vpcinfo['State'], vpcinfo['OwnerId'])
    return True
  except Exception as othererr:
    logger.error("search_vpcid_and_tagname() %s", othererr)
    return False

def describe_vpcs(searchRegions): 
  '''
    search vpcs in searchRegions
  '''

  for region in searchRegions:
    try:

      ec2=boto3.client('ec2', region )
      vpcs = ec2.describe_vpcs()
  #    print(vpcs)
      if 200 == vpcs["ResponseMetadata"]["HTTPStatusCode"]:
        logger.debug("call success")
  #       logger_dat.debug(vpcs["Vpcs"])
        for vpc in vpcs["Vpcs"]:
          ### case1 : search tag Name and RouteTableId
          search_vpcid_and_tagname(vpc)

          ### case2 : describe vpc
          logger_dat.debug("--------< %s/%s/%s > ", vpcinfo['VpcId'], vpcinfo['TagName'], vpcinfo['CidrBlock'])
          datalist = dictlist.describe_dict("", vpc)
          for data in datalist:
            logger_dat.debug(data)

          # list clear
          del datalist[:]
      else:
        logger.error("call error : %d", vpcs["ResponseMetadata"]["HTTPStatusCode"])

    except Exception as othererr:
      logger.error("ec2.describe_vpcs(),region[%s],%s", region, othererr)

  return True

def main(argv):
  ###  set search region name to variable of searchRegions
  searchRegions = ['ap-northeast-2']
  describe_vpcs(searchRegions) 
  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
