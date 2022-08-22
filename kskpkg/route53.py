####################################################################################################
# 
# Purpose : get list route53 info
# Source  : route53.py
# Usage   : python route53.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.20     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html
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

def list_hosted_zones():
  '''
    search hosted zone
  '''
  klogger_dat.debug('route53')
  try:
    results = [] 
    route53=boto3.client('route53')
    hosts = route53.list_hosted_zones()
    if 200 == hosts["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug(hosts["HostedZones"])
      if len(hosts["HostedZones"]) > 0:
        for host in hosts["HostedZones"]:
          linkedservices = list({'ServicePrincipal':host['LinkedService']['ServicePrincipal']}
                                 if 'LinkedService' in host else ' ')
          results.append( { "Id": host["Id"],
                            "Name" : host['Name'],
                            "Comment" : host['Config']['Comment'],
                            "Type" : 'Public' if not host['Config']['PrivateZone'] else 'Private',
                            "ResourceRecordSetCount" : host["ResourceRecordSetCount"],
                            "CallerReference" : host["CallerReference"],
                            "ResourceRecordSetCount" : host["ResourceRecordSetCount"],
                            "LinkedService" : linkedservices
                           })
      else: # column list
        results.append( { "Id": ' ',
                          "Name" : ' ',
                          "Comment" : ' ',
                          "Type" : ' ',
                          "ResourceRecordSetCount" : ' ',
                          "CallerReference" : ' ',
                          "ResourceRecordSetCount" : ' ',
                          "LinkedService" : list(' '),
                         })
    else:
      klogger.error("call error : %d", hosts["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "Id": 'ERROR CHECK',
                        "Name" : 'ERROR CHECK',
                        "Comment" : 'ERROR CHECK',
                        "Type" : 'ERROR CHECK',
                        "ResourceRecordSetCount" : 'ERROR CHECK',
                        "CallerReference" : 'ERROR CHECK',
                        "ResourceRecordSetCount" : 'ERROR CHECK',
                        "LinkedService" : list('ERROR CHECK'),
                       })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("route53.list_hosted_zones(),%s", othererr)
    results.append( { "Id": 'ERROR CHECK',
                      "Name" : 'ERROR CHECK',
                      "Comment" : 'ERROR CHECK',
                      "Type" : 'ERROR CHECK',
                      "ResourceRecordSetCount" : 'ERROR CHECK',
                      "CallerReference" : 'ERROR CHECK',
                      "ResourceRecordSetCount" : 'ERROR CHECK',
                      "LinkedService" : list('ERROR CHECK'),
                     })
  finally:
    return results

def list_resource_record_sets(searchHostZoneids):
  '''
    search record set zone
  '''
  klogger_dat.debug('route53_records')
  results = [] 
  for searchHostZoneid in searchHostZoneids:
    try:
      route53=boto3.client('route53')
      # path에서 id 만 추출
      shostzoneid = searchHostZoneid.split("/")[-1:][0]
      records = route53.list_resource_record_sets(HostedZoneId=shostzoneid)
      if 200 == records["ResponseMetadata"]["HTTPStatusCode"]:
        # klogger_dat.debug(records["ResourceRecordSets"])
        if len(records["ResourceRecordSets"]) > 0:
          for record in records["ResourceRecordSets"]:
            resourcerecords = []
            if 'ResourceRecords' in record :
              for resourcerecord in record['ResourceRecords']:
                resourcerecords.append(resourcerecord['Value'])
            else:
              resourcerecords.append('')
            setidentifier = record['SetIdentifier'] if 'SetIdentifier' in record else ' '
            multivalueanswer = record['MultiValueAnswer'] if 'MultiValueAnswer' in record else ' '
            callereference = record['CallerReference'] if 'CallerReference' in record else ' '
            resourcerecordsetcount = record['ResourceRecordSetCount'] if 'ResourceRecordSetCount' in record else ' '
            aliastarget = record['AliasTarget']['DNSName'] if 'AliasTarget' in record else ' '
            evaluatetargethealth = record['AliasTarget']['EvaluateTargetHealth'] if 'AliasTarget' in record else ' '
            
            results.append( { "HostedZoneId" : searchHostZoneid,
                              "Name": record["Name"],
                              "Type" : record['Type'],
                              "ResourceRecords" : resourcerecords,
                              "AliasTarget" : aliastarget,
                              "EvaluateTargetHealth" : evaluatetargethealth,
                              "SetIdentifier" : setidentifier,
                              "MultiValueAnswer" : multivalueanswer,
                              "CallerReference" : callereference,
                              "ResourceRecordSetCount" : resourcerecordsetcount,
                             })
        else: # column list
          results.append( { "HostedZoneId" : ' ',
                            "Name": ' ',
                            "Type" : ' ',
                            "ResourceRecords" : ' ',
                            "AliasTarget" : ' ',
                            "EvaluateTargetHealth" : ' ',
                            "SetIdentifier" : ' ',
                            "MultiValueAnswer" : ' ',
                            "CallerReference" : ' ',
                            "ResourceRecordSetCount" : list(' '),
                           })
      else:
        klogger.error("call error : %d", records["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "HostedZoneId" : 'ERROR CHECK',
                          "Name": 'ERROR CHECK',
                          "Type" : 'ERROR CHECK',
                          "ResourceRecords" : 'ERROR CHECK',
                          "AliasTarget" : 'ERROR CHECK',
                          "EvaluateTargetHealth" : 'ERROR CHECK',
                          "SetIdentifier" : 'ERROR CHECK',
                          "MultiValueAnswer" : 'ERROR CHECK',
                          "CallerReference" : 'ERROR CHECK',
                          "ResourceRecordSetCount" : list('ERROR CHECK'),
                         })
      # klogger.debug(results)
    except Exception as othererr:
      klogger.error("route53.list_resource_record_sets(),%s", othererr)
      results.append( { "HostedZoneId" : 'ERROR CHECK',
                        "Name": 'ERROR CHECK',
                        "Type" : 'ERROR CHECK',
                        "ResourceRecords" : 'ERROR CHECK',
                        "AliasTarget" : 'ERROR CHECK',
                        "EvaluateTargetHealth" : 'ERROR CHECK',
                        "SetIdentifier" : 'ERROR CHECK',
                        "MultiValueAnswer" : 'ERROR CHECK',
                        "CallerReference" : 'ERROR CHECK',
                        "ResourceRecordSetCount" : list('ERROR CHECK'),
                       })
    finally:
      pass
  return results

def main(argv):
  ###  set search region name to variable of searchRegions
  searchHostZoneids = ['/hostedzone/Z06810722G9MN5XIX81MG']
  list_hosted_zones() 
  list_resource_record_sets()
  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
