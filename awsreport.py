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

def get_elbname(df, x):
  for loadbalacerarn, loadbalancername in df[['LoadBalancerArn','LoadBalancerName']].value_counts().index:
    if x == loadbalacerarn :
      return loadbalancername

def get_elbinfo(df, x):
  for listenerarn, loadbalacerarn, loadbalancername, protocol, port in df[['ListenerArn','LoadBalancerArn','LoadBalancerName', 'Protocol', 'Port']].value_counts().index:
    if x == listenerarn :
      return { loadbalancername : loadbalacerarn, protocol : port }

def get_eniname(df, x):
  for netinfid, enitname in df[['NetworkInterfaceId','ENITName']].value_counts().index:
    if x == netinfid :
      return enitname

def get_eipname(df, x):
  for allocationid, eiptname in df[['AllocationId','EIPTName']].value_counts().index:
    if x == allocationid :
      return eiptname

def get_insname(df, x):
  for instanceid, instname in df[['InstanceId','InstanceTName']].value_counts().index:
    if x == instanceid :
      return instname

def get_keyalias(df, x):
  for keyarn, keyalias in df[['KeyArn','KeyAlias']].value_counts().index:
    if x == keyarn :
      return keyalias

def get_ecsclustername(df, x):
  for clusterarn, clustername in df[['ClusterArn','ECSClusterName']].value_counts().index:
    if x == clusterarn :
      return clustername

def main(argv):
  # logger setting 
  global_config_init()

  df_cloudfront_dist = results_to_dataframe(executefunc_p1("kskpkg.cloudfront.list_distributions"))
  klogger_dat.debug(df_cloudfront_dist)

  exit(1)
  df_route53 = results_to_dataframe(executefunc_p1("kskpkg.route53.list_hosted_zones"))
  # klogger_dat.debug(df_route53)
  df_route53_record = results_to_dataframe(executefunc("kskpkg.route53.list_resource_record_sets",list(df_route53['Id'].value_counts().index)))
  # klogger_dat.debug(df_route53_record)
  df_cloudfront_oid = results_to_dataframe(executefunc_p1("kskpkg.cloudfront.list_cloud_front_origin_access_identities"))
  # klogger_dat.debug(df_cloudfront_oid)
  df_cloudmap = results_to_dataframe(executefunc_p1("kskpkg.servicediscovery.list_namespaces"))
  # klogger_dat.debug(df_cloudmap)
  df_acm = results_to_dataframe(executefunc_p1("kskpkg.acm.list_certificates"))
  # klogger_dat.debug(df_acm)
  df_vpc = results_to_dataframe(executefunc("kskpkg.ec2.describe_vpcs", ['ap-northeast-2']))
  # klogger_dat.debug(df_vpc)
  df_igw = results_to_dataframe(executefunc("kskpkg.ec2.describe_internet_gateways", ['ap-northeast-2']))
  df_igw['VpcTName'] = df_igw['AttachedVpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  # klogger_dat.debug(df_igw)
  df_subnet = results_to_dataframe(executefunc("kskpkg.ec2.describe_subnets", ['ap-northeast-2']))
  df_subnet['VpcTName'] = df_subnet['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  # klogger_dat.debug(df_subnet)
  results1, results2 = executefunc2("kskpkg.ec2.describe_route_tables", ['ap-northeast-2'])
  df_routea, df_routet = two_results_to_dataframe(results1, results2)
  df_routea['VpcTName'] = df_routea['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_routea['SubnetTName'] = df_routea['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get Subnet TagName
  df_routet['VpcTName'] = df_routet['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  # klogger_dat.debug(df_routet)
  df_eni = results_to_dataframe(executefunc("kskpkg.ec2.describe_network_interfaces", ['ap-northeast-2']))
  df_eni['VpcTName'] = df_eni['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_eni['SubnetTName'] = df_eni['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get Subnet TagName
  df_kms = results_to_dataframe(executefunc_p1("kskpkg.kms.list_keys"))
  # klogger_dat.debug(df_kms)
  df_ins = results_to_dataframe(executefunc("kskpkg.ec2.describe_instances", ['ap-northeast-2']))
  df_ins['VpcTName'] = df_ins['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_ins['SubnetTName'] = df_ins['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get Subnet TagName
  df_ins['ENITName'] = df_ins['NetworkInterfaceId'].apply(lambda x : get_eniname(df_eni,x)) # get ENI TagName
  # klogger_dat.debug(df_ins)
  df_mplist = results_to_dataframe(executefunc("kskpkg.ec2.describe_prefix_lists", ['ap-northeast-2']))
  # klogger_dat.debug(df_mplist)
  df_sg = results_to_dataframe(executefunc("kskpkg.ec2.describe_security_groups", ['ap-northeast-2']))
  df_sg['VpcTName'] = df_sg['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_sg['In_GroupName'] = df_sg['In_GroupId'].apply(lambda x : get_sgname(df_sg,x)) # get Security Group TagName
  df_sg['Out_GroupName'] = df_sg['Out_GroupId'].apply(lambda x : get_sgname(df_sg,x)) # get Security Group TagName
  # klogger_dat.debug(df_sg)
  # 상호 참조관계의 instanse와 eni는 일부 항목만 순서 조정하여 셋팅 ( 먼저 ec2 <- eni tag 치환 후 eni <- ec2 tag 치환)
  df_eni['Attach_InstanceTName'] = df_eni['Attach_InstanceID'].apply(lambda x : get_insname(df_ins,x)) # get Instance TagName
  # klogger_dat.debug(df_eni)
  # display.display(df_eni)
  df_eip = results_to_dataframe(executefunc("kskpkg.ec2.describe_addresses", ['ap-northeast-2']))
  df_eip['ENITName'] = df_eip['NetworkInterfaceId'].apply(lambda x : get_eniname(df_eni,x)) # get ENI TagName
  df_eip['InstanceTName'] = df_eip['InstanceId'].apply(lambda x : get_insname(df_ins,x)) # get Instance TagName
  # klogger_dat.debug(df_eip)
  df_nat = results_to_dataframe(executefunc("kskpkg.ec2.describe_nat_gateways", ['ap-northeast-2']))
  df_nat['VpcTName'] = df_nat['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_nat['SubnetTName'] = df_nat['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get Subnet TagName
  df_nat['EIPTName'] = df_nat['AllocationId'].apply(lambda x : get_eipname(df_eip,x)) # get EIP TagName
  df_nat['ENITName'] = df_nat['NetworkInterfaceId'].apply(lambda x : get_eniname(df_eni,x)) # get ENI TagName
  # klogger_dat.debug(df_nat)
  df_elb = results_to_dataframe(executefunc_p1("kskpkg.elb.describe_load_balancers"))
  df_elb['VpcTName'] = df_elb['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_elb['SubnetTName'] = df_elb['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get Subnet TagName
  df_elb['SecurityGroupName'] = df_elb['SecurityGroupId'].apply(lambda x : get_sgname(df_sg,x)) # get Security Group TagName
  # klogger_dat.debug(df_elb)
  df_elb_listener = results_to_dataframe(executefunc("kskpkg.elb.describe_listeners", list(df_elb['LoadBalancerArn'].value_counts().index)))
  df_elb_listener['LoadBalancerName'] = df_elb_listener['LoadBalancerArn'].apply(lambda x : get_elbname(df_elb,x)) # get ELB Name
  # klogger_dat.debug(df_elb_listener)
  df_elb_listener_rule = results_to_dataframe(executefunc("kskpkg.elb.describe_rules", list(df_elb_listener['ListenerArn'].value_counts().index)))
  df_elb_listener_rule['LoadBalancerInfo'] = df_elb_listener_rule['ListenerArn'].apply(lambda x : get_elbinfo(df_elb_listener,x)) # get ELB Info
  # klogger_dat.debug(df_elb_listener_rule)
  df_elb_targetgroup = results_to_dataframe(executefunc("kskpkg.elb.describe_target_groups", list(df_elb['LoadBalancerArn'].value_counts().index)))
  df_elb_targetgroup['VpcTName'] = df_elb_targetgroup['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_elb_targetgroup['LoadBalancerName'] = df_elb_targetgroup['LoadBalancerArn'].apply(lambda x : get_elbname(df_elb,x)) # get ELB Name
  # klogger_dat.debug(df_elb_targetgroup)
  df_ekscluster = results_to_dataframe(executefunc_p1("kskpkg.eks.list_clusters"))
  df_ekscluster['VpcTName'] = df_ekscluster['VpcId'].apply(lambda x : get_vpcname(df_vpc,x)) # get VpcTagName
  df_ekscluster['SubnetTName'] = df_ekscluster['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get Subnet TagName
  df_ekscluster['SecurityGroupName'] = df_ekscluster['SecurityGroup'].apply(lambda x : get_sgname(df_sg,x)) # get Security Group TagName
  df_ekscluster['ClusterSecurityGroupName'] = df_ekscluster['ClusterSecurityGroupId'].apply(lambda x : get_sgname(df_sg,x)) # get Security Group TagName
  df_ekscluster['EncryptKeyAlias'] = df_ekscluster['EncryptKeyArn'].apply(lambda x : get_keyalias(df_kms,x)) # get KMS Key alias
  # klogger_dat.debug(df_ekscluster)
  df_ecscluster = results_to_dataframe(executefunc_p1("kskpkg.ecs.list_clusters"))
  # klogger_dat.debug(df_ecscluster)
  df_ecs_service = results_to_dataframe(executefunc("kskpkg.ecs.list_services", list(df_ecscluster['ClusterArn'].value_counts().index)))
  df_ecs_service['ECSClusterName'] = df_ecs_service['ClusterArn'].apply(lambda x : get_ecsclustername(df_ecscluster,x)) # get Subnet TagName
  df_ecs_service['SubnetTName'] = df_ecs_service['SubnetId'].apply(lambda x : get_subnetname(df_subnet,x)) # get Subnet TagName
  df_ecs_service['SecurityGroupName'] = df_ecs_service['SecurityGroup'].apply(lambda x : get_sgname(df_sg,x)) # get Security Group TagName
  # klogger_dat.debug(df_ecs_service)
  df_s3 = results_to_dataframe(executefunc_p1("kskpkg.s3.list_buckets"))
  df_s3['KMSMasterKeyAlias'] = df_s3['KMSMasterKeyID'].apply(lambda x : get_keyalias(df_kms,x)) # get KMS Key alias
  # klogger_dat.debug(df_s3)
  df_efs = results_to_dataframe(executefunc_p1("kskpkg.efs.describe_file_systems"))
  df_efs['KmsKeyAlias'] = df_efs['KmsKeyId'].apply(lambda x : get_keyalias(df_kms,x)) # get KMS Key alias
  # klogger_dat.debug(df_efs)
  df_ecr = results_to_dataframe(executefunc_p1("kskpkg.ecr.describe_repositories"))
  df_ecr['KmsKeyAlias'] = df_ecr['KmsKeyId'].apply(lambda x : get_keyalias(df_kms,x)) # get KMS Key alias
  # klogger_dat.debug(df_ecr)
  df_rdscluser = results_to_dataframe(executefunc_p1("kskpkg.rds.describe_db_clusters"))
  df_rdscluser['KmsKeyAlias'] = df_rdscluser['KmsKeyId'].apply(lambda x : get_keyalias(df_kms,x)) # get KMS Key alias
  df_rdscluser['ActivityStreamKmsKeyAlias'] = df_rdscluser['ActivityStreamKmsKeyId'].apply(lambda x : get_keyalias(df_kms,x)) # get KMS Key alias
  df_rdscluser['PerformanceInsightsKMSKeyAlias'] = df_rdscluser['PerformanceInsightsKMSKeyId'].apply(lambda x : get_keyalias(df_kms,x)) # get KMS Key alias
  df_rdscluser['VpcSecurityGroupName'] = df_rdscluser['VpcSecurityGroupId'].apply(lambda x : get_sgname(df_sg,x)) # get Security Group TagName
  # klogger_dat.debug(df_rdscluser)

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
      df_eip.to_excel(writer, sheet_name='eip', index=False) 
      df_subnet.to_excel(writer, sheet_name='subnet', index=False) 
      df_routea.to_excel(writer, sheet_name='router', index=False) 
      df_routet.to_excel(writer, sheet_name='routeinfo', index=False) 
      df_mplist.to_excel(writer, sheet_name='managed_prefixlist', index=False) 
      df_elb.to_excel(writer, sheet_name='elb', index=False) 
      df_elb_listener.to_excel(writer, sheet_name='elb_listener', index=False) 
      df_elb_listener_rule.to_excel(writer, sheet_name='elb_listener_rule', index=False) 
      df_elb_targetgroup.to_excel(writer, sheet_name='elb_targetgroup', index=False) 
      df_ekscluster.to_excel(writer, sheet_name='eks', index=False) 
      df_ecscluster.to_excel(writer, sheet_name='ecs', index=False) 
      df_ecs_service.to_excel(writer, sheet_name='ecs-service', index=False) 
      df_ins.to_excel(writer, sheet_name='instance', index=False) 
      df_sg.to_excel(writer, sheet_name='securegroup', index=False) 
      df_eni.to_excel(writer, sheet_name='eni', index=False) 
      df_efs.to_excel(writer, sheet_name='efs', index=False) 
      df_s3.to_excel(writer, sheet_name='s3', index=False) 
      df_ecr.to_excel(writer, sheet_name='ecr', index=False) 
      df_kms.to_excel(writer, sheet_name='kms', index=False) 
      df_rdscluser.to_excel(writer, sheet_name='rds', index=False) 
  else:
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
      df_route53.to_excel(writer, sheet_name='route53', index=False)
      df_route53_record.to_excel(writer, sheet_name='route53_record', index=False) 
      df_cloudmap.to_excel(writer, sheet_name='cloudmap', index=False) 
      df_acm.to_excel(writer, sheet_name='acm', index=False)
      df_vpc.to_excel(writer, sheet_name='vpc', index=False)
      df_igw.to_excel(writer, sheet_name='igw', index=False) 
      df_nat.to_excel(writer, sheet_name='nat', index=False) 
      df_eip.to_excel(writer, sheet_name='eip', index=False) 
      df_subnet.to_excel(writer, sheet_name='subnet', index=False) 
      df_routea.to_excel(writer, sheet_name='router', index=False) 
      df_routet.to_excel(writer, sheet_name='routeinfo', index=False) 
      df_mplist.to_excel(writer, sheet_name='managed_prefixlist', index=False) 
      df_elb.to_excel(writer, sheet_name='elb', index=False) 
      df_elb_listener.to_excel(writer, sheet_name='elb_listener', index=False) 
      df_elb_listener_rule.to_excel(writer, sheet_name='elb_listener_rule', index=False) 
      df_elb_targetgroup.to_excel(writer, sheet_name='elb_targetgroup', index=False) 
      df_ekscluster.to_excel(writer, sheet_name='eks', index=False) 
      df_ecscluster.to_excel(writer, sheet_name='ecs', index=False) 
      df_ecs_service.to_excel(writer, sheet_name='ecs-service', index=False) 
      df_ins.to_excel(writer, sheet_name='instance', index=False) 
      df_sg.to_excel(writer, sheet_name='securegroup', index=False) 
      df_eni.to_excel(writer, sheet_name='eni', index=False) 
      df_efs.to_excel(writer, sheet_name='efs', index=False) 
      df_s3.to_excel(writer, sheet_name='s3', index=False) 
      df_ecr.to_excel(writer, sheet_name='ecr', index=False) 
      df_kms.to_excel(writer, sheet_name='kms', index=False) 
      df_rdscluser.to_excel(writer, sheet_name='rds', index=False) 
  klogger_dat.debug("finished")

if __name__ == "__main__":
   main(sys.argv[:])

