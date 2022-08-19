####################################################################################################
# 
# Purpose : aws operator main program
# Source  : awsreport.py
# Usage   : python awsreport.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2019.09.06     first create
#          
####################################################################################################
### This first line is for modules to work with Python 2 or 3
from __future__ import print_function
import os
import sys, getopt
import argparse
import importlib
import kskpkg.config.awsglobal as awsglobal
import numpy as np   # pip install numpy
import pandas as pd  # pip install pandas


# 현재 디렉토리
path_cwd = os.getcwd()
def global_config_init():
  global klogger
  global klogger_dat

  # Main에서 log config 경로 전달
  awsglobal.init_logger(path_cwd + '/kskpkg/config/logging.conf')
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat

  return True

def getobjectstring(content):
  '''
     extract module string and function string from content by delimeter '.'
  '''
  idx = content.rfind('.')
  modstr = content[:idx]
  funcstr = content[idx+1:]
  return modstr, funcstr

def executefunc(objstr, regions):
  '''
     execute function from reserved function string
  '''
  try:
    objlist = getobjectstring(objstr)
    objmodule = importlib.import_module(objlist[0])
    objfunction = getattr(objmodule, objlist[1]) 

    # dynamic function call
    results = objfunction(regions)

    return results

  except Exception as othererr:
    print("executefunc() %s" % othererr)
    return False

def cmd_parse():
  cmdlines = [
      # data means => 0:option, 1:dest , 2:required , 3:action , 4:const , 5:help
      { '-i' : ('instance'  , False, 'store_const', 'awspkg.ec2.ec2instanceslist.describe_instances',
                              'ec2instance operation(describe)'                                       )},
      { '-v' : ('vpc'       , False, 'store_const', 'awspkg.ec2.ec2vpcslist.describe_vpcs',
                              'ec2vpc operation(describe)'                                            )},
             ]

  parser = argparse.ArgumentParser(description='aws operation tool for datalake infra')

  for cmdline in cmdlines:
    for key, dtuple in cmdline.items():
      dlist = list(dtuple)
      if dlist[2] == 'append': # action is append type
        parser.add_argument(key, dest=dlist[0], required=dlist[1], action=dlist[2],                 help=dlist[4])
      else:                    # action is store_const type
        parser.add_argument(key, dest=dlist[0], required=dlist[1], action=dlist[2], const=dlist[3], help=dlist[4])

  return parser.parse_args()

def main(argv):

  global_config_init()

  results = executefunc("kskpkg.ec2.describe_instances", ['ap-northeast-2'])

  exit(1)

  results = executefunc("kskpkg.ec2.describe_vpcs", ['ap-northeast-2'])
  df = pd.DataFrame()
  for result in results:
    df = pd.concat([df, pd.DataFrame(result)], ignore_index=True)
    klogger.debug(df.values)

  output_file = f'{path_cwd}/output.xlsx'
  if os.path.exists(output_file):
    with pd.ExcelWriter(f'{path_cwd}/output.xlsx', mode='a') as writer:
      df.to_excel(writer, sheet_name='vpc', engine='openpyxl') # pip install openpyxl
  else:
    with pd.ExcelWriter(f'{path_cwd}/output.xlsx') as writer:
      df.to_excel(writer, sheet_name='vpc', engine='openpyxl') # pip install openpyxl

#  args = cmd_parse()
#  if args.instance    != None:
#    executefunc(args.instance, args.regions)

if __name__ == "__main__":
   main(sys.argv[:])

