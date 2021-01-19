#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   Imports:
#   {{{3
import tempfile
import calendar
import argparse
import io
import sys
import importlib
import importlib.resources
import time
import glob
import re
import pprint
import logging
import os
import datetime
import pandas
import dateparser
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE, STDOUT
from io import StringIO
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from matplotlib.dates import DateFormatter
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
#   }}}1
#   {{{2
#from timeplot.util import _GPGEncryptString2ByteArray, _GPGDecryptFileToString, _Fix_DatetimeStr, _GetFiles_FromMonthlyRange
from timeplot.util import TimePlotUtils
from timeplot.decaycalc import DecayCalc

_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class PlotTimestamps(object):
    default_color_options = [ 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple', 'tab:red'  ]

    plot_save_dir = os.path.join(tempfile.gettempdir(), "PlotDecayQtys")

    data_file_path = None

    _data_labels = []
    
    data_column_label = None
    data_column_dt = None
    data_delim = ","

    def __init__(self):
        pass

    def PlotDaily_TimestampSplits_ForDateRange(self, arg_date_start, arg_date_end, arg_restrictFuture=True):
        pass

    def PlotDaily_TimestampSplits(self, loop_day, intervals_list):
        pass

    def _ReadTimestampsSplits(self, path_log, arg_label):
        pass

#   }}}1

