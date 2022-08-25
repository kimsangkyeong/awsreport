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

def describe_load_balancers():
  '''
    search load_balancers
  '''
  klogger_dat.debug('elb')
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
    else:
      klogger.error("call error : %d", loadbalancers["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "LoadBalancerName": 'ERROR CHECK',
                        "Scheme" : 'ERROR CHECK',
                        "Type" : 'ERROR CHECK',
                        "Scheme" : 'ERROR CHECK',
                        "IpAddressType" : 'ERROR CHECK',
                        "State" : 'ERROR CHECK',
                        "AvailableZoneName" : 'ERROR CHECK',
                        "SubnetId" : 'ERROR CHECK',
                        "SubnetTName" : 'ERROR CHECK',
                        "ELB_IpAddress" : 'ERROR CHECK',
                        "ELB_AllocationId" : 'ERROR CHECK',
                        "PrivateIPv4Address" : 'ERROR CHECK',
                        "SecurityGroupId" : 'ERROR CHECK',
                        "SecurityGroupName" : 'ERROR CHECK',
                        "VpcId" : 'ERROR CHECK',
                        "VpcTName" : 'ERROR CHECK',
                        "DNSName" : 'ERROR CHECK',
                        "LoadBalancerArn" : 'ERROR CHECK',
                        "CreatedTime" : list('ERROR CHECK'),
                       })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("elbv2.describe_load_balancers(),%s", othererr)
    results.append( { "LoadBalancerName": 'ERROR CHECK',
                      "Scheme" : 'ERROR CHECK',
                      "Type" : 'ERROR CHECK',
                      "Scheme" : 'ERROR CHECK',
                      "IpAddressType" : 'ERROR CHECK',
                      "State" : 'ERROR CHECK',
                      "AvailableZoneName" : 'ERROR CHECK',
                      "SubnetId" : 'ERROR CHECK',
                      "SubnetTName" : 'ERROR CHECK',
                      "ELB_IpAddress" : 'ERROR CHECK',
                      "ELB_AllocationId" : 'ERROR CHECK',
                      "PrivateIPv4Address" : 'ERROR CHECK',
                      "SecurityGroupId" : 'ERROR CHECK',
                      "SecurityGroupName" : 'ERROR CHECK',
                      "VpcId" : 'ERROR CHECK',
                      "VpcTName" : 'ERROR CHECK',
                      "DNSName" : 'ERROR CHECK',
                      "LoadBalancerArn" : 'ERROR CHECK',
                      "CreatedTime" : list('ERROR CHECK'),
                     })
  finally:
    return results

def describe_listeners(LoadBalancerArns):
  '''
    search load_balancers Listensers
  '''
  klogger_dat.debug('elb-listener')
#   klogger_dat.debug(LoadBalancerArns)
  try:
    results = [] 
    elb=boto3.client('elbv2')
    for LoadBalancerArn in LoadBalancerArns :
      if (LoadBalancerArn == ' ') : # Not Exist LoadBalancer
        continue
      listeners = elb.describe_listeners(LoadBalancerArn=LoadBalancerArn)
      # klogger_dat.debug(listeners)
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
      else:
        klogger.error("call error : %d", listeners["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "LoadBalancerName": 'ERROR CHECK',
                          "LoadBalancerArn" : 'ERROR CHECK',
                          "Protocol" : 'ERROR CHECK',
                          "Port" : 'ERROR CHECK',
                          "ListenerArn" : 'ERROR CHECK',
                          "SslPolicy" : 'ERROR CHECK',
                          "Certificates" : 'ERROR CHECK',
                          "AlpnPolicy" : 'ERROR CHECK',
                          "Order" : 'ERROR CHECK',
                          "Act_Type" : 'ERROR CHECK',
                          "Act_TargetGroupArn" : 'ERROR CHECK',
                          "Forward_TargetGroupArn" : 'ERROR CHECK',
                          "Forward_TargetGroupWeight" : 'ERROR CHECK',
                          "Forward_TargetGroupStickiness" : 'ERROR CHECK',
                          "Forward_TargetGroupStickinessDuration" : 'ERROR CHECK',
                          "Redir_Protocol" : 'ERROR CHECK',
                          "Redir_Port" : 'ERROR CHECK',
                          "Redir_Host" : 'ERROR CHECK',
                          "Redir_Path" : 'ERROR CHECK',
                          "Redir_Query" : 'ERROR CHECK',
                          "Redir_StatusCode" : 'ERROR CHECK',
                          "FixRep_MessageBody" : 'ERROR CHECK',
                          "FixRep_StatusCode" : 'ERROR CHECK',
                          "FixRep_ContentType" : 'ERROR CHECK',
                          "Act_oidc_Issuer" : 'ERROR CHECK',
                          "Act_oidc_AuthorizationEndpoint" : 'ERROR CHECK',
                          "Act_oidc_Scope" : 'ERROR CHECK',
                          "Act_oidc_SessionCookieName" : 'ERROR CHECK',
                          "Act_oidc_AuthExtraParams" : 'ERROR CHECK',
                          "Act_oidc_OnUnauthRequest" : 'ERROR CHECK',
                          "Act_cognito_UserPoolDomain" : 'ERROR CHECK',
                          "Act_cognito_UserPoolArn" : 'ERROR CHECK',
                          "Act_cognito_UserPoolClientId" : 'ERROR CHECK',
                          "Act_cognito_SessionCookieName" : 'ERROR CHECK',
                          "Act_cognito_Scope" : 'ERROR CHECK',
                          "Act_cognito_AuthExtraParams" : 'ERROR CHECK',
                          "Act_cognito_OnUnauthRequest" : list('ERROR CHECK'),
                         })
    if results == [] :
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
  except Exception as othererr:
    klogger.error("elbv2.describe_listeners(),%s", othererr)
    results.append( { "LoadBalancerName": 'ERROR CHECK',
                      "LoadBalancerArn" : 'ERROR CHECK',
                      "Protocol" : 'ERROR CHECK',
                      "Port" : 'ERROR CHECK',
                      "ListenerArn" : 'ERROR CHECK',
                      "SslPolicy" : 'ERROR CHECK',
                      "Certificates" : 'ERROR CHECK',
                      "AlpnPolicy" : 'ERROR CHECK',
                      "Order" : 'ERROR CHECK',
                      "Act_Type" : 'ERROR CHECK',
                      "Act_TargetGroupArn" : 'ERROR CHECK',
                      "Forward_TargetGroupArn" : 'ERROR CHECK',
                      "Forward_TargetGroupWeight" : 'ERROR CHECK',
                      "Forward_TargetGroupStickiness" : 'ERROR CHECK',
                      "Forward_TargetGroupStickinessDuration" : 'ERROR CHECK',
                      "Redir_Protocol" : 'ERROR CHECK',
                      "Redir_Port" : 'ERROR CHECK',
                      "Redir_Host" : 'ERROR CHECK',
                      "Redir_Path" : 'ERROR CHECK',
                      "Redir_Query" : 'ERROR CHECK',
                      "Redir_StatusCode" : 'ERROR CHECK',
                      "FixRep_MessageBody" : 'ERROR CHECK',
                      "FixRep_StatusCode" : 'ERROR CHECK',
                      "FixRep_ContentType" : 'ERROR CHECK',
                      "Act_oidc_Issuer" : 'ERROR CHECK',
                      "Act_oidc_AuthorizationEndpoint" : 'ERROR CHECK',
                      "Act_oidc_Scope" : 'ERROR CHECK',
                      "Act_oidc_SessionCookieName" : 'ERROR CHECK',
                      "Act_oidc_AuthExtraParams" : 'ERROR CHECK',
                      "Act_oidc_OnUnauthRequest" : 'ERROR CHECK',
                      "Act_cognito_UserPoolDomain" : 'ERROR CHECK',
                      "Act_cognito_UserPoolArn" : 'ERROR CHECK',
                      "Act_cognito_UserPoolClientId" : 'ERROR CHECK',
                      "Act_cognito_SessionCookieName" : 'ERROR CHECK',
                      "Act_cognito_Scope" : 'ERROR CHECK',
                      "Act_cognito_AuthExtraParams" : 'ERROR CHECK',
                      "Act_cognito_OnUnauthRequest" : list('ERROR CHECK'),
                     })
  finally:
    return results

def describe_rules(ListenerArns):
  '''
    search load_balancers Listenser Rules
  '''
  klogger_dat.debug('elb-listener-rule')
#   klogger_dat.debug(ListenerArns)
  try:
    results = [] 
    elb=boto3.client('elbv2')
    for LisenerArn in ListenerArns :
      if LisenerArn == ' ' : # Not Exist Listener
        continue
      rules = elb.describe_rules(ListenerArn=LisenerArn)
    #   klogger_dat.debug(rules)
      if 200 == rules["ResponseMetadata"]["HTTPStatusCode"]:
      #   klogger_dat.debug(rules["Rules"])
        if len(rules["Rules"]) > 0 :
          for rule in rules["Rules"]:
            # klogger_dat.debug(rule)
            actorders = []; acttypes = []; acttgrparn =[]; tgrparns = [];
            tgrpweights = []; tgrpsticki = []; tgrpstikidu = []; rprotocols = []; rports = [];
            rhosts = []; rpaths = []; rquerys = []; rstates = []; fmsgbodys = []; fstates = [];
            fcontenttypes = []; oidcissuers = []; oidcendpoints = []; oidcscopes = []; oidctoken = [];
            oidccookies = []; oidcextparams = []; oidcunauths = []; cognitodomains = [];
            cognitoarns = []; cognitocliids = []; cognitocookies = []; cognitoscopes = [];
            cognitoextparams = []; cognitounauths = []; cfields = []; cvalues = [];
            chostconfs = []; cpathconfs = []; chttpheaders = []; chttpvalues= []; cquerykeys = [];
            cqueryvalues = []; cmethodconfs = []; cipconfs = [];

            if 'Conditions' in rule :
              for condition in rule['Conditions']:
                cfields.append(condition['Field'] if 'Field' in condition else ' ')
                if 'Values' in condition :
                  for value in condition['Values'] :
                    cvalues.append(value)
                if 'HostHeaderConfig' in condition :
                  for value in condition['HostHeaderConfig']['Values'] :
                    chostconfs.append(value)
                if 'PathPatternConfig' in condition :
                  for value in condition['PathPatternConfig']['Values'] :
                    cpathconfs.append(value)
                if 'HttpHeaderConfig' in condition :
                  chttpheaders.append(condition['HttpHeaderConfig']['HttpHeaderName']
                                      if 'HttpHeaderName' in condition['HttpHeaderConfig'] else ' ')
                  if 'Values' in condition['HttpHeaderConfig']:
                    for value in condition['HttpHeaderConfig']['Values'] :
                      chttpvalues.append(value)
                if 'QueryStringConfig' in condition :
                  for value in condition['QueryStringConfig']['Values']:
                    cquerykeys.append(value['Key'] if 'Key' in value else ' ')
                    cqueryvalues.append(value['Value'] if 'Value' in value else ' ')
                if 'HttpRequestMethodConfig' in condition :
                  for value in condition['HttpRequestMethodConfig']['Values'] :
                    cmethodconfs.append(value)
                if 'SourceIpConfig' in condition :
                  for value in condition['SourceIpConfig']['Values'] :
                    cipconfs.append(value)
            if 'Actions' in rule :
              for action in rule['Actions']:
                actorders.append(action['Order'] if 'Order' in action else ' ')
                acttypes.append(action['Type'] if 'Type' in action else ' ')
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
                  oidctoken.append(action['AuthenticateOidcConfig']['TokenEndpoint'] 
                                     if 'TokenEndpoint' in action['AuthenticateOidcConfig'] else ' ')
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
            utils.ListSyncCountWithSpace(actorders, acttypes, acttgrparn, 
                                 tgrparns, tgrpweights, tgrpsticki, tgrpstikidu, 
                                 rprotocols, rports, rhosts, rpaths, rquerys, rstates, 
                                 fmsgbodys, fstates, fcontenttypes, 
                                 oidcissuers, oidcendpoints, oidcscopes, oidctoken,
                                 oidccookies, oidcextparams, oidcunauths, 
                                 cognitodomains, cognitoarns, cognitocliids, cognitocookies, 
                                 cognitoscopes, cognitoextparams, cognitounauths, cfields,
                                 cvalues, chostconfs, cpathconfs, chttpheaders, chttpvalues,
                                 cquerykeys, cqueryvalues, cmethodconfs, cipconfs)

            results.append( { "LoadBalancerInfo": ' ',
                              "ListenerArn" : LisenerArn,
                              "RuleArn" : rule['RuleArn'],
                              "Priority" : rule['Priority'],
                              "Cond_Field" : cfields,
                              "Cond_Values" : cvalues,
                              "Cond_HostHeaderConfig" : chostconfs,
                              "Cond_PathPatternConfig" : cpathconfs,
                              "Cond_HttpHeaderName" : chttpheaders,
                              "Cond_HttpHeaderValue" : chttpvalues,
                              "Cond_QueryStringKey" : cquerykeys,
                              "Cond_QueryStringValue" : cqueryvalues,
                              "Cond_HttpRequestMethodConfig" : cmethodconfs,
                              "Cond_SourceIpConfig" : cipconfs,
                              "Act_Type" : acttypes,
                              "Act_TargetGroupArn" : acttgrparn,
                              "Act_Order" : actorders,
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
                              "Act_oidc_TokenEndpoint" : oidctoken,
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
          results.append( { "LoadBalancerInfo": ' ',
                            "ListenerArn" : ' ',
                            "RuleArn" : ' ',
                            "Priority" : ' ',
                            "Cond_Field" : ' ',
                            "Cond_Values" : ' ',
                            "Cond_HostHeaderConfig" : ' ',
                            "Cond_PathPatternConfig" : ' ',
                            "Cond_HttpHeaderName" : ' ',
                            "Cond_HttpHeaderValue" : ' ',
                            "Cond_QueryStringKey" : ' ',
                            "Cond_QueryStringValue" : ' ',
                            "Cond_HttpRequestMethodConfig" : ' ',
                            "Cond_SourceIpConfig" : ' ',
                            "Act_Type" : ' ',
                            "Act_TargetGroupArn" : ' ',
                            "Act_Order" : ' ',
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
                            "Act_oidc_TokenEndpoint" : ' ',
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
      else:
        klogger.error("call error : %d", rules["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "LoadBalancerInfo": 'ERROR CHECK',
                          "ListenerArn" : 'ERROR CHECK',
                          "RuleArn" : 'ERROR CHECK',
                          "Priority" : 'ERROR CHECK',
                          "Cond_Field" : 'ERROR CHECK',
                          "Cond_Values" : 'ERROR CHECK',
                          "Cond_HostHeaderConfig" : 'ERROR CHECK',
                          "Cond_PathPatternConfig" : 'ERROR CHECK',
                          "Cond_HttpHeaderName" : 'ERROR CHECK',
                          "Cond_HttpHeaderValue" : 'ERROR CHECK',
                          "Cond_QueryStringKey" : 'ERROR CHECK',
                          "Cond_QueryStringValue" : 'ERROR CHECK',
                          "Cond_HttpRequestMethodConfig" : 'ERROR CHECK',
                          "Cond_SourceIpConfig" : 'ERROR CHECK',
                          "Act_Type" : 'ERROR CHECK',
                          "Act_TargetGroupArn" : 'ERROR CHECK',
                          "Act_Order" : 'ERROR CHECK',
                          "Forward_TargetGroupArn" : 'ERROR CHECK',
                          "Forward_TargetGroupWeight" : 'ERROR CHECK',
                          "Forward_TargetGroupStickiness" : 'ERROR CHECK',
                          "Forward_TargetGroupStickinessDuration" : 'ERROR CHECK',
                          "Redir_Protocol" : 'ERROR CHECK',
                          "Redir_Port" : 'ERROR CHECK',
                          "Redir_Host" : 'ERROR CHECK',
                          "Redir_Path" : 'ERROR CHECK',
                          "Redir_Query" : 'ERROR CHECK',
                          "Redir_StatusCode" : 'ERROR CHECK',
                          "FixRep_MessageBody" : 'ERROR CHECK',
                          "FixRep_StatusCode" : 'ERROR CHECK',
                          "FixRep_ContentType" : 'ERROR CHECK',
                          "Act_oidc_Issuer" : 'ERROR CHECK',
                          "Act_oidc_AuthorizationEndpoint" : 'ERROR CHECK',
                          "Act_oidc_Scope" : 'ERROR CHECK',
                          "Act_oidc_TokenEndpoint" : 'ERROR CHECK',
                          "Act_oidc_SessionCookieName" : 'ERROR CHECK',
                          "Act_oidc_AuthExtraParams" : 'ERROR CHECK',
                          "Act_oidc_OnUnauthRequest" : 'ERROR CHECK',
                          "Act_cognito_UserPoolDomain" : 'ERROR CHECK',
                          "Act_cognito_UserPoolArn" : 'ERROR CHECK',
                          "Act_cognito_UserPoolClientId" : 'ERROR CHECK',
                          "Act_cognito_SessionCookieName" : 'ERROR CHECK',
                          "Act_cognito_Scope" : 'ERROR CHECK',
                          "Act_cognito_AuthExtraParams" : 'ERROR CHECK',
                          "Act_cognito_OnUnauthRequest" : list('ERROR CHECK'),
                         })
    if results == []:
      results.append( { "LoadBalancerInfo": ' ',
                        "ListenerArn" : ' ',
                        "RuleArn" : ' ',
                        "Priority" : ' ',
                        "Cond_Field" : ' ',
                        "Cond_Values" : ' ',
                        "Cond_HostHeaderConfig" : ' ',
                        "Cond_PathPatternConfig" : ' ',
                        "Cond_HttpHeaderName" : ' ',
                        "Cond_HttpHeaderValue" : ' ',
                        "Cond_QueryStringKey" : ' ',
                        "Cond_QueryStringValue" : ' ',
                        "Cond_HttpRequestMethodConfig" : ' ',
                        "Cond_SourceIpConfig" : ' ',
                        "Act_Type" : ' ',
                        "Act_TargetGroupArn" : ' ',
                        "Act_Order" : ' ',
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
                        "Act_oidc_TokenEndpoint" : ' ',
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
  except Exception as othererr:
    klogger.error("elbv2.describe_rules(),%s", othererr)
    results.append( { "LoadBalancerInfo": 'ERROR CHECK',
                      "ListenerArn" : 'ERROR CHECK',
                      "RuleArn" : 'ERROR CHECK',
                      "Priority" : 'ERROR CHECK',
                      "Cond_Field" : 'ERROR CHECK',
                      "Cond_Values" : 'ERROR CHECK',
                      "Cond_HostHeaderConfig" : 'ERROR CHECK',
                      "Cond_PathPatternConfig" : 'ERROR CHECK',
                      "Cond_HttpHeaderName" : 'ERROR CHECK',
                      "Cond_HttpHeaderValue" : 'ERROR CHECK',
                      "Cond_QueryStringKey" : 'ERROR CHECK',
                      "Cond_QueryStringValue" : 'ERROR CHECK',
                      "Cond_HttpRequestMethodConfig" : 'ERROR CHECK',
                      "Cond_SourceIpConfig" : 'ERROR CHECK',
                      "Act_Type" : 'ERROR CHECK',
                      "Act_TargetGroupArn" : 'ERROR CHECK',
                      "Act_Order" : 'ERROR CHECK',
                      "Forward_TargetGroupArn" : 'ERROR CHECK',
                      "Forward_TargetGroupWeight" : 'ERROR CHECK',
                      "Forward_TargetGroupStickiness" : 'ERROR CHECK',
                      "Forward_TargetGroupStickinessDuration" : 'ERROR CHECK',
                      "Redir_Protocol" : 'ERROR CHECK',
                      "Redir_Port" : 'ERROR CHECK',
                      "Redir_Host" : 'ERROR CHECK',
                      "Redir_Path" : 'ERROR CHECK',
                      "Redir_Query" : 'ERROR CHECK',
                      "Redir_StatusCode" : 'ERROR CHECK',
                      "FixRep_MessageBody" : 'ERROR CHECK',
                      "FixRep_StatusCode" : 'ERROR CHECK',
                      "FixRep_ContentType" : 'ERROR CHECK',
                      "Act_oidc_Issuer" : 'ERROR CHECK',
                      "Act_oidc_AuthorizationEndpoint" : 'ERROR CHECK',
                      "Act_oidc_Scope" : 'ERROR CHECK',
                      "Act_oidc_TokenEndpoint" : 'ERROR CHECK',
                      "Act_oidc_SessionCookieName" : 'ERROR CHECK',
                      "Act_oidc_AuthExtraParams" : 'ERROR CHECK',
                      "Act_oidc_OnUnauthRequest" : 'ERROR CHECK',
                      "Act_cognito_UserPoolDomain" : 'ERROR CHECK',
                      "Act_cognito_UserPoolArn" : 'ERROR CHECK',
                      "Act_cognito_UserPoolClientId" : 'ERROR CHECK',
                      "Act_cognito_SessionCookieName" : 'ERROR CHECK',
                      "Act_cognito_Scope" : 'ERROR CHECK',
                      "Act_cognito_AuthExtraParams" : 'ERROR CHECK',
                      "Act_cognito_OnUnauthRequest" : list('ERROR CHECK'),
                     })
  finally:
    return results

def describe_target_groups(LoadBalancerArns):
  '''
    search load_balancers target groups
  '''
  klogger_dat.debug('elb-targetgroup')
#   klogger_dat.debug(LoadBalancerArns)
  try:
    results = [] 
    elb=boto3.client('elbv2')
    for LoadBalancerArn in LoadBalancerArns :
      if LoadBalancerArn == ' ': # Not Exist LoadBalancer
        continue
      targetgrps = elb.describe_target_groups(LoadBalancerArn=LoadBalancerArn)
    #   klogger_dat.debug(targetgrps)
      if 200 == targetgrps["ResponseMetadata"]["HTTPStatusCode"]:
      #   klogger_dat.debug(targetgrps["TargetGroups"])
        if len(targetgrps["TargetGroups"]) > 0 :
          for targetgrp in targetgrps["TargetGroups"]:
            # klogger_dat.debug(targetgrp)
            protocols = []; ports = []; tgrpnames = []; tgrparns = [];
            targettypes = []; henableds = []; hprotocols = []; hports = []; hintsecs = [];
            htimeouts = []; hcounts = []; uhcounts = []; hpaths = []; mhttpcodes = [];
            mgrpccodes = []; versions = []; vpcids = [];
            
            tgrparns.append(targetgrp['TargetGroupArn'] if 'TargetGroupArn' in targetgrp else ' ')
            tgrpnames.append(targetgrp['TargetGroupName'] if 'TargetGroupName' in targetgrp else ' ')
            protocols.append(targetgrp['Protocol'] if 'Protocol' in targetgrp else ' ')
            ports.append(targetgrp['Port'] if 'Port' in targetgrp else ' ')
            vpcids.append(targetgrp['VpcId'] if 'VpcId' in targetgrp else ' ')
            targettypes.append(targetgrp['TargetType'] if 'TargetType' in targetgrp else ' ')
            henableds.append(targetgrp['HealthCheckEnabled'] if 'HealthCheckEnabled' in targetgrp else ' ')
            hprotocols.append(targetgrp['HealthCheckProtocol'] if 'HealthCheckProtocol' in targetgrp else ' ')
            hports.append(targetgrp['HealthCheckPort'] if 'HealthCheckPort' in targetgrp else ' ')
            hintsecs.append(targetgrp['HealthCheckIntervalSeconds'] if 'HealthCheckIntervalSeconds' in targetgrp else ' ')
            htimeouts.append(targetgrp['HealthCheckTimeoutSeconds'] if 'HealthCheckTimeoutSeconds' in targetgrp else ' ')
            hcounts.append(targetgrp['HealthyThresholdCount'] if 'HealthyThresholdCount' in targetgrp else ' ')
            uhcounts.append(targetgrp['UnhealthyThresholdCount'] if 'UnhealthyThresholdCount' in targetgrp else ' ')
            hpaths.append(targetgrp['HealthCheckPath'] if 'HealthCheckPath' in targetgrp else ' ')
            if 'Matcher' in targetgrp :
              mhttpcodes.append(targetgrp['Matcher']['HttpCode'] if 'HttpCode' in targetgrp['Matcher'] else ' ')
              mgrpccodes.append(targetgrp['Matcher']['GrpcCode'] if 'GrpcCode' in targetgrp['Matcher'] else ' ')
            else:
              mhttpcodes.append(' ')
              mgrpccodes.append(' ')
            versions.append(targetgrp['ProtocolVersion'] if 'ProtocolVersion' in targetgrp else ' ')

            results.append( { "LoadBalancerName": '',
                              "LoadBalancerArn" : LoadBalancerArn,
                              "Protocol" : protocols,
                              "Port" : ports,
                              "TargetGroupName" : tgrpnames,
                              "TargetGroupArn" : tgrparns,
                              "TargetType" : targettypes,
                              "HealthCheckEnabled" : henableds,
                              "HealthCheckProtocol" : hprotocols,
                              "HealthCheckPort" : hports,
                              "HealthCheckIntervalSeconds" : hintsecs,
                              "HealthCheckTimeoutSeconds" : htimeouts,
                              "HealthyThresholdCount" : hcounts,
                              "UnhealthyThresholdCount" : uhcounts,
                              "HealthCheckPath" : hpaths,
                              "Matcher_HttpCode" : mhttpcodes,
                              "Matcher_GrpcCode" : mgrpccodes,
                              "ProtocolVersion" : versions,
                              "VpcId" : vpcids,
                              "VpcTName" : '',
                             })
          
        else: # column list
          results.append( { "LoadBalancerName": ' ',
                            "LoadBalancerArn" : ' ',
                            "Protocol" : ' ',
                            "Port" : ' ',
                            "TargetGroupName" : ' ',
                            "TargetType" : ' ',
                            "HealthCheckEnabled" : ' ',
                            "HealthCheckProtocol" : ' ',
                            "HealthCheckPort" : ' ',
                            "HealthCheckIntervalSeconds" : ' ',
                            "HealthCheckTimeoutSeconds" : ' ',
                            "HealthyThresholdCount" : ' ',
                            "UnhealthyThresholdCount" : ' ',
                            "HealthCheckPath" : ' ',
                            "Matcher_HttpCode" : ' ',
                            "Matcher_GrpcCode" : ' ',
                            "ProtocolVersion" : ' ',
                            "VpcId" : ' ',
                            "VpcTName" : list(' '),
                           })
      else:
        klogger.error("call error : %d", targetgrps["ResponseMetadata"]["HTTPStatusCode"])
        results.append( { "LoadBalancerName": 'ERROR CHECK',
                          "LoadBalancerArn" : 'ERROR CHECK',
                          "Protocol" : 'ERROR CHECK',
                          "Port" : 'ERROR CHECK',
                          "TargetGroupName" : 'ERROR CHECK',
                          "TargetType" : 'ERROR CHECK',
                          "HealthCheckEnabled" : 'ERROR CHECK',
                          "HealthCheckProtocol" : 'ERROR CHECK',
                          "HealthCheckPort" : 'ERROR CHECK',
                          "HealthCheckIntervalSeconds" : 'ERROR CHECK',
                          "HealthCheckTimeoutSeconds" : 'ERROR CHECK',
                          "HealthyThresholdCount" : 'ERROR CHECK',
                          "UnhealthyThresholdCount" : 'ERROR CHECK',
                          "HealthCheckPath" : 'ERROR CHECK',
                          "Matcher_HttpCode" : 'ERROR CHECK',
                          "Matcher_GrpcCode" : 'ERROR CHECK',
                          "ProtocolVersion" : 'ERROR CHECK',
                          "VpcId" : 'ERROR CHECK',
                          "VpcTName" : list('ERROR CHECK'),
                         })
    if results == [] :
      results.append( { "LoadBalancerName": ' ',
                        "LoadBalancerArn" : ' ',
                        "Protocol" : ' ',
                        "Port" : ' ',
                        "TargetGroupName" : ' ',
                        "TargetType" : ' ',
                        "HealthCheckEnabled" : ' ',
                        "HealthCheckProtocol" : ' ',
                        "HealthCheckPort" : ' ',
                        "HealthCheckIntervalSeconds" : ' ',
                        "HealthCheckTimeoutSeconds" : ' ',
                        "HealthyThresholdCount" : ' ',
                        "UnhealthyThresholdCount" : ' ',
                        "HealthCheckPath" : ' ',
                        "Matcher_HttpCode" : ' ',
                        "Matcher_GrpcCode" : ' ',
                        "ProtocolVersion" : ' ',
                        "VpcId" : ' ',
                        "VpcTName" : list(' '),
                       })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("elbv2.describe_target_groups(),%s", othererr)
    results.append( { "LoadBalancerName": 'ERROR CHECK',
                      "LoadBalancerArn" : 'ERROR CHECK',
                      "Protocol" : 'ERROR CHECK',
                      "Port" : 'ERROR CHECK',
                      "TargetGroupName" : 'ERROR CHECK',
                      "TargetType" : 'ERROR CHECK',
                      "HealthCheckEnabled" : 'ERROR CHECK',
                      "HealthCheckProtocol" : 'ERROR CHECK',
                      "HealthCheckPort" : 'ERROR CHECK',
                      "HealthCheckIntervalSeconds" : 'ERROR CHECK',
                      "HealthCheckTimeoutSeconds" : 'ERROR CHECK',
                      "HealthyThresholdCount" : 'ERROR CHECK',
                      "UnhealthyThresholdCount" : 'ERROR CHECK',
                      "HealthCheckPath" : 'ERROR CHECK',
                      "Matcher_HttpCode" : 'ERROR CHECK',
                      "Matcher_GrpcCode" : 'ERROR CHECK',
                      "ProtocolVersion" : 'ERROR CHECK',
                      "VpcId" : 'ERROR CHECK',
                      "VpcTName" : list('ERROR CHECK'),
                     })
  finally:
    return results

def main(argv):

  describe_load_balancers() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
