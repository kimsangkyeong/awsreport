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

# dynamic module load and call function
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

# boto3 results to dataframe
def results_to_dataframe(results):
  df = pd.DataFrame()
  for result in results:
    df_tmp = pd.DataFrame(result)
    df = pd.concat([df, df_tmp], ignore_index=True)
  #klogger.debug(df.values)
  return df

def get_vpcname(df, x):
  for vpcid, vpctname in df[['VpcId','VpcTName']].value_counts().index:
    if x == vpcid:
      return vpctname

def main(argv):
  # logger setting 
  global_config_init()

  df_vpc = results_to_dataframe(executefunc("kskpkg.ec2.describe_vpcs", ['ap-northeast-2']))
  # df_igw = results_to_dataframe(executefunc("kskpkg.ec2.describe_internet_gateways", ['ap-northeast-2']))
  # df_igw['VpcTName'] = df_igw['AttachedVpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  # klogger_dat.debug(df_igw)
  df_nat = results_to_dataframe(executefunc("kskpkg.ec2.describe_nat_gateways", ['ap-northeast-2']))
  df_nat['VpcTName'] = df_nat['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  klogger_dat.debug(df_nat)
  df_ins = results_to_dataframe(executefunc("kskpkg.ec2.describe_instances", ['ap-northeast-2']))
  df_ins['VpcTName'] = df_ins['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  # klogger_dat.debug(df_ins)

  # to_excel 
  if os.path.exists(output_file):
    with pd.ExcelWriter(output_file, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
      df_igw.to_excel(writer, sheet_name='igw', index=False) 
      df_vpc.to_excel(writer, sheet_name='vpc', index=False) # pip install openpyxl
      df_ins.to_excel(writer, sheet_name='instance', index=False) 
  else:
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
      df_igw.to_excel(writer, sheet_name='igw', index=False) 
      df_vpc.to_excel(writer, sheet_name='vpc', index=False)
      df_ins.to_excel(writer, sheet_name='instance', index=False) 

if __name__ == "__main__":
   main(sys.argv[:])

