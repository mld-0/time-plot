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
from dtscan.dtscan import DTScanner

_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class PlotDassResults(object):
    default_color_options = [ 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple', 'tab:red'  ]
    plot_save_dir = os.path.join(tempfile.gettempdir(), "PlotDecayQtys")

    _data_path_dir = None
    _data_fname_prefix = None
    _data_fname_postfix = None

    def __init__(self):
        pass

    def PlotDassScores_ForDateRange(self, arg_dt_start, arg_dt_end):
        pass

    def _ReadDassData_ForDateRange(self, arg_dt_start=None, arg_dt_end=None):
        """Get list of dass data, and plot values between datetime range, or all values if dt start/end are None"""
        dass_data = []
        files_list = TimePlotUtils._GetAvailableFiles_FromMonthlyRange_WithFullTime(self._data_path_dir, self._data_fname_prefix, self._data_fname_postfix)
        #   Continue: 2021-01-25T00:57:06AEDT plot DAS dictionary vs datetimes for dt_start/end given

    def _ReadDassData_All(self):
        dass_data = []
        files_list = TimePlotUtils._GetAvailableFiles_FromMonthlyRange_WithFullTime(self._data_path_dir, self._data_fname_prefix, self._data_fname_postfix)
        for loop_path in files_list:
            loop_data = self._ReadDassScoresFromFile(loop_path)
            _log.debug("loop_data=(%s)" % str(loop_data))

    def _ReadDassData_GetFirstAndLastDateInDir(self):
        files_list = TimePlotUtils._GetAvailableFiles_FromMonthlyRange_WithFullTime(self._data_path_dir, self._data_fname_prefix, self._data_fname_postfix)
        first_fname = os.path.basename(files_list[0])
        last_fname = os.path.basename(files_list[-1])
        first_datetime = self._FilePath2Datetime(first_fname)
        last_datetime = self._FilePath2Datetime(last_fname)
        _log.debug("first_datetime=(%s)" % str(first_datetime))
        _log.debug("last_datetime=(%s)" % str(last_datetime))
        return [ first_datetime, last_datetime ]

    def _FilePath2Datetime(self, arg_filepath):
        _fname = os.path.basename(arg_filepath)
        _datetime_str = _fname.replace(self._data_fname_prefix, "")
        _datetime_str = _datetime_str.replace(self._data_fname_postfix, "")[::-1]
        _datetime_str = _datetime_str.replace("-", ":", 1)
        _datetime_str = _datetime_str.replace("-", "T", 1)
        _datetime_str = _datetime_str[0:4] + ":" + _datetime_str[5:]
        _datetime_str = _datetime_str[::-1]
        _datetime = dateparser.parse(_datetime_str)

        return _datetime
        

    def _ReadDassScoresFromFile(self, path_dass):
        #   TODO: 2021-01-25T00:39:16AEDT Handle 'file is not encrypted' case
        dass_file_str = TimePlotUtils._GPGDecryptFileToString(path_dass)
        #_log.debug("dass_file_str=(%s)" % str(dass_file_str))
        dass_file_datetime = self._FilePath2Datetime(dass_file_str.split('\n')[0])
        dass_file_linetwo = dass_file_str.split('\n')[1]
        dass_results_dict = eval(dass_file_linetwo)
        #_log.debug("dass_file_datetime=(%s)" % str(dass_file_datetime))
        #_log.debug("dass_results_dict=(%s)" % str(dass_results_dict))
        return [ dass_file_datetime, dass_results_dict ]


#   }}}1

