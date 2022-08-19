####################################################################################################
# 
# Purpose : aws operator main program
# Source  : awsreport.py
# Usage   : python awsreport.py 
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2019.09.06     first create
# ref     : https://pandas.pydata.org/docs/reference/api/pandas.ExcelWriter.html, .to_excel.html
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
# OS 판단  : win32, linux, cygwin, darwin, aix
my_os = sys.platform
#print(my_os)
if my_os == "linux":
  path_logconf = path_cwd + '/kskpkg/config/logging.conf'
  output_file = f'{path_cwd}/output.xlsx'
else:
  path_logconf = path_cwd + '\kskpkg\config\logging.conf'
  output_file = f'{path_cwd}\output.xlsx'

def global_config_init():
  global klogger
  global klogger_dat

  # Main에서 log config 경로 전달
  awsglobal.init_logger(path_logconf)
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
  # logger setting 
  global_config_init()

  # vpcs
  results = executefunc("kskpkg.ec2.describe_vpcs", ['ap-northeast-2'])
  df_vpc = pd.DataFrame()
  for result in results:
    df_tmp = pd.DataFrame(result)
    df_vpc = pd.concat([df_vpc, df_tmp], ignore_index=True)
    klogger.debug(df_vpc.values)
  # instances
  results = executefunc("kskpkg.ec2.describe_instances", ['ap-northeast-2'])
  df_ins = pd.DataFrame()
  klogger.debug(df_ins.values)
  for result in results:
    df_tmp = pd.DataFrame(result)
    df_ins = pd.concat([df_ins, df_tmp], ignore_index=True)
    klogger.debug(df_ins.values)
  exit(1)
  # to_excel 
  if os.path.exists(output_file):
    with pd.ExcelWriter(output_file, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
      df_vpc.to_excel(writer, sheet_name='vpc', index=False) # pip install openpyxl
      df_ins.to_excel(writer, sheet_name='instance', index=False) 
  else:
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
      df_vpc.to_excel(writer, sheet_name='vpc', index=False)
      df_ins.to_excel(writer, sheet_name='instance', index=False) 

#  args = cmd_parse()
#  if args.instance    != None:
#    executefunc(args.instance, args.regions)

if __name__ == "__main__":
   main(sys.argv[:])

