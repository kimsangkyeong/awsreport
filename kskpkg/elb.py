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
          # list count sync with space
          utils.ListSyncCountWithSpace(availzons, availsubnetids, availsubnetnames,
                eip_ipaddrs, eip_allocateids, privateaddrs, securitygroups, sgrpnames)
  
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
                            "LoadBalancerArn" : loadbalancer['LoadBalancerArn'],
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
                          "LoadBalancerArn" : ' ',
                          "CreatedTime" : list(' '),
                         })
        
    #   klogger.debug(results)
    else:
      klogger.error("call error : %d", loadbalancers["ResponseMetadata"]["HTTPStatusCode"])
  except Exception as othererr:
    klogger.error("elbv2.describe_load_balancers(),%s", othererr)
  return results

def describe_listeners(LoadBalancerArns):
  '''
    search load_balancers Listensers
  '''
  klogger_dat.debug('ELB-Listener')
#   klogger_dat.debug(LoadBalancerArns)
  try:
    results = [] 
    elb=boto3.client('elbv2')
    for LoadBalancerArn in LoadBalancerArns :
      listeners = elb.describe_listeners(LoadBalancerArn=LoadBalancerArn)
    #   klogger_dat.debug(listeners)
      if 200 == listeners["ResponseMetadata"]["HTTPStatusCode"]:
      #   klogger_dat.debug(listeners["Listeners"])
        if len(listeners["Listeners"]) > 0 :
          for listener in listeners["Listeners"]:
            # klogger_dat.debug(listener)
            certificates = []; alpnpolicys = []; orders = []; types = []; acttgrparn =[]; tgrparns = [];
            tgrpweights = []; tgrpsticki = []; tgrpstikidu = []; rprotocols = []; rports = [];
            rhosts = []; rpaths = []; rquerys = []; rstates = []; fmsgbodys = []; fstates = [];
            fcontenttypes = []; oidcissuers = []; oidcendpoints = []; oidcscopes = [];
            oidccookies = []; oidcextparams = []; oidcunauths = []; cognitodomains = [];
            cognitoarns = []; cognitocliids = []; cognitocookies = []; cognitoscopes = [];
            cognitoextparams = []; cognitounauths = [];
            if 'Certificates' in listener :
              for certificate in listener['Certificates']:
                certificates.append(certificate['CertificateArn'])
            if 'AlpnPolicy' in listener :
              for policy in listener['AlpnPolicy'] :
                alpnpolicys.append(policy)
            if 'DefaultActions' in listener :
              for action in listener['DefaultActions']:
                orders.append(action['Order'] if 'Order' in action else ' ')
                types.append(action['Type'] if 'Type' in action else ' ')
                acttgrparn.append(action['TargetGroupArn'] if 'TargetGroupArn' in action else ' ')
                if 'AuthenticateOidcConfig' in action :
                  oidcissuers.append(action['AuthenticateOidcConfig']['Issuer'] 
                                     if 'Issuer' in action['AuthenticateOidcConfig'] else ' ')
                  oidcendpoints.append(action['AuthenticateOidcConfig']['AuthorizationEndpoint'] 
                                     if 'AuthorizationEndpoint' in action['AuthenticateOidcConfig'] else ' ')
                  oidcscopes.append(action['AuthenticateOidcConfig']['Scope'] 
                                     if 'Scope' in action['AuthenticateOidcConfig'] else ' ')
                  oidccookies.append(action['AuthenticateOidcConfig']['SessionCookieName'] 
                                     if 'SessionCookieName' in action['AuthenticateOidcConfig'] else ' ')
                  oidcextparams.append(action['AuthenticateOidcConfig']['AuthenticationRequestExtraParams']['string'] 
                                     if 'AuthenticationRequestExtraParams' in action['AuthenticateOidcConfig'] else ' ')
                  oidcunauths.append(action['AuthenticateOidcConfig']['OnUnauthenticatedRequest'] 
                                     if 'OnUnauthenticatedRequest' in action['AuthenticateOidcConfig'] else ' ')
                if 'AuthenticateCognitoConfig' in action :
                  cognitodomains.append(action['AuthenticateCognitoConfig']['UserPoolDomain'] 
                                   if 'UserPoolDomain' in action['AuthenticateCognitoConfig'] else ' ')
                  cognitoarns.append(action['AuthenticateCognitoConfig']['UserPoolArn'] 
                                   if 'UserPoolArn' in action['AuthenticateCognitoConfig'] else ' ')
                  cognitocliids.append(action['AuthenticateCognitoConfig']['UserPoolClientId'] 
                                   if 'UserPoolClientId' in action['AuthenticateCognitoConfig'] else ' ')
                  cognitocookies.append(action['AuthenticateCognitoConfig']['SessionCookieName'] 
                                   if 'SessionCookieName' in action['AuthenticateCognitoConfig'] else ' ')
                  cognitoscopes.append(action['AuthenticateCognitoConfig']['Scope'] 
                                   if 'Scope' in action['AuthenticateCognitoConfig'] else ' ')
                  cognitoextparams.append(action['AuthenticateCognitoConfig']['AuthenticationRequestExtraParams']['string'] 
                                   if 'AuthenticationRequestExtraParams' in action['AuthenticateCognitoConfig'] else ' ')
                  cognitounauths.append(action['AuthenticateCognitoConfig']['OnUnauthenticatedRequest'] 
                                   if 'OnUnauthenticatedRequest' in action['AuthenticateCognitoConfig'] else ' ')
                if 'RedirectConfig' in action :
                  rprotocols.append(action['RedirectConfig']['Protocol'] 
                                   if 'Protocol' in action['RedirectConfig'] else ' ')
                  rports.append(action['RedirectConfig']['Port'] 
                                   if 'Port' in action['RedirectConfig'] else ' ')
                  rhosts.append(action['RedirectConfig']['Host'] 
                                   if 'Host' in action['RedirectConfig'] else ' ')
                  rpaths.append(action['RedirectConfig']['Path'] 
                                   if 'Path' in action['RedirectConfig'] else ' ')
                  rquerys.append(action['RedirectConfig']['Query'] 
                                   if 'Query' in action['RedirectConfig'] else ' ')
                  rstates.append(action['RedirectConfig']['StatusCode'] 
                                   if 'StatusCode' in action['RedirectConfig'] else ' ')
                if 'FixedResponseConfig' in action :
                  fmsgbodys.append(action['FixedResponseConfig']['MessageBody'] 
                                   if 'MessageBody' in action['FixedResponseConfig'] else ' ')
                  fstates.append(action['FixedResponseConfig']['StatusCode'] 
                                   if 'StatusCode' in action['FixedResponseConfig'] else ' ')
                  fcontenttypes.append(action['FixedResponseConfig']['ContentType'] 
                                   if 'ContentType' in action['FixedResponseConfig'] else ' ')
                if 'ForwardConfig' in action :
                  if 'TargetGroups' in action['ForwardConfig'] :
                    for tgroup in action['ForwardConfig']['TargetGroups'] :
                      tgrparns.append(tgroup['TargetGroupArn'] 
                                    if 'TargetGroupArn' in tgroup else ' ')
                      tgrpweights.append(tgroup['Weight'] 
                                    if 'Weight' in tgroup else ' ')
                  if 'TargetGroupStickinessConfig' in action['ForwardConfig'] :
                    tgrpsticki.append(action['ForwardConfig']['TargetGroupStickinessConfig']['Enabled'] 
                                    if 'Enabled' in action['ForwardConfig']['TargetGroupStickinessConfig'] else ' ')
                    tgrpstikidu.append(action['ForwardConfig']['TargetGroupStickinessConfig']['DurationSeconds'] 
                                    if 'DurationSeconds' in action['ForwardConfig']['TargetGroupStickinessConfig'] else ' ')  
            # list count sync with space
            utils.ListSyncCountWithSpace(certificates, alpnpolicys, orders, types, acttgrparn, 
                                 tgrparns, tgrpweights, tgrpsticki, tgrpstikidu, rprotocols, rports, 
                                 rhosts, rpaths, rquerys, rstates, fmsgbodys, fstates,
                                 fcontenttypes, oidcissuers, oidcendpoints, oidcscopes,
                                 oidccookies, oidcextparams, oidcunauths, cognitodomains,
                                 cognitoarns, cognitocliids, cognitocookies, cognitoscopes,
                                 cognitoextparams, cognitounauths)
    
            results.append( { "LoadBalancerName": '',
                              "LoadBalancerArn" : listener['LoadBalancerArn'],
                              "Protocol" : listener['Protocol'],
                              "Port" : listener['Port'],
                              "ListenerArn" : listener['ListenerArn'],
                              "SslPolicy" : listener['SslPolicy'] if 'SslPolicy' in listener else '',
                              "Certificates" : certificates,
                              "AlpnPolicy" : alpnpolicys,
                              "Act_Order" : orders,
                              "Act_Type" : types,
                              "Act_TargetGroupArn" : acttgrparn,
                              "Forward_TargetGroupArn" : tgrparns,
                              "Forward_TargetGroupWeight" : tgrpweights,
                              "Forward_TargetGroupStickiness" : tgrpsticki,
                              "Forward_TargetGroupStickinessDuration" : tgrpstikidu,
                              "Redir_Protocol" : rprotocols,
                              "Redir_Port" : rports,
                              "Redir_Host" : rhosts,
                              "Redir_Path" : rpaths,
                              "Redir_Query" : rquerys,
                              "Redir_StatusCode" : rstates,
                              "FixRep_MessageBody" : fmsgbodys,
                              "FixRep_StatusCode" : fstates,
                              "FixRep_ContentType" : fcontenttypes,
                              "Act_oidc_Issuer" : oidcissuers,
                              "Act_oidc_AuthorizationEndpoint" : oidcendpoints,
                              "Act_oidc_Scope" : oidcscopes,
                              "Act_oidc_SessionCookieName" : oidccookies,
                              "Act_oidc_AuthExtraParams" : oidcextparams,
                              "Act_oidc_OnUnauthRequest" : oidcunauths,
                              "Act_cognito_UserPoolDomain" : cognitodomains,
                              "Act_cognito_UserPoolArn" : cognitoarns,
                              "Act_cognito_UserPoolClientId" : cognitocliids,
                              "Act_cognito_SessionCookieName" : cognitocookies,
                              "Act_cognito_Scope" : cognitoscopes,
                              "Act_cognito_AuthExtraParams" : cognitoextparams,
                              "Act_cognito_OnUnauthRequest" : cognitounauths,
                             })
          
        else: # column list
          results.append( { "LoadBalancerName": ' ',
                            "LoadBalancerArn" : ' ',
                            "Protocol" : ' ',
                            "Port" : ' ',
                            "ListenerArn" : ' ',
                            "SslPolicy" : ' ',
                            "Certificates" : ' ',
                            "AlpnPolicy" : ' ',
                            "Order" : ' ',
                            "Act_Type" : ' ',
                            "Act_TargetGroupArn" : ' ',
                            "Forward_TargetGroupArn" : ' ',
                            "Forward_TargetGroupWeight" : ' ',
                            "Forward_TargetGroupStickiness" : ' ',
                            "Forward_TargetGroupStickinessDuration" : ' ',
                            "Redir_Protocol" : ' ',
                            "Redir_Port" : ' ',
                            "Redir_Host" : ' ',
                            "Redir_Path" : ' ',
                            "Redir_Query" : ' ',
                            "Redir_StatusCode" : ' ',
                            "FixRep_MessageBody" : ' ',
                            "FixRep_StatusCode" : ' ',
                            "FixRep_ContentType" : ' ',
                            "Act_oidc_Issuer" : ' ',
                            "Act_oidc_AuthorizationEndpoint" : ' ',
                            "Act_oidc_Scope" : ' ',
                            "Act_oidc_SessionCookieName" : ' ',
                            "Act_oidc_AuthExtraParams" : ' ',
                            "Act_oidc_OnUnauthRequest" : ' ',
                            "Act_cognito_UserPoolDomain" : ' ',
                            "Act_cognito_UserPoolArn" : ' ',
                            "Act_cognito_UserPoolClientId" : ' ',
                            "Act_cognito_SessionCookieName" : ' ',
                            "Act_cognito_Scope" : ' ',
                            "Act_cognito_AuthExtraParams" : ' ',
                            "Act_cognito_OnUnauthRequest" : list(' '),
                           })
          
        # klogger.debug(results)
      else:
        klogger.error("call error : %d", listeners["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("elbv2.describe_listeners(),%s", othererr)
  return results

def main(argv):

  describe_load_balancers() 
  describe_listeners()

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
