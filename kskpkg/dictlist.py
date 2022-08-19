####################################################################################################
#
# Purpose : convert dict, list  to string 
# Source  : dictlist.py
# Usage   : python dictlist.py
# Develop : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2019.09.06     first create
#  1.1      2019.09.15     local logger assign to logger that made by main program.
#
####################################################################################################
### This first line is for modules to work with Python 2 or 3
from __future__ import print_function
import sys, getopt
import json
from config import *

### module global logger variable
global logger
global logger_dat

datalist = []

def describe_dict(spaces, contents):
  '''
    describe dict type info recursively
  '''
  ### assign external logger to module globla logger
  logger     = awsglobal.logger
  logger_dat = awsglobal.logger_dat

  try:
#    print(contents)
    for key in contents.keys():
      if isinstance(contents[key], dict):
#        logger.debug("%s%s", spaces, "type dict ->  more")
        #logger.debug("%s%s:", spaces, key)
        #print("{}{}:".format(spaces,key))
        datalist.append("{}{}:".format(spaces,key))
        describe_dict(spaces + " "*2, contents[key])
      elif isinstance(contents[key], list):
        if len(contents[key]) == 0:
          #logger.debug("%s%s:[]", spaces, key)
          #print("{}{}:".format(spaces, key))
          datalist.append("{}{}:".format(spaces, key))
        else:
#          logger.debug("%s%s", spaces, "type list ->  more")
          #logger.debug("%s%s:", spaces, key)
          #print("{}{}:".format(spaces, key))
          datalist.append("{}{}:".format(spaces, key))
          describe_list(spaces + " "*2, contents[key])
      elif isinstance(contents[key], tuple):
        #logger.debug("%s%s", spaces, "type tuple -> list more")
        describe_list(spaces + " "*2, list(contents[key]))
      elif isinstance(contents[key], set):
        #logger.debug("%s%s", spaces, "type set -> more")
        describe_list(spaces + " "*2, contents[key])
      else:
        #logger.debug("%s%s", spaces, type(contents[key]))
        #logger.debug("%s%s:%s", spaces, key, contents[key])
        #print("{}{}:{}".format(spaces, key, contents[key]))
        datalist.append("{}{}:{}".format(spaces, key, contents[key]))
    return datalist

  except Exception as othererr:
    #logger.error("describe_dict() %s", othererr)
    return False

def describe_list(spaces, contents):
  '''
    describe list type info recursively
  '''

  try:

#    print(contents)
    for content in contents:
      if isinstance(content, dict):
#        logger.debug("%s%s", spaces, "type dict -> more")
        describe_dict(spaces, content)
      elif isinstance(content, list):
#        logger.debug("%s%s", spaces, "type list -> more")
        describe_list(spaces + " "*2,content)
      elif isinstance(content, tuple):
        #logger.debug("%s%s", spaces, "type tuple -> list more")
        describe_list(spaces + " "*2, list(consent))
      elif isinstance(content, set):
#        logger.debug("%s%s", spaces, "type set -> more")
        describe_list(spces + " "*2, content)
      else:
        #logger.debug("%s%s", spaces, content)
        #logger.debug(spaces, type(content))
        #print("{}{}".format(spaces, content))
        datalist.append("{}{}".format(spaces, content))
    return datalist

  except Exception as othererr:
    #logger.error("describe_list() %s", othererr)
    return False

def main(argv):
  try:
    opts, args = getopt.getopt(argv,'a:', ["ifile=","ofile="])
  except getopt.GetoptError as err:
    print(err)
    print('')
    print('Usage : atypical json =>    python dictdsp.py -a {sentents} ')
    print('                         or echo \'{sentense}\' | python dictdsp.py')
    sys.exit(2)
  #logger.info("argv : %s %d",argv, len(argv))
  ## multi input with option string
  for opt, arg in opts:
    if opt == "-a": 
      describe_atypical_json( arg )
    else:
      describe_atypical_json( arg )
  ## multi input without option string
  for arg in args:
    if len(opts) > 0 and opt == "-a": 
      describe_atypical_json( arg )
    else:
      describe_atypical_json( arg )

  if len(argv) == 0:
    describe_atypical_json( sys.stdin.readline() )

if __name__ == "__main__":
   main(sys.argv[1:])

