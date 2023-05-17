####################################################################################################
#
# Purpose   : utilities 
# Source    : utils.py
# Usage     : python utils.py
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.21     first create
#  1.1      2023.05.17     add session handling logic
#
####################################################################################################
### This first line is for modules to work with Python 2 or 3
from __future__ import print_function
import os, sys, getopt
import json
import logging
import boto3



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
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
  profile_flag = awsglobal.profile_flag
  profile      = awsglobal.profile
  region      = awsglobal.region
else:
  # Module 실행으로 상대 경로 
  from .config import awsglobal
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
  profile_flag = awsglobal.profile_flag
  profile      = awsglobal.profile
  region      = awsglobal.region

def ListSyncCountWithSpace(*lists):
  '''
    input list max count로 space 추가하여 동기화
  '''
  try:
    # klogger_dat.debug('utils.ListSyncCountWithSpace')
    max_len = 1
    for list in lists:
      max_len = max(max_len, len(list))
    #   klogger_dat.debug("max_len : %d, len : %d, %s", max_len, len(list), list)
    for list in lists:
      for ix in range(len(list), max_len):
        list.append(' ')

    return True
  except Exception as othererr:
    klogger.error("utils.ListSyncCountWithSpace(),%s", othererr)
  finally:
    return False

# AWS Session
def get_session(AWSService, func_region=None):
  '''
    AWS Configure Profile 이름을 참고하여 Session 생성하기
  '''
  if profile_flag :
    try:
      if func_region != None :  # 함수에서 리전 정보를 입력값으로 하여 처리하고자 하는 경우. 기동 시 입력 parameter 보다 우선처리
        session = boto3.Session(profile_name=profile, region_name=func_region)
      else :
        session = boto3.Session(profile_name=profile, region_name=region)
      return session.client(AWSService)
    except Exception as othererr:
      print("get_session() %s" % othererr)
      return None
  else :
    if func_region != None :  # 함수에서 리전 정보를 입력값으로 하여 처리하고자 하는 경우
      return boto3.client(AWSService, region_name=func_region)
    else :
      return boto3.client(AWSService)

# AWS Session resource
def get_session_resource(AWSService, func_region=None):
  '''
    AWS Configure Profile 이름을 참고하여 Session 생성하기
  '''
  if profile_flag :
    try:
      if func_region != None :  # 함수에서 리전 정보를 입력값으로 하여 처리하고자 하는 경우. 기동 시 입력 parameter 보다 우선처리
        session = boto3.Session(profile_name=profile, region_name=func_region)
      else :
        session = boto3.Session(profile_name=profile, region_name=region)
      return session.resource(AWSService)
    except Exception as othererr:
      print("get_session() %s" % othererr)
      return None
  else :
    if func_region != None :  # 함수에서 리전 정보를 입력값으로 하여 처리하고자 하는 경우
      return boto3.resource(AWSService, region_name=func_region)
    else :
      return boto3.resource(AWSService)

def main(argv):

  a = ['1', '2']
  b = ['a']
  c = ['']
  d = ['b', 'c', 'd', 'e']
  f = ['10', '20']
  klogger_dat.debug("before : %s,%s,%s,%s,%s", a, b, c,d,f)
  ListSyncCountWithSpace(a,b,c,d,f) 
  klogger_dat.debug("After : %s,%s,%s,%s,%s", a, b, c,d,f)
  
  sys.exit(0)

if __name__ == "__main__":
  main(sys.argv[1:])

