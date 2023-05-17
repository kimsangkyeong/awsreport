####################################################################################################
# 
# Purpose   : get list backup
# Source    : backup.py
# Usage     : python backup.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.07     first create
#  1.1      2023.05.17     add session handling logic
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backup.html
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

def list_backup_plans():
  '''
    search backup  
  '''
  klogger_dat.debug('backup')
  try:
    results = [] 
    global BACKUP_session

    BACKUP_session = utils.get_session('backup')
    backup = BACKUP_session
    bkplans = backup.list_backup_plans(IncludeDeleted=False)
    # klogger_dat.debug(bkplans)
    if 200 == bkplans["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(bkplans["BackupPlansList"])
      if 'BackupPlansList' in bkplans and  len(bkplans["BackupPlansList"]) > 0 :
        for bkplan in bkplans["BackupPlansList"]:
        #   klogger_dat.debug(bkplan)
          resorcetypes = []; backupoptions = [];
          if 'AdvancedBackupSettings' in bkplan :
            for advset in bkplan['AdvancedBackupSettings'] :
              resorcetypes.append(advset['ResourceType'] if 'ResourceType' in advset else ' ')
              backupoptions.append(advset['BackupOptions'] if 'BackupOptions' in advset else ' ')

          rules = get_backup_plan(bkplan['BackupPlanId'], bkplan['VersionId'])
        #   klogger_dat.debug(rules)
          rulenames = []; tbkvaultnames = []; scheduleexpressions = []; startminutes = []; completminutes = [];
          lifecycles = []; recoverpointtags = [];
          for rule in rules:
            rulenames.append(rule['RuleName'])
            tbkvaultnames.append(rule['TargetBackupVaultName'] if 'TargetBackupVaultName' in rule else ' ')
            scheduleexpressions.append(rule['ScheduleExpression'] if 'ScheduleExpression' in rule else ' ')
            startminutes.append(rule['StartWindowMinutes'])
            completminutes.append(rule['CompletionWindowMinutes'])
            lifecycles.append(rule['Lifecycle'] if 'Lifecycle' in rule else ' ')
            recoverpointtags.append(rule['RecoveryPointTags'] if 'RecoveryPointTags' in rule else ' ' )

          selections = list_backup_selections(bkplan['BackupPlanId'])
        #   klogger_dat.debug(selections)
          selectnames = []; iamrolearns = []; bkselection = {}; resources = []; listoftags = [];
          notresources = []; conditions = [];
          for select in selections:
            selectnames.append(select['SelectionName'])
            iamrolearns.append(select['IamRoleArn'] if 'IamRoleArn' in select else ' ')
            bkselection = get_backup_selection(bkplan['BackupPlanId'], select['SelectionId'])
            # klogger_dat.debug(bkselection)
            if bkselection != None :
              if 'Resources' in bkselection :
                for item in bkselection['Resources'] :
                  resources.append(item)
              if 'ListOfTags' in bkselection :
                for item in bkselection['ListOfTags'] :
                  listoftags.append(str(item))
              if 'NotResources' in bkselection :
                for item in bkselection['NotResources'] :
                  notresources.append(item)
              if 'Conditions' in bkselection :
                conditions.append(str(bkselection['Conditions']))
          # list count sync with space
          utils.ListSyncCountWithSpace(resorcetypes, backupoptions, rulenames, tbkvaultnames, scheduleexpressions,
                                       startminutes, completminutes, lifecycles, recoverpointtags,
                                       selectnames, iamrolearns, resources, listoftags, notresources, conditions
                                      )

          results.append( { "BackupPlanName": bkplan['BackupPlanName'],
                            "BackupPlanArn" : bkplan['BackupPlanArn'],
                            "BackupPlanId" : bkplan['BackupPlanId'],
                            "VersionId" : bkplan['VersionId'],
                            "RuleName" : rulenames, 
                            "TargetBackupVaultName" : tbkvaultnames,
                            "ScheduleExpression" : scheduleexpressions,
                            "StartWindowMinutes" : startminutes,
                            "CompletionWindowMinutes" : completminutes,
                            "Lifecycle" : lifecycles,
                            "SelectionName" : selectnames,
                            "IamRoleArn" : iamrolearns,
                            "Resources" : resources,
                            "ListOfTags" : listoftags,
                            "NotResources" : notresources,
                            "Conditions" : conditions,
                            "RecoveryPointTags" : recoverpointtags,
                            "CreationDate": bkplan['CreationDate'].strftime('%Y-%m-%d'),
                            "LastExecutionDate" : bkplan['LastExecutionDate'].strftime('%Y-%m-%d') if 'LastExecutionDate' in bkplan else ' ',
                            "ResourceType": resorcetypes,
                            "BackupOptions" : backupoptions,
                          })
      else: # column list
        results.append( { "BackupPlanName": ' ',
                          "BackupPlanArn" : ' ',
                          "BackupPlanId" : ' ',
                          "VersionId" : ' ',
                          "RuleName" : ' ',
                          "TargetBackupVaultName" : ' ',
                          "ScheduleExpression" : ' ',
                          "StartWindowMinutes" : ' ',
                          "CompletionWindowMinutes" : ' ',
                          "Lifecycle" : ' ',
                          "SelectionName" : ' ',
                          "IamRoleArn" : ' ',
                          "Resources" : ' ',
                          "ListOfTags" : ' ',
                          "NotResources" : ' ',
                          "Conditions" : ' ',
                          "RecoveryPointTags" : ' ',
                          "CreationDate": ' ',
                          "LastExecutionDate" : ' ',
                          "ResourceType": ' ',
                          "BackupOptions" : list(' '),
                        })
    else:
      klogger.error("call error : %d", bkplans["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "BackupPlanName": 'ERROR CHECK',
                        "BackupPlanArn" : 'ERROR CHECK',
                        "BackupPlanId" : 'ERROR CHECK',
                        "VersionId" : 'ERROR CHECK',
                        "RuleName" : 'ERROR CHECK',
                        "TargetBackupVaultName" : 'ERROR CHECK',
                        "ScheduleExpression" : 'ERROR CHECK',
                        "StartWindowMinutes" : 'ERROR CHECK',
                        "CompletionWindowMinutes" : 'ERROR CHECK',
                        "Lifecycle" : 'ERROR CHECK',
                        "SelectionName" : 'ERROR CHECK',
                        "IamRoleArn" : 'ERROR CHECK',
                        "Resources" : 'ERROR CHECK',
                        "ListOfTags" : 'ERROR CHECK',
                        "NotResources" : 'ERROR CHECK',
                        "Conditions" : 'ERROR CHECK',
                        "RecoveryPointTags" : 'ERROR CHECK',
                        "CreationDate": 'ERROR CHECK',
                        "LastExecutionDate" : 'ERROR CHECK',
                        "ResourceType": 'ERROR CHECK',
                        "BackupOptions" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("backup.list_backup_plans(),%s", othererr)
    results.append( { "BackupPlanName": 'ERROR CHECK',
                      "BackupPlanArn" : 'ERROR CHECK',
                      "BackupPlanId" : 'ERROR CHECK',
                      "VersionId" : 'ERROR CHECK',
                      "RuleName" : 'ERROR CHECK',
                      "TargetBackupVaultName" : 'ERROR CHECK',
                      "ScheduleExpression" : 'ERROR CHECK',
                      "StartWindowMinutes" : 'ERROR CHECK',
                      "CompletionWindowMinutes" : 'ERROR CHECK',
                      "Lifecycle" : 'ERROR CHECK',
                      "SelectionName" : 'ERROR CHECK',
                      "IamRoleArn" : 'ERROR CHECK',
                      "Resources" : 'ERROR CHECK',
                      "ListOfTags" : 'ERROR CHECK',
                      "NotResources" : 'ERROR CHECK',
                      "Conditions" : 'ERROR CHECK',
                      "RecoveryPointTags" : 'ERROR CHECK',
                      "CreationDate": 'ERROR CHECK',
                      "LastExecutionDate" : 'ERROR CHECK',
                      "ResourceType": 'ERROR CHECK',
                      "BackupOptions" : list('ERROR CHECK'),
                    })
  finally:
    return results

def get_backup_selection(BackupPlanId, SelectionId):
  '''
    search backup selection
  '''
#   klogger_dat.debug('backup selection')
  try:
    result = None 
    backup = BACKUP_session
    bkselection = backup.get_backup_selection(BackupPlanId=BackupPlanId, SelectionId=SelectionId)
    # klogger_dat.debug(bkselection)
    if 200 == bkselection["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(bkselection["BackupSelection"])
      result = bkselection["BackupSelection"]
    else:
      klogger.error("call error : %d", bkselection["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("backup.get_backup_selection(),%s", othererr)
  finally:
    return result

def get_backup_plan(BackupPlanId, VersionId):
  '''
    search backup plan
  '''
#   klogger_dat.debug('backup plan')
  try:
    results = [] 
    backup = BACKUP_session
    bkplan = backup.get_backup_plan(BackupPlanId=BackupPlanId, VersionId=VersionId)
    # klogger_dat.debug(bkplan)
    if 200 == bkplan["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(bkplan["BackupPlan"])
      if 'Rules' in bkplan["BackupPlan"] :
        results = bkplan["BackupPlan"]['Rules']
    else:
      klogger.error("call error : %d", bkplan["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("backup.get_backup_plan(),%s", othererr)
  finally:
    return results


def list_backup_selections(BackupPlanId):
  '''
    search backup plan selection
  '''
#   klogger_dat.debug('backup plan selection')
  try:
    results = [] 
    backup = BACKUP_session
    select = backup.list_backup_selections(BackupPlanId=BackupPlanId)
    # klogger_dat.debug(select)
    if 200 == select["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(select["BackupSelectionsList"])
      if 'BackupSelectionsList' in select :
        results = select["BackupSelectionsList"]
    else:
      klogger.error("call error : %d", select["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("backup.list_backup_selections(),%s", othererr)
  finally:
    return results

def list_backup_vaults():
  '''
    search backup vaults 
  '''
  klogger_dat.debug('backup vault')
  try:
    results = [] 
    backup = BACKUP_session
    bkvaults = backup.list_backup_vaults()
    # klogger_dat.debug(bkvaults)
    if 200 == bkvaults["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(bkvaults["BackupVaultList"])
      if 'BackupVaultList' in bkvaults and len(bkvaults["BackupVaultList"]) > 0 :
        for bkvault in bkvaults["BackupVaultList"]:
        #   klogger_dat.debug(bkvault)

          results.append( { "BackupVaultName": bkvault['BackupVaultName'],
                            "BackupVaultArn" : bkvault['BackupVaultArn'],
                            "KmsKeyAlias" : list(' '),
                            "EncryptionKeyArn" : bkvault['EncryptionKeyArn'] if 'EncryptionKeyArn' in bkvault else ' ',
                            "CreationDate": bkvault['CreationDate'].strftime('%Y-%m-%d'),
                            "NumberOfRecoveryPoints" : bkvault['NumberOfRecoveryPoints'] if 'NumberOfRecoveryPoints' in bkvault else ' ',
                            "MinRetentionDays": bkvault['MinRetentionDays'] if 'MinRetentionDays' in bkvault else ' ',
                            "MaxRetentionDays" : bkvault['MaxRetentionDays'] if 'MaxRetentionDays' in bkvault else ' ',
                          })
      else: # column list
        results.append( { "BackupVaultName": ' ',
                          "BackupVaultArn" : ' ',
                          "KmsKeyAlias" : ' ',
                          "EncryptionKeyArn" : ' ',
                          "CreationDate" : ' ',
                          "NumberOfRecoveryPoints" : ' ',
                          "MinRetentionDays" : ' ',
                          "MaxRetentionDays" : list(' '),
                        })
    else:
      klogger.error("call error : %d", bkvaults["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "BackupVaultName": 'ERROR CHECK',
                        "BackupVaultArn" : 'ERROR CHECK',
                        "KmsKeyAlias" : 'ERROR CHECK',
                        "EncryptionKeyArn" : 'ERROR CHECK',
                        "CreationDate" : 'ERROR CHECK',
                        "NumberOfRecoveryPoints" : 'ERROR CHECK',
                        "MinRetentionDays" : 'ERROR CHECK',
                        "MaxRetentionDays" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("backup.list_backup_vaults(),%s", othererr)
    results.append( { "BackupVaultName": 'ERROR CHECK',
                      "BackupVaultArn" : 'ERROR CHECK',
                      "KmsKeyAlias" : 'ERROR CHECK',
                      "EncryptionKeyArn" : 'ERROR CHECK',
                      "CreationDate" : 'ERROR CHECK',
                      "NumberOfRecoveryPoints" : 'ERROR CHECK',
                      "MinRetentionDays" : 'ERROR CHECK',
                      "MaxRetentionDays" : list('ERROR CHECK'),
                    })
  finally:
    return results

def main(argv):

  list_backup_plans() 
  list_backup_vaults()

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
