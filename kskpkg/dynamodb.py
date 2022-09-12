####################################################################################################
# 
# Purpose   : get list dynamodb info
# Source    : dynamodb.py
# Usage     : python dynamodb.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.11     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
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

def list_tables():
  '''
    search DYNAMODB tables
  '''
  klogger_dat.debug('dynamodb tables')
  try:
    results = [] 
    dynamodb=boto3.client('dynamodb')
    tables = dynamodb.list_tables()
    # klogger_dat.debug(tables)
    if 200 == tables["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(tables["TableNames"])
      if 'TableNames' in tables and len(tables["TableNames"]) > 0 :
        for tablename in tables["TableNames"]:
        #   klogger_dat.debug(tablename)
          tableinfo = describe_table(tablename)
        #   klogger.debug(tableinfo)
          tablestatus = ' '; createdtm = ' '; tablesizebytes = ' '; itemcount = ' '; tablearn = ' '; tableid = ' ';
          attributes = []; keyschemas = []; provithrouputs = []; billsummary = []; localsecondindexes = []; globalsecondindexes = [];
          tblclasssummary = []; globaltableversion = []; replicas = []; ssedescription = [];
          if tableinfo != None :
            tablestatus = tableinfo['TableStatus'] if 'TableStatus' in tableinfo else ' '
            createdtm = tableinfo['CreationDateTime'].strftime('%Y-%m-%d %H:%M') if 'CreationDateTime' in tableinfo else ' '
            tablesizebytes = tableinfo['TableSizeBytes'] if 'TableSizeBytes' in tableinfo else ' '
            itemcount = tableinfo['ItemCount'] if 'ItemCount' in tableinfo else ' '
            tablearn = tableinfo['TableArn'] if 'TableArn' in tableinfo else ' '
            tableid = tableinfo['TableId'] if 'TableId' in tableinfo else ' '
            if 'AttributeDefinitions' in tableinfo :
              for item in tableinfo['AttributeDefinitions'] :
                attributes.append(item)
            if 'KeySchema' in tableinfo :
              for item in tableinfo['KeySchema'] :
                keyschemas.append(item)
            if 'ProvisionedThroughput' in tableinfo :
              provithrouputs.append(tableinfo['ProvisionedThroughput'])
            if 'BillingModeSummary' in tableinfo :
              billsummary.append(tableinfo['BillingModeSummary'])
            if 'LocalSecondaryIndexes' in tableinfo :
              for localidx in tableinfo['LocalSecondaryIndexes'] :
                localsecondindexes.append(localidx)
            if 'GlobalSecondaryIndexes' in tableinfo :
              for globalidx in tableinfo['GlobalSecondaryIndexes'] :
                globalsecondindexes.append(globalidx)
            if 'TableClassSummary' in tableinfo :
              tblclasssummary.append(tableinfo['TableClassSummary'])
            globaltableversion.append(tableinfo['GlobalTableVersion'] if 'GlobalTableVersion' in tableinfo else ' ')
            if 'Replicas' in tableinfo :
              for replica in tableinfo['Replicas'] :
                replicas.append(replica)
            if 'SSEDescription' in tableinfo :
              ssedescription.append(tableinfo['SSEDescription'])
          # list count sync with space
          utils.ListSyncCountWithSpace(attributes, keyschemas, provithrouputs, billsummary, localsecondindexes, 
                                       globalsecondindexes, tblclasssummary, globaltableversion, replicas, ssedescription
                                      )
          
          results.append({ "TableNames" : tablename,
                           "TableStatus" : tablestatus,
                           "CreationDateTime" : createdtm,
                           "TableSizeBytes" : tablesizebytes,
                           "ItemCount" : itemcount,
                           "TableArn" : tablearn,
                           "TableId" : tableid,
                           "AttributeDefinitions" : attributes,
                           "KeySchema" : keyschemas,
                           "ProvisionedThroughput" : provithrouputs,
                           "BillingModeSummary" : billsummary,
                           "LocalSecondaryIndexes" : localsecondindexes,
                           "GlobalSecondaryIndexes" : globalsecondindexes,
                           "TableClassSummary" : tblclasssummary,
                           "GlobalTableVersion" : globaltableversion,
                           "Replicas" : replicas,
                           "SSEDescription" : ssedescription, 
                         })
      else: # column list
        results.append({ "TableNames" : ' ',
                         "TableStatus" :' ',
                         "CreationDateTime" : ' ',
                         "TableSizeBytes" : ' ',
                         "ItemCount" : ' ',
                         "TableArn" : ' ',
                         "TableId" : ' ',
                         "AttributeDefinitions" : ' ',
                         "KeySchema" : ' ',
                         "ProvisionedThroughput" : ' ',
                         "BillingModeSummary" : ' ',
                         "LocalSecondaryIndexes" : ' ',
                         "GlobalSecondaryIndexes" : ' ',
                         "TableClassSummary" : ' ',
                         "GlobalTableVersion" : ' ',
                         "Replicas" : ' ',
                         "SSEDescription" : list(' '),
                       })
    else:
      klogger.error("call error : %d", tables["ResponseMetadata"]["HTTPStatusCode"])
      results.append({ "TableNames" : 'ERROR CHECK',
                       "TableStatus" :'ERROR CHECK',
                       "CreationDateTime" : 'ERROR CHECK',
                       "TableSizeBytes" : 'ERROR CHECK',
                       "ItemCount" : 'ERROR CHECK',
                       "TableArn" : 'ERROR CHECK',
                       "TableId" : 'ERROR CHECK',
                       "AttributeDefinitions" : 'ERROR CHECK',
                       "KeySchema" : 'ERROR CHECK',
                       "ProvisionedThroughput" : 'ERROR CHECK',
                       "BillingModeSummary" : 'ERROR CHECK',
                       "LocalSecondaryIndexes" : 'ERROR CHECK',
                       "GlobalSecondaryIndexes" : 'ERROR CHECK',
                       "TableClassSummary" : 'ERROR CHECK',
                       "GlobalTableVersion" : 'ERROR CHECK',
                       "Replicas" : 'ERROR CHECK',
                       "SSEDescription" : list(' '),
                     })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("dynamodb.list_tables(),%s", othererr)
    results.append({ "TableNames" : 'ERROR CHECK',
                     "TableStatus" :'ERROR CHECK',
                     "CreationDateTime" : 'ERROR CHECK',
                     "TableSizeBytes" : 'ERROR CHECK',
                     "ItemCount" : 'ERROR CHECK',
                     "TableArn" : 'ERROR CHECK',
                     "TableId" : 'ERROR CHECK',
                     "AttributeDefinitions" : 'ERROR CHECK',
                     "KeySchema" : 'ERROR CHECK',
                     "ProvisionedThroughput" : 'ERROR CHECK',
                     "BillingModeSummary" : 'ERROR CHECK',
                     "LocalSecondaryIndexes" : 'ERROR CHECK',
                     "GlobalSecondaryIndexes" : 'ERROR CHECK',
                     "TableClassSummary" : 'ERROR CHECK',
                     "GlobalTableVersion" : 'ERROR CHECK',
                     "Replicas" : 'ERROR CHECK',
                     "SSEDescription" : list(' '),
                   })
  finally:
    return results

def describe_table(TableName):
  '''
    search dynamodb table
  '''
#   klogger_dat.debug('dynamodb table')

  try:
    result = None
    dynamodb=boto3.client('dynamodb')
    # klogger.debug(f'{TableName}')
    table = dynamodb.describe_table(TableName=TableName)
    # klogger.debug("%s", table)
    if 200 == table["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",table["Table"])
      if 'Table' in table :
        result = table['Table']
    else:
      klogger.error("call error : %d", table["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("dynamodb.describe_table(),%s", othererr)
  finally:
    return result

def list_global_tables():
  '''
    search DYNAMODB global tables
  '''
  klogger_dat.debug('dynamodb global tables')
  try:
    results = [] 
    dynamodb=boto3.client('dynamodb')
    gtables = dynamodb.list_global_tables()
    # klogger_dat.debug(gtables)
    if 200 == gtables["ResponseMetadata"]["HTTPStatusCode"]:
    #   klogger_dat.debug(gtables["GlobalTables"])
      if 'GlobalTables' in gtables and len(gtables["GlobalTables"]) > 0 :
        for gtable in gtables["GlobalTables"]:
          klogger_dat.debug(gtable)
          replicationgrp = []; 
          gtablename = gtable['GlobalTableName'] if 'GlobalTableName' in gtable else ' '
          if 'ReplicationGroup' in gtable :
            for repgrp in gtable['ReplicationGroup'] :
              replicationgrp.append(repgrp)
          if 'LastEvaluatedGlobalTableName' in gtables :
            lastgtablename = gtables['LastEvaluatedGlobalTableName']
          tableinfo = describe_global_table(gtablename)
        #   klogger.debug(tableinfo)
          gtablearn = ' '; createdtm = ' '; gtablesgtatus = ' '; 
          if tableinfo != None :
            gtablearn = tableinfo['GlobalTableArn'] if 'GlobalTableArn' in tableinfo else ' '
            createdtm = tableinfo['CreationDateTime'].strftime('%Y-%m-%d %H:%M') if 'CreationDateTime' in tableinfo else ' '
            gtablesgtatus = tableinfo['GlobalTableStatus'] if 'GlobalTableStatus' in tableinfo else ' '
          # list count sync with space
          utils.ListSyncCountWithSpace(replicationgrp
                                      )
          
          results.append({ "GlobalTableName" : gtablename,
                           "ReplicationGroup" : replicationgrp,
                           "LastEvaluatedGlobalTableName" : lastgtablename,
                           "GlobalTableArn" : gtablearn,
                           "CreationDateTime" : createdtm, 
                           "GlobalTableStatus" : gtablesgtatus,
                         })
      else: # column list
        lastgtablename = ' '
        if 'LastEvaluatedGlobalTableName' in gtables :
          lastgtablename = gtables['LastEvaluatedGlobalTableName']
        results.append({ "GlobalTableName" : ' ',
                         "ReplicationGroup" : list(' '),
                         "LastEvaluatedGlobalTableName" : lastgtablename,
                         "GlobalTableArn" : ' ',
                         "CreationDateTime" : ' ',
                         "GlobalTableStatus" : ' ',
                       })
    else:
      klogger.error("call error : %d", gtables["ResponseMetadata"]["HTTPStatusCode"])
      results.append({ "GlobalTableName" : 'ERROR CHECK',
                       "ReplicationGroup" : 'ERROR CHECK',
                       "LastEvaluatedGlobalTableName" : 'ERROR CHECK',
                       "GlobalTableArn" : 'ERROR CHECK',
                       "CreationDateTime" : 'ERROR CHECK',
                       "GlobalTableStatus" : list(' '),
                     })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("dynamodb.list_global_tables(),%s", othererr)
    results.append({ "GlobalTableName" : 'ERROR CHECK',
                     "ReplicationGroup" : 'ERROR CHECK',
                     "LastEvaluatedGlobalTableName" : 'ERROR CHECK',
                     "GlobalTableArn" : 'ERROR CHECK',
                     "CreationDateTime" : 'ERROR CHECK',
                     "GlobalTableStatus" : list(' '),
                   })
  finally:
    return results

def describe_global_table(GlobalTableName):
  '''
    search dynamodb global table
  '''
#   klogger_dat.debug('dynamodb global table')

  try:
    result = None
    dynamodb=boto3.client('dynamodb')
    # klogger.debug(f'{GlobalTableName}')
    gtable = dynamodb.describe_global_table(GlobalTableName=GlobalTableName)
    # klogger.debug("%s", gtable)
    if 200 == gtable["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",gtable["GlobalTableDescription"])
      if 'GlobalTableDescription' in gtable :
        result = gtable['GlobalTableDescription']
    else:
      klogger.error("call error : %d", gtable["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("dynamodb.describe_global_table(),%s", othererr)
  finally:
    return result

def main(argv):

  list_global_tables()
  list_tables() 

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
