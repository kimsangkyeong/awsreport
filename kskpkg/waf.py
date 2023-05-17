####################################################################################################
# 
# Purpose   : get list waf
# Source    : waf.py
# Usage     : python waf.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.12     first create
#  1.1      2023.05.17     add session handling logic
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/waf.html
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

def list_web_acls(Scope):
  '''
    search waf web acls
  '''
  klogger_dat.debug('waf web acls')

  try:
    results = [] 
    wafv2 = WAFV2_session
    webacls = wafv2.list_web_acls(Scope=Scope)
    # klogger_dat.debug("%s", webacls)
    if 200 == webacls["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(webacls["WebACLs"])
      if 'WebACLs' in webacls and len(webacls["WebACLs"]) > 0 :
        for webacl in webacls["WebACLs"]:
        #   klogger_dat.debug(webacl)
          id = webacl['Id'] if 'Id' in webacl else ' '
          name = webacl['Name'] if 'Name' in webacl else ' '
          description = webacl['Description'] if 'Description' in webacl else ' '
          locktoken = webacl['LockToken'] if 'LockToken' in webacl else ' '
          arns = webacl['ARN'] if 'ARN' in webacl else ' '
          webaclinfo = get_web_acl(name, 'REGIONAL', id)
        #   klogger.debug(webaclinfo)
          defaultaction = ' '; rules = []; visiblecfg = ' '; capacity = ' '; prerulegrps = []; postrulegrps = [];
          managedby = 'False'; lblnamespace = ' '; custresponse = ' '; captchacfg = ' '; appinturl = ' ';
          if webaclinfo != None :
            if 'WebACL' in webaclinfo :
              defaultaction = str(webaclinfo['WebACL']['DefaultAction']) if 'DefaultAction' in webaclinfo['WebACL'] else ' '
              if 'Rules' in webaclinfo['WebACL'] :
                for rule in webaclinfo['WebACL']['Rules'] :
                  rules.append(str(rule))
              visiblecfg = str(webaclinfo['WebACL']['VisibilityConfig']) if 'VisibilityConfig' in webaclinfo['WebACL'] else ' '
              capacity = webaclinfo['WebACL']['Capacity'] if 'Capacity' in webaclinfo['WebACL'] else ' '
              if 'PreProcessFirewallManagerRuleGroups' in webaclinfo['WebACL'] :
                for prerulegrp in webaclinfo['WebACL']['PreProcessFirewallManagerRuleGroups'] : 
                  prerulegrps.append(str(prerulegrp))
              if 'PostProcessFirewallManagerRuleGroups' in webaclinfo['WebACL'] :
                for postrulegrp in webaclinfo['WebACL']['PostProcessFirewallManagerRuleGroups'] :
                  postrulegrps.append(str(postrulegrp))
              if 'ManagedByFirewallManager' in webaclinfo['WebACL'] :
                if webaclinfo['WebACL']['ManagedByFirewallManager'] :
                  managedby = 'True'
              lblnamespace = webaclinfo['WebACL']['LabelNamespace'] if 'LabelNamespace' in webaclinfo['WebACL'] else ' '
              custresponse = str(webaclinfo['WebACL']['CustomResponseBodies']) if 'CustomResponseBodies' in webaclinfo['WebACL'] else ' '
              captchacfg = str(webaclinfo['WebACL']['CaptchaConfig']) if 'CaptchaConfig' in webaclinfo['WebACL'] else ' '
            appinturl = webaclinfo['ApplicationIntegrationURL'] if 'ApplicationIntegrationURL' in webaclinfo else ' '
          # list count sync with space
          utils.ListSyncCountWithSpace(rules, prerulegrps, postrulegrps)
  
          results.append( { "WebACLId": id,
                            "WebACLName" : name,
                            "Description" : description,
                            "LockToken" : locktoken,
                            "ARN" : arns,
                            "DefaultAction" : defaultaction,
                            "Rules" : rules,
                            "VisibilityConfig" : visiblecfg,
                            "Capacity" : capacity,
                            "PreProcessFirewallManagerRuleGroups" : prerulegrps,
                            "PostProcessFirewallManagerRuleGroups" : postrulegrps,
                            "ManagedByFirewallManager" : managedby,
                            "LabelNamespace" : lblnamespace,
                            "CustomResponseBodies" : custresponse,
                            "CaptchaConfig" : captchacfg,
                            "ApplicationIntegrationURL" : appinturl,
                          })
      else: # column list
        results.append( { "WebACLId": ' ',
                          "WebACLName" : ' ',
                          "Description" : ' ',
                          "LockToken" : ' ',
                          "ARN" : ' ',
                          "DefaultAction" : ' ',
                          "Rules" : ' ',
                          "VisibilityConfig" : ' ',
                          "Capacity" : ' ',
                          "PreProcessFirewallManagerRuleGroups" : ' ',
                          "PostProcessFirewallManagerRuleGroups" : ' ',
                          "ManagedByFirewallManager" : ' ',
                          "LabelNamespace" : ' ',
                          "CustomResponseBodies" : ' ',
                          "CaptchaConfig" : ' ',
                          "ApplicationIntegrationURL" : list(' '),
                        })
    else:
      klogger.error("call error : %d", webacls["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "WebACLId": 'ERROR CHECK',
                        "WebACLName" : 'ERROR CHECK',
                        "Description" : 'ERROR CHECK',
                        "LockToken" : 'ERROR CHECK',
                        "ARN" : 'ERROR CHECK',
                        "DefaultAction" : 'ERROR CHECK',
                        "Rules" : 'ERROR CHECK',
                        "VisibilityConfig" : 'ERROR CHECK',
                        "Capacity" : 'ERROR CHECK',
                        "PreProcessFirewallManagerRuleGroups" : 'ERROR CHECK',
                        "PostProcessFirewallManagerRuleGroups" : 'ERROR CHECK',
                        "ManagedByFirewallManager" : 'ERROR CHECK',
                        "LabelNamespace" : 'ERROR CHECK',
                        "CustomResponseBodies" : 'ERROR CHECK',
                        "CaptchaConfig" : 'ERROR CHECK',
                        "ApplicationIntegrationURL" : list(' '),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("wafv2.list_web_acls(),%s", othererr)
    results.append( { "WebACLId": 'ERROR CHECK',
                      "WebACLName" : 'ERROR CHECK',
                      "Description" : 'ERROR CHECK',
                      "LockToken" : 'ERROR CHECK',
                      "ARN" : 'ERROR CHECK',
                      "DefaultAction" : 'ERROR CHECK',
                      "Rules" : 'ERROR CHECK',
                      "VisibilityConfig" : 'ERROR CHECK',
                      "Capacity" : 'ERROR CHECK',
                      "PreProcessFirewallManagerRuleGroups" : 'ERROR CHECK',
                      "PostProcessFirewallManagerRuleGroups" : 'ERROR CHECK',
                      "ManagedByFirewallManager" : 'ERROR CHECK',
                      "LabelNamespace" : 'ERROR CHECK',
                      "CustomResponseBodies" : 'ERROR CHECK',
                      "CaptchaConfig" : 'ERROR CHECK',
                      "ApplicationIntegrationURL" : list(' '),
                    })
  finally:
    return results

def get_web_acl(Name, Scope, Id):
  '''
    search waf web acl
  '''
#   klogger_dat.debug('waf web acl')

  try:
    result = None
    wafv2 = WAFV2_session
    # klogger.debug(f'{Name}, {Scope}, {Id}')
    webacl = wafv2.get_web_acl(Name=Name, Scope=Scope, Id=Id)
    # klogger.debug("%s", webacl)
    if 200 == webacl["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",webacl["WebACL"])
      result = webacl
    else:
      klogger.error("call error : %d", webacl["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("wafv2.get_web_acl(),%s", othererr)
  finally:
    return result

def list_rule_groups(Scope):
  '''
    search waf rule groups
  '''
  klogger_dat.debug('waf rule groups')

  try:
    results = [] 
    wafv2 = WAFV2_session
    rulegrps = wafv2.list_rule_groups(Scope=Scope)
    # klogger_dat.debug("%s", rules)
    if 200 == rulegrps["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(rulesets["RuleGroups"])
      if 'RuleGroups' in rulegrps and len(rulegrps["RuleGroups"]) > 0 :
        for rulegrp in rulegrps["RuleGroups"]:
        #   klogger_dat.debug(rulegrp)
          id = rulegrp['Id'] if 'Id' in rulegrp else ' '
          name = rulegrp['Name'] if 'Name' in rulegrp else ' '
          description = rulegrp['Description'] if 'Description' in rulegrp else ' '
          locktoken = rulegrp['LockToken'] if 'LockToken' in rulegrp else ' '
          arns = rulegrp['ARN'] if 'ARN' in rulegrp else ' '
          rulegrpinfo = get_rule_group(name, 'REGIONAL', id)
        #   klogger.debug(rulegrpinfo)
          visiblecfg = ' '; lblnamespace = ' '; custresponse = ' '; rules = []; availablelabels = []; consumedlbls = [];
          if rulegrpinfo != None :
            if 'Rules' in rulegrpinfo :
              for rule in rulegrpinfo['Rules'] :
                rules.append(str(rule))
            visiblecfg = str(rulegrpinfo['VisibilityConfig']) if 'VisibilityConfig' in rulegrpinfo else ' '
            lblnamespace = rulegrpinfo['LabelNamespace'] if 'LabelNamespace' in rulegrpinfo else ' '
            custresponse = str(rulegrpinfo['CustomResponseBodies']) if 'CustomResponseBodies' in rulegrpinfo else ' '
            if 'AvailableLabels' in rulegrpinfo :
              for avllbl in rulegrpinfo['AvailableLabels']:
                availablelabels.append(avllbl['Name'])
            if 'ConsumedLabels' in rulegrpinfo :
              for consumedlbl in rulegrpinfo['ConsumedLabels'] :
                consumedlbls.append(consumedlbl['Name'])
          # list count sync with space
          utils.ListSyncCountWithSpace(rules, availablelabels, consumedlbls)

          results.append( { "RuleGroupId": id,
                            "RuleGroupName" : name,
                            "Description" : description,
                            "LockToken" : locktoken,
                            "ARN" : arns,
                            "Rules" : rules,
                            "VisibilityConfig" : visiblecfg,
                            "LabelNamespace" : lblnamespace,
                            "CustomResponseBodies" : custresponse,
                            "AvailableLabels" : availablelabels,
                            "ConsumedLabels" : consumedlbls,
                          })
      else: # column list
        results.append( { "RuleGroupId": ' ',
                          "RuleGroupName" : list(' '),
                          "Description" : ' ',
                          "LockToken" : ' ',
                          "ARN" : ' ',
                          "Rules" : ' ',
                          "VisibilityConfig" : ' ',
                          "LabelNamespace" : ' ',
                          "CustomResponseBodies" : ' ',
                          "AvailableLabels" : ' ',
                          "ConsumedLabels" : ' ',
                        })
    else:
      klogger.error("call error : %d", rulegrps["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "RuleGroupId": 'ERROR CHECK',
                        "RuleGroupName" : list(' '),
                        "Description" : 'ERROR CHECK',
                        "LockToken" : 'ERROR CHECK',
                        "ARN" : 'ERROR CHECK',
                        "Rules" : 'ERROR CHECK',
                        "VisibilityConfig" : 'ERROR CHECK',
                        "LabelNamespace" : 'ERROR CHECK',
                        "CustomResponseBodies" : 'ERROR CHECK',
                        "AvailableLabels" : 'ERROR CHECK',
                        "ConsumedLabels" : 'ERROR CHECK',
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("wafv2.list_rule_groups(),%s", othererr)
    results.append( { "RuleGroupId": 'ERROR CHECK',
                      "RuleGroupName" : list(' '),
                      "Description" : 'ERROR CHECK',
                      "LockToken" : 'ERROR CHECK',
                      "ARN" : 'ERROR CHECK',
                      "Rules" : 'ERROR CHECK',
                      "VisibilityConfig" : 'ERROR CHECK',
                      "LabelNamespace" : 'ERROR CHECK',
                      "CustomResponseBodies" : 'ERROR CHECK',
                      "AvailableLabels" : 'ERROR CHECK',
                      "ConsumedLabels" : 'ERROR CHECK',
                    })
  finally:
    return results

def get_rule_group(Name, Scope, Id):
  '''
    search waf rule group
  '''
#   klogger_dat.debug('waf rule group')

  try:
    result = None
    wafv2 = WAFV2_session
    # klogger.debug(f'{Name}, {Scope}, {Id}')
    rulegrp = wafv2.get_rule_group(Name=Name,Scope=Scope,Id=Id)
    # klogger.debug("%s", rulegrp)
    if 200 == rulegrp["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",rulegrp["RuleGroup"])
      if 'RuleGroup' in rulegrp :
        result = rulegrp['RuleGroup']
    else:
      klogger.error("call error : %d", rulegrp["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("wafv2.get_rule_group(),%s", othererr)
  finally:
    return result
    
def list_ip_sets(Scope):
  '''
    search waf ip sets
  '''
  klogger_dat.debug('waf ip sets')

  try:
    results = [] 
    global WAFV2_session

    WAFV2_session = utils.get_session('wafv2')
    wafv2 = WAFV2_session
    ipsets = wafv2.list_ip_sets(Scope=Scope)
    # klogger_dat.debug("%s", ipsets)
    if 200 == ipsets["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger.debug(ipsets["IPSets"])
      if 'IPSets' in ipsets and len(ipsets["IPSets"]) > 0 :
        for ipset in ipsets["IPSets"]:
        #   klogger.debug(ipset)
          id = ipset['Id'] if 'Id' in ipset else ' '
          name = ipset['Name'] if 'Name' in ipset else ' '
          ipsetdescription = ipset['Description'] if 'Description' in ipset else ' '
          locktoken = ipset['LockToken'] if 'LockToken' in ipset else ' '
          arns = ipset['ARN'] if 'ARN' in ipset else ' '
          ipsetinfo = get_ip_set(name, Scope, id)
          addresses = [];
          if ipsetinfo != None :
            if 'IPSet' in ipsetinfo :
              if 'Addresses' in ipsetinfo['IPSet'] :
                for address in ipsetinfo['IPSet']['Addresses'] :
                  addresses.append(address)
              ipversion = ipsetinfo['IPSet']['IPAddressVersion'] if 'IPAddressVersion' in ipsetinfo['IPSet'] else ' '
          # list count sync with space
          utils.ListSyncCountWithSpace(addresses)
  
          results.append( { "IPSetId": id,
                            "IPSetName" : name,
                            "IPSetDescription" : ipsetdescription,
                            "LockToken" : locktoken,
                            "ARN" : arns,
                            "IPAddressVersion" : ipversion,
                            "Addresses" : addresses,
                          })
      else: # column list
        results.append( { "IPSetId": ' ',
                          "IPSetName" : list(' '),
                          "IPSetDescriptors": ' ',
                          "LockToken" : ' ',
                          "ARN" : ' ',
                          "IPAddressVersion" : ' ',
                          "Addresses" : ' ',
                        })
    else:
      klogger.error("call error : %d", ipsets["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "IPSetId": 'ERROR CHECK',
                        "IPSetName" : list(' '),
                        "IPSetDescriptors": 'ERROR CHECK',
                        "LockToken" : 'ERROR CHECK',
                        "ARN" : 'ERROR CHECK',
                        "IPAddressVersion" : 'ERROR CHECK',
                        "Addresses" : 'ERROR CHECK',
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("wafv2.list_ip_sets(),%s", othererr)
    results.append( { "IPSetId": 'ERROR CHECK',
                      "IPSetName" : list(' '),
                      "IPSetDescriptors": 'ERROR CHECK',
                      "LockToken" : 'ERROR CHECK',
                      "ARN" : 'ERROR CHECK',
                      "IPAddressVersion" : 'ERROR CHECK',
                      "Addresses" : 'ERROR CHECK',
                    })
  finally:
    return results

def get_ip_set(Name, Scope, Id):
  '''
    search waf ip set
  '''
#   klogger_dat.debug('waf ip set')

  try:
    result = None
    wafv2 = WAFV2_session
    # klogger.debug(f'{Name}, {Scope}, {Id}')
    ipset = wafv2.get_ip_set(Name=Name, Scope=Scope, Id=Id)
    # klogger.debug("%s", ipset)
    if 200 == ipset["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug("%s",ipset["IPSet"])
      result = ipset
    else:
      klogger.error("call error : %d", ipset["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("wafv2.get_ip_set(),%s", othererr)
  finally:
    return result
    
def main(argv):

  list_rules()
  list_rule_groups()

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
