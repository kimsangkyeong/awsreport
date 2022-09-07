####################################################################################################
#
# Purpose   : utilities 
# Source    : utils.py
# Usage     : python utils.py
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2022.08.21     first create
#
####################################################################################################
### This first line is for modules to work with Python 2 or 3
from __future__ import print_function
import os, sys, getopt
import json
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
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat
else:
  # Module 실행으로 상대 경로 
  from .config import awsglobal
  klogger     = awsglobal.klogger
  klogger_dat = awsglobal.klogger_dat

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

