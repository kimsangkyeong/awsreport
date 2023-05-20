####################################################################################################
# 
# Purpose   : get list cloudfront info
# Source    : cloudfront.py
# Usage     : python cloudfront.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.30     first create
#  1.1      2023.05.17     add session handling logic
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html
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

def list_cloud_front_origin_access_identities():
  '''
    search cloudfront origin_access_identities
  '''
  klogger_dat.debug('cloudfront-origin_access_identities')
  try:
    results = [] 
    cloudfront = CLOUDFRONT_session
    oids = cloudfront.list_cloud_front_origin_access_identities()
    # klogger_dat.debug(oids)
    if 200 == oids["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(oids["CloudFrontOriginAccessIdentityList"])
      if 'Items' in oids["CloudFrontOriginAccessIdentityList"] and len(oids["CloudFrontOriginAccessIdentityList"]['Items']) > 0 :
        ids = []; s3cuids = []; comments = [];
        for oid in oids["CloudFrontOriginAccessIdentityList"]['Items']:
          # klogger_dat.debug(oid)
          ids.append(oid['Id'])
          s3cuids.append(oid['S3CanonicalUserId'])
          comments.append(oid['Comment'] if 'Comment' in oid else ' ')
        # list count sync with space
        utils.ListSyncCountWithSpace(ids, s3cuids, comments)
                
        results.append( { "Id": ids,
                          "S3CanonicalUserId" : s3cuids,
                          "Comment": comments,
                        })
      else: # column list
        results.append( { "Id": ' ',
                          "S3CanonicalUserId" : ' ',
                          "Comment" : list(' '),
                        })
    else:
      klogger.error("call error : %d", oids["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "Id": 'ERROR CHECK',
                        "S3CanonicalUserId" : 'ERROR CHECK',
                        "Comment" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("cloudfront.list_cloud_front_origin_access_identities(),%s", othererr)
    results.append( { "Id": 'ERROR CHECK',
                      "S3CanonicalUserId" : 'ERROR CHECK',
                      "Comment" : list('ERROR CHECK'),
                    })
  finally:
    return results

def list_distributions():
  '''
    search cloudfront distributions
  '''
  klogger_dat.debug('cloudfront-distributions')
  try:
    results = []
    global CLOUDFRONT_session

    CLOUDFRONT_session = utils.get_session('cloudfront')
    cloudfront = CLOUDFRONT_session
    distributions = cloudfront.list_distributions()
    # klogger_dat.debug(distributions)
    if 200 == distributions["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug(distributions["DistributionList"])
      if 'Items' in distributions["DistributionList"] and len(distributions["DistributionList"]['Items']) > 0 :
        ids = []; arns = []; status = []; domainnames = []; aliasitems = []; originitems =[];
        origingroupitems = []; defaultcachebehavior = []; cachebehaviors = []; customerrresponses = [];
        comments = []; priceclass = []; enableds = []; viewercertificates = []; webaclids = [];
        httpversions = [];
        for distribution in distributions["DistributionList"]['Items']:
          # klogger_dat.debug(distribution)
          ids.append(distribution['Id'])
          arns.append(distribution['ARN'])
          status.append(distribution['Status'])
          domainnames.append(distribution['DomainName'])
          webaclids.append(distribution['WebACLId'] if 'WebACLId' in distribution else ' ')
          httpversions.append(distribution['HttpVersion'])
          priceclass.append(distribution['PriceClass'])
          enableds.append('True' if distribution['Enabled'] else 'False')
          comments.append(distribution['Comment'] if 'Comment' in distribution else '')
          if 'ViewerCertificate' in distribution :
            cdcertificate = 'False'
            if 'CloudFrontDefaultCertificate' in distribution['ViewerCertificate'] :
              if distribution['ViewerCertificate']['CloudFrontDefaultCertificate'] :
                cdcertificate = 'True'
            iamcertificate = distribution['ViewerCertificate']['IAMCertificateId'] if 'IAMCertificateId' in  distribution['ViewerCertificate'] else ' '
            acmcertificate = distribution['ViewerCertificate']['ACMCertificateArn'] if 'ACMCertificateArn' in  distribution['ViewerCertificate'] else ' '
            certificate = distribution['ViewerCertificate']['Certificate'] if 'Certificate' in  distribution['ViewerCertificate'] else ' '
            viewercertificates.append({'CloudFrontDefaultCertificate' : cdcertificate,
                                       'IAMCertificateId' : iamcertificate,
                                       'ACMCertificateArn' : acmcertificate,
                                       'SSLSupportMethod' : distribution['ViewerCertificate']['SSLSupportMethod'],
                                       'MinimumProtocolVersion' : distribution['ViewerCertificate']['MinimumProtocolVersion'],
                                       'Certificate' : certificate,
                                       'CertificateSource' : distribution['ViewerCertificate']['CertificateSource']
                                      })
          if 'Aliases' in distribution :
            if 'Items' in distribution['Aliases'] :
              for item in distribution['Aliases']['Items'] :
                aliasitems.append(item)
          if 'Origins' in distribution :
            if 'Items' in distribution['Origins'] :
              for item in distribution['Origins']['Items'] :
                customheaders = ''
                if 'Items' in item['CustomHeaders'] :
                  for headitem in item['CustomHeaders']['Items']:
                    customheaders = customheaders + headitem['HeaderName'] + ':' + headitem['HeaderValue'] + ','
                customoriginconfig = dict()
                if 'CustomOriginConfig' in item :
                  customoriginconfig = {'HTTPPort' : item['CustomOriginConfig']['HTTPPort'] if 'HTTPPort' in item['CustomOriginConfig'] else '',
                                        'HTTPSPort' : item['CustomOriginConfig']['HTTPSPort'] if 'HTTPSPort' in item['CustomOriginConfig'] else '',
                                        'OriginProtocolPolicy' : item['CustomOriginConfig']['OriginProtocolPolicy'] if 'OriginProtocolPolicy' in item['CustomOriginConfig'] else '',
                                        'OriginReadTimeout' : item['CustomOriginConfig']['OriginReadTimeout'] if 'OriginReadTimeout' in item['CustomOriginConfig'] else '',
                                        'OriginKeepaliveTimeout' : item['CustomOriginConfig']['OriginKeepaliveTimeout'] if 'OriginKeepaliveTimeout' in item['CustomOriginConfig'] else ''
                                       }
                originshield = dict()
                if 'OriginShield' in item :
                  originshield = {'Enabled' : 'True' if item['OriginShield']['Enabled'] else 'False',
                                  'OriginShieldRegion' : item['OriginShield']['OriginShieldRegion'] if 'OriginShieldRegion' in item['OriginShield'] else ''
                                 }
                originitems.append({'Id' : item['Id'],
                                    'DomainName' : item['DomainName'],
                                    'OriginPath' : item['OriginPath'] if 'OriginPath' in item else '',
                                    'CustomHeaders' : customheaders,
                                    'S3OriginConfig' : item['S3OriginConfig'] if 'S3OriginConfig' in item else '',
                                    'CustomOriginConfig' : customoriginconfig,
                                    'ConnectionAttempts' : item['ConnectionAttempts'] if 'ConnectionAttempts' in item else '',
                                    'ConnectionTimeout' : item['ConnectionTimeout'] if 'ConnectionTimeout' in item else '',
                                    'OriginShield' : originshield,
                                    'OriginAccessControlId' : item['OriginAccessControlId'] if 'OriginAccessControlId' in item else ''
                                   })
          if 'OriginGroups' in distribution :
            if 'Items' in distribution['OriginGroups'] :
              for item in distribution['OriginGroups']['Items'] :
                members = ''
                if 'Members' in item:
                  for originid in item['Members']['Items']:
                    members = members + originid + ','
                origingroupitems.append({
                  'Id' : item['Id'] if 'Id' in item else '',
                  'MembersOriginIds' : members
                })
          if 'DefaultCacheBehavior' in distribution :
            defaultcachebehavior.append({
              'TargetOriginId' : distribution['DefaultCacheBehavior']['TargetOriginId'],
              'ViewerProtocolPolicy' : distribution['DefaultCacheBehavior']['ViewerProtocolPolicy'],
              'MinTTL' : distribution['DefaultCacheBehavior']['MinTTL'] if 'MinTTL' in distribution['DefaultCacheBehavior'] else '',
              'DefaultTTL' : distribution['DefaultCacheBehavior']['DefaultTTL'] if 'DefaultTTL' in distribution['DefaultCacheBehavior'] else '',
              'MaxTTL' : distribution['DefaultCacheBehavior']['MaxTTL'] if 'MaxTTL' in distribution['DefaultCacheBehavior'] else ''
            })
          if 'CacheBehaviors' in distribution :
            if 'Items' in distribution['CacheBehaviors'] :
              for item in distribution['CacheBehaviors']['Items']:
                cachebehaviors.append({
                  'PathPattern' : item['PathPattern'] if 'PathPattern' in item else '',
                  'TargetOriginId' : item['TargetOriginId'] if 'TargetOriginId' in item else '',
                  'ViewerProtocolPolicy' : item['ViewerProtocolPolicy'] if 'ViewerProtocolPolicy' in item else '',
                  'RealtimeLogConfigArn' : item['RealtimeLogConfigArn'] if 'RealtimeLogConfigArn' in item else '',
                  'CachePolicyId' : item['CachePolicyId'] if 'CachePolicyId' in item else '',
                  'OriginRequestPolicyId' : item['OriginRequestPolicyId'] if 'OriginRequestPolicyId' in item else '',
                  'MinTTL' : item['MinTTL'] if 'MinTTL' in item else '',
                  'DefaultTTL' : item['DefaultTTL'] if 'DefaultTTL' in item else '',
                  'MaxTTL' : item['MaxTTL'] if 'MaxTTL' in item else ''
                })
          if 'CustomErrorResponses' in distribution :
            if 'Items' in distribution['CustomErrorResponses'] :
              for item in distribution['CustomErrorResponses']['Items']:
                customerrresponses.append({
                  'ErrorCode' : item['ErrorCode'] if 'ErrorCode' in item else '',
                  'ResponsePagePath' : item['ResponsePagePath'] if 'ResponsePagePath' in item else '',
                  'ResponseCode' : item['ResponseCode'] if 'ResponseCode' in item else '',
                  'ErrorCachingMinTTL' : item['ErrorCachingMinTTL'] if 'ErrorCachingMinTTL' in item else ''
                })
        # list count sync with space
        utils.ListSyncCountWithSpace(ids, arns, status, domainnames, webaclids, httpversions, priceclass,
                                     enableds, aliasitems, originitems, origingroupitems, defaultcachebehavior,
                                     cachebehaviors, customerrresponses, comments, viewercertificates)
                
        results.append( { "Id": ids,
                          "ARN" : arns,
                          "Status": status,
                          "DomainName": domainnames,
                          "WebACLId": webaclids,
                          "HttpVersion": httpversions,
                          "PriceClass": priceclass,
                          "Enabled": enableds,
                          "AliasItems": aliasitems,
                          "OriginItems": originitems,
                          "OriginGroupItems": origingroupitems,
                          "DefaultCacheBehavior": defaultcachebehavior,
                          "CacheBehaviors": cachebehaviors,
                          "CustomErrorResponses": customerrresponses,
                          "Comment": comments,
                          "ViewerCertificate": viewercertificates,
                        })
      else: # column list
        results.append( { "Id": ' ',
                          "ARN": ' ',
                          "Status": ' ',
                          "DomainName": ' ',
                          "WebACLId": ' ',
                          "HttpVersion": ' ',
                          "PriceClass": ' ',
                          "Enabled": ' ',
                          "AliasItems": ' ',
                          "OriginItems": ' ',
                          "OriginGroupItems": ' ',
                          "DefaultCacheBehavior": ' ',
                          "CacheBehaviors": ' ',
                          "CustomErrorResponses": ' ',
                          "Comment": ' ',
                          "ViewerCertificate": list(' '),
                        })
    else:
      klogger.error("call error : %d", distributions["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "Id": 'ERROR CHECK',
                        "ARN": 'ERROR CHECK',
                        "Status": 'ERROR CHECK',
                        "DomainName": 'ERROR CHECK',
                        "WebACLId": 'ERROR CHECK',
                        "HttpVersion": 'ERROR CHECK',
                        "PriceClass": 'ERROR CHECK',
                        "Enabled": 'ERROR CHECK',
                        "AliasItems": 'ERROR CHECK',
                        "OriginItems": 'ERROR CHECK',
                        "OriginGroupItems": 'ERROR CHECK',
                        "DefaultCacheBehavior": 'ERROR CHECK',
                        "CacheBehaviors": 'ERROR CHECK',
                        "CustomErrorResponses": 'ERROR CHECK',
                        "Comment": 'ERROR CHECK',
                        "ViewerCertificate": list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("cloudfront.list_distributions(),%s", othererr)
    results.append( { "Id": 'ERROR CHECK',
                      "ARN": 'ERROR CHECK',
                      "Status": 'ERROR CHECK',
                      "DomainName": 'ERROR CHECK',
                      "WebACLId": 'ERROR CHECK',
                      "HttpVersion": 'ERROR CHECK',
                      "PriceClass": 'ERROR CHECK',
                      "Enabled": 'ERROR CHECK',
                      "AliasItems": 'ERROR CHECK',
                      "OriginItems": 'ERROR CHECK',
                      "OriginGroupItems": 'ERROR CHECK',
                      "DefaultCacheBehavior": 'ERROR CHECK',
                      "CacheBehaviors": 'ERROR CHECK',
                      "CustomErrorResponses": 'ERROR CHECK',
                      "Comment": 'ERROR CHECK',
                      "ViewerCertificate": list('ERROR CHECK'),
                    })
  finally:
    return results

def main(argv):

  list_cloud_front_origin_access_identities() 
  list_distributions()
  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
