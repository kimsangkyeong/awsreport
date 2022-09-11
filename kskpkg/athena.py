####################################################################################################
# 
# Purpose   : get list athena
# Source    : athena.py
# Usage     : python athena.py 
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.09.11     first create
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/athena.html
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


def list_data_catalogs():
  '''
    search athena
  '''
  klogger_dat.debug('athena')

  try:
    results = [] 
    athena=boto3.client('athena')
    catalogs = athena.list_data_catalogs()
    # klogger_dat.debug("%s", catalogs)
    if 200 == catalogs["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug(catalogs["DataCatalogsSummary"])
      if 'DataCatalogsSummary' in catalogs and len(catalogs["DataCatalogsSummary"]) > 0 :
        for summaryinfo in catalogs["DataCatalogsSummary"]:
          # klogger_dat.debug(summaryinfo)
          databases = list_databases(summaryinfo['CatalogName'])
          dbnames = []; descriptions = []; parameters = []; tables = [];
          for database in databases :
            dbnames.append(database['Name'])
            descriptions.append(database['Description'] if 'Description' in database else ' ')
            parameters.append(database['Parameters'] if 'Parameters' in database else ' ')
            tablemetadatas = list_table_metadata(summaryinfo['CatalogName'], database['Name'])
            for tableinfo in tablemetadatas :
              tables.append(tableinfo)
          # list count sync with space
          utils.ListSyncCountWithSpace(dbnames, descriptions, parameters, tables)

          results.append( { "CatalogName": summaryinfo['CatalogName'] if 'CatalogName' in summaryinfo else ' ',
                            "Type" : summaryinfo['Type'] if 'Type' in summaryinfo else ' ',
                            "DBName" : dbnames,
                            "DBDescription" : descriptions,
                            "DBParameters" : parameters,
                            "Tables" : tables,
                          })
      else: # column list
        results.append( { "CatalogName": ' ',
                          "Type" : ' ',
                          "DBName" : ' ',
                          "DBDescription" : ' ',
                          "DBParameters" : ' ',
                          "Tables" : ' ',
                        })
    else:
      klogger.error("call error : %d", catalogs["ResponseMetadata"]["HTTPStatusCode"])
      results.append( { "CatalogName": 'ERROR CHECK',
                        "Type" : 'ERROR CHECK',
                        "DBName" : 'ERROR CHECK',
                        "DBDescription" : 'ERROR CHECK',
                        "DBParameters" : 'ERROR CHECK',
                        "Tables" : list('ERROR CHECK'),
                      })
    # klogger.debug(results)
  except Exception as othererr:
    klogger.error("athena.list_data_catalogs(),%s", othererr)
    results.append( { "CatalogName": 'ERROR CHECK',
                      "Type" : 'ERROR CHECK',
                      "DBName" : 'ERROR CHECK',
                      "DBDescription" : 'ERROR CHECK',
                      "DBParameters" : 'ERROR CHECK',
                      "Tables" : list('ERROR CHECK'),
                    })
  finally:
    return results

def list_databases(CatalogName):
  '''
    search athena databases
  '''
#   klogger_dat.debug('athena databases')

  try:
    results = []
    athena=boto3.client('athena')
    # klogger.debug(f'{CatalogName}')
    databases = athena.list_databases(CatalogName=CatalogName)
    # klogger.debug("%s", databases)
    if 200 == databases["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",databases["DatabaseList"])
      if 'DatabaseList' in databases :
        results = databases['DatabaseList']
    else:
      klogger.error("call error : %d", databases["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("athena.list_databases(),%s", othererr)
  finally:
    return results

def list_table_metadata(CatalogName, DatabaseName):
  '''
    search athena tables
  '''
#   klogger_dat.debug('athena tables')

  try:
    results = []
    athena=boto3.client('athena')
    # klogger.debug(f'{CatalogName, DatabaseName}')
    tables = athena.list_table_metadata(CatalogName=CatalogName, DatabaseName=DatabaseName)
    # klogger.debug("%s", tables)
    if 200 == tables["ResponseMetadata"]["HTTPStatusCode"]:
      # klogger_dat.debug("%s",tables["TableMetadataList"])
      if 'TableMetadataList' in tables :
        results = tables['TableMetadataList']
    else:
      klogger.error("call error : %d", tables["ResponseMetadata"]["HTTPStatusCode"])
    # klogger.debug(result)
  except Exception as othererr:
    klogger.error("athena.list_table_metadata(),%s", othererr)
  finally:
    return results

def main(argv):

  list_data_catalogs()

  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])
