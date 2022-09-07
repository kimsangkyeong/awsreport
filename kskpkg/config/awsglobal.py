###################################################################################################
#
# Purpose   : define global variables. 
# Source    : awsglobal.py
# Usage     : import awsglobal
# Developer : ksk
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2019.09.15     first create
#
####################################################################################################
### This first line is for modules to work with Python 2 or 3
from __future__ import print_function
import os
import logging
import logging.config

# boto3 Log Level setting
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)


def init_logger(path):
   # module global variable 
   global klogger
   global klogger_dat

   logging.config.fileConfig(path)

   klogger     = logging.getLogger('logConsoleTypeA') # log 
   klogger_dat = logging.getLogger('datConsoleTypeC') # data

def update_logger(logtype):
   klogger  = logging.getLogger( logtype )

def update_logger_dat(logdat_type):
   klogger_dat  = logging.getLogger( logdat_type )

