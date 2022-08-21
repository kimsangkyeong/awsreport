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
# required install package : # pip install numpy, pandas, openpyxl
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
from datetime import date
import IPython.display as display # pip install ipython

# 현재 디렉토리
path_cwd = os.getcwd()
# OS 판단  : win32, linux, cygwin, darwin, aix
my_os = sys.platform
#print(my_os)
if my_os == "linux":
  path_logconf = path_cwd + '/kskpkg/config/logging.conf'
  output_file = f'{path_cwd}/output_{date.today().strftime("%Y%m%d")}.xlsx'
else:
  path_logconf = path_cwd + '\kskpkg\config\logging.conf'
  output_file = f'{path_cwd}\output_{date.today().strftime("%Y%m%d")}.xlsx'

pd.set_option("display.max_colwidth", 999)  # 컬럼 정보 보여주기
pd.set_option("display.max_rows", 150)  # row 정보 보여주기

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

# dynamic module load and call function : parameter one
def executefunc_p1(objstr):
  '''
     execute function from reserved function string
  '''
  try:
    objlist = getobjectstring(objstr)
    objmodule = importlib.import_module(objlist[0])
    objfunction = getattr(objmodule, objlist[1]) 

    # dynamic function call
    results = objfunction()
    return results

  except Exception as othererr:
    print("executefunc() %s" % othererr)
    return False

# dynamic module load and call function : return one
def executefunc(objstr, param):
  '''
     execute function from reserved function string
  '''
  try:
    objlist = getobjectstring(objstr)
    objmodule = importlib.import_module(objlist[0])
    objfunction = getattr(objmodule, objlist[1]) 

    # dynamic function call
    results = objfunction(param)
    return results

  except Exception as othererr:
    print("executefunc() %s" % othererr)
    return False

# boto3 results to dataframe
def results_to_dataframe(results):
  # klogger.debug(results)
  df = pd.DataFrame()
  for result in results:
    df_tmp = pd.DataFrame(result)
    df = pd.concat([df, df_tmp], ignore_index=True)
  # klogger.debug(df.values)
  return df

# dynamic module load and call function : return two
def executefunc2(objstr, param):
  '''
     execute function from reserved function string
  '''
  try:
    objlist = getobjectstring(objstr)
    objmodule = importlib.import_module(objlist[0])
    objfunction = getattr(objmodule, objlist[1]) 

    # dynamic function call
    results1, results2 = objfunction(param)
    return results1, results2

  except Exception as othererr:
    print("executefunc() %s" % othererr)
    return False

# boto3 results to dataframe
def two_results_to_dataframe(results1, results2):
  df1 = pd.DataFrame()
  for result in results1:
    df_tmp = pd.DataFrame(result)
    df1 = pd.concat([df1, df_tmp], ignore_index=True)
  # klogger.debug(df1.values)
  df2 = pd.DataFrame()
  for result in results2:
    df_tmp = pd.DataFrame(result)
    df2 = pd.concat([df2, df_tmp], ignore_index=True)
  # klogger.debug(df2.values)
  return df1, df2

def get_vpcname(df, x):
  for vpcid, vpctname in df[['VpcId','VpcTName']].value_counts().index:
    if x == vpcid:
      return vpctname

def get_subnetname(df, x):
  for subnetid, subnettname in df[['SubnetId','SubnetTName']].value_counts().index:
    if x == subnetid:
      return subnettname

def get_sgname(df, x, tagname=False):
  if tagname :
    for sgid, sgname in df[['SGroupId','SGroupTName']].value_counts().index:
      if x == sgid:
        return sgname
  else:
    for sgid, sgname in df[['SGroupId','SGroupName']].value_counts().index:
      if x == sgid:
        return sgname

def main(argv):
  # logger setting 
  global_config_init()

  df_route53 = results_to_dataframe(executefunc_p1("kskpkg.route53.list_hosted_zones"))
  # klogger_dat.debug(df_route53)
  df_route53_record = results_to_dataframe(executefunc("kskpkg.route53.list_resource_record_sets",list(df_route53['Id'])))
  # klogger_dat.debug(df_route53_record)
  df_cloudmap = results_to_dataframe(executefunc_p1("kskpkg.servicediscovery.list_namespaces"))
  # klogger_dat.debug(df_cloudmap)
  df_acm = results_to_dataframe(executefunc_p1("kskpkg.acm.list_certificates"))
  # klogger_dat.debug(df_acm)
  df_vpc = results_to_dataframe(executefunc("kskpkg.ec2.describe_vpcs", ['ap-northeast-2']))
  df_igw = results_to_dataframe(executefunc("kskpkg.ec2.describe_internet_gateways", ['ap-northeast-2']))
  df_igw['VpcTName'] = df_igw['AttachedVpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  # klogger_dat.debug(df_igw)
  df_subnet = results_to_dataframe(executefunc("kskpkg.ec2.describe_subnets", ['ap-northeast-2']))
  df_subnet['VpcTName'] = df_subnet['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  # klogger_dat.debug(df_subnet)
  df_nat = results_to_dataframe(executefunc("kskpkg.ec2.describe_nat_gateways", ['ap-northeast-2']))
  df_nat['VpcTName'] = df_nat['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_nat['SubnetTName'] = df_nat['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get VpcTagName
  # klogger_dat.debug(df_nat)
  results1, results2 = executefunc2("kskpkg.ec2.describe_route_tables", ['ap-northeast-2'])
  df_routea, df_routet = two_results_to_dataframe(results1, results2)
  df_routea['VpcTName'] = df_routea['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_routea['SubnetTName'] = df_routea['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get VpcTagName
  df_routet['VpcTName'] = df_routet['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  # klogger_dat.debug(df_routet)
  df_ins = results_to_dataframe(executefunc("kskpkg.ec2.describe_instances", ['ap-northeast-2']))
  df_ins['VpcTName'] = df_ins['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_ins['SubnetTName'] = df_ins['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get VpcTagName
  # klogger_dat.debug(df_ins)
  df_sg = results_to_dataframe(executefunc("kskpkg.ec2.describe_security_groups", ['ap-northeast-2']))
  df_sg['VpcTName'] = df_sg['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_sg['In_GroupName'] = df_sg['In_GroupId'].apply(lambda x : get_sgname(df_sg,x)) # get VpcTagName
  df_sg['Out_GroupName'] = df_sg['Out_GroupId'].apply(lambda x : get_sgname(df_sg,x)) # get VpcTagName
  # klogger_dat.debug(df_sg)
  df_eni = results_to_dataframe(executefunc("kskpkg.ec2.describe_network_interfaces", ['ap-northeast-2']))
  df_eni['VpcTName'] = df_eni['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_eni['SubnetTName'] = df_eni['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get VpcTagName
  # klogger_dat.debug(df_eni)
  # display.display(df_eni)
  df_elb = results_to_dataframe(executefunc_p1("kskpkg.elb.describe_load_balancers"))
  df_elb['VpcTName'] = df_elb['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_elb['SubnetTName'] = df_elb['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get VpcTagName
  df_elb['SecurityGroupName'] = df_elb['SecurityGroupId'].apply(lambda x : get_sgname(df_sg,x)) # get VpcTagName
  # klogger_dat.debug(df_elb)
  df_s3 = results_to_dataframe(executefunc_p1("kskpkg.s3.list_buckets"))
  # klogger_dat.debug(df_s3)

  # to_excel 
  klogger_dat.debug("%s\n%s","-"*20,"save to excel")
  if os.path.exists(output_file):
    with pd.ExcelWriter(output_file, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
      df_route53.to_excel(writer, sheet_name='route53', index=False) 
      df_route53_record.to_excel(writer, sheet_name='route53_record', index=False) 
      df_cloudmap.to_excel(writer, sheet_name='cloudmap', index=False) 
      df_acm.to_excel(writer, sheet_name='acm', index=False)
      df_vpc.to_excel(writer, sheet_name='vpc', index=False)
      df_igw.to_excel(writer, sheet_name='igw', index=False) 
      df_nat.to_excel(writer, sheet_name='nat', index=False) 
      df_subnet.to_excel(writer, sheet_name='subnet', index=False) 
      df_routea.to_excel(writer, sheet_name='router', index=False) 
      df_routet.to_excel(writer, sheet_name='routeinfo', index=False) 
      df_elb.to_excel(writer, sheet_name='elb', index=False) 
      df_ins.to_excel(writer, sheet_name='instance', index=False) 
      df_sg.to_excel(writer, sheet_name='securegroup', index=False) 
      df_eni.to_excel(writer, sheet_name='eni', index=False) 
      df_s3.to_excel(writer, sheet_name='s3', index=False) 
  else:
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
      df_route53.to_excel(writer, sheet_name='route53', index=False)
      df_route53_record.to_excel(writer, sheet_name='route53_record', index=False) 
      df_cloudmap.to_excel(writer, sheet_name='cloudmap', index=False) 
      df_acm.to_excel(writer, sheet_name='acm', index=False)
      df_vpc.to_excel(writer, sheet_name='vpc', index=False)
      df_igw.to_excel(writer, sheet_name='igw', index=False) 
      df_nat.to_excel(writer, sheet_name='nat', index=False) 
      df_subnet.to_excel(writer, sheet_name='subnet', index=False) 
      df_routea.to_excel(writer, sheet_name='router', index=False) 
      df_routet.to_excel(writer, sheet_name='routeinfo', index=False) 
      df_elb.to_excel(writer, sheet_name='elb', index=False) 
      df_ins.to_excel(writer, sheet_name='instance', index=False) 
      df_sg.to_excel(writer, sheet_name='securegroup', index=False) 
      df_eni.to_excel(writer, sheet_name='eni', index=False) 
      df_s3.to_excel(writer, sheet_name='s3', index=False) 
  klogger_dat.debug("finished")

if __name__ == "__main__":
   main(sys.argv[:])

