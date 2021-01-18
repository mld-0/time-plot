#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   Imports:
#   {{{3
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

_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class PlotDecayQtys(object):
    default_color_options = [ 'tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple' ]

    data_file_dir = None
    data_file_prefix = None
    data_file_postfix = None

    data_labels = []
    data_halflives = []
    data_onsets = []

    data_column_dt = None
    data_column_qty = None
    data_column_label = None
    data_delim = ","

    flag_restrictFuture = True

    #def _ReadData(self, arg_files_list, arg_label, self.data_column_dt, self.data_column_qty, self.data_column_label, self.data_delim):
    def _ReadData(self, arg_files_list, arg_label):
    #   {{{
        """Given a list of files, get as a list qtys and datetimes (from columns self.data_column_qty and self.data_column_dt), for lines where value in column self.data_column_label==arg_label (if arg_label is not None, otherwise read every line). Return [ results_dt, results_qty ] lists, sorted chronologicaly"""
        #   validate data_column_dt, data_column_qty, data_column_label
        #   {{{
        if (not isinstance(self.data_column_dt, int)) or (not isinstance(self.data_column_qty, int)) or (not isinstance(self.data_column_label, int)):
            raise Exception("Must set int values for data_column_dt=(%s), data_column_qty=(%s), data_column_label=(%s)" % (str(self.data_column_dt), str(self.data_column_qty), str(self.data_column_label)))
        #   }}}
        _log.debug("arg_label=(%s)" % str(arg_label))
        _log.debug("cols: (dt, qty, label)=(%s, %s, %s), delim=(%s)" % (self.data_column_dt, self.data_column_qty, self.data_column_label, self.data_delim))
        results_dt = []
        results_qty = []
        for loop_filepath in arg_files_list:
            loop_filestr = TimePlotUtils._GPGDecryptFileToString(loop_filepath)
            for loop_line in loop_filestr.split("\n"):
                loop_line_split = loop_line.split(self.data_delim)
                if not (len(loop_line_split) <= 1):
                    #_log.debug("loop_line_split=(%s)" % str(loop_line_split))
                    if (arg_label is None) or (loop_line_split[self.data_column_label] == arg_label):
                        loop_qty = None
                        if (self.data_column_qty is not None):
                            loop_qty_str = loop_line_split[self.data_column_qty]
                            loop_qty = Decimal(loop_qty_str)
                        loop_dt_str = loop_line_split[self.data_column_dt]
                        loop_dt_str = TimePlotUtils._Fix_DatetimeStr(loop_dt_str)
                        #   Attempt parsing with datetime.datetime.strptime() first, on account of slowness of dateparser.parse
                        loop_dt = None
                        if (loop_dt is None):
                            try:
                                loop_dt = datetime.datetime.strptime(loop_dt_str, "%Y-%m-%dT%H:%M:%S%Z")
                            except Exception as e:
                                loop_dt = None
                        if (loop_dt is None):
                            try:
                                loop_dt = datetime.datetime.strptime(loop_dt_str, "%Y-%m-%dT%H:%M:%S")
                            except Exception as e:
                                loop_dt = None
                        if (loop_dt is None):
                            loop_dt = dateparser.parse(loop_dt_str)
                        if (loop_dt is None):
                            raise Exception("Failed to parse loop_dt_str=(%s)" % str(loop_dt_str))
                        results_dt.append(loop_dt)
                        results_qty.append(loop_qty)
        if (len(results_dt) != len(results_qty)):
            raise Exception("mismatch, len(results_dt)=(%s), len(results_qty)=(%s)" % (str(len(results_dt)), str(len(results_qty))))
        _log.debug("len(results)=(%s)" % str(len(results_dt)))
        return [ results_dt, results_qty ]
    #   }}}

    #def _GetMonthRange(self, arg_dt_first, arg_dt_last, arg_includeMonthBefore=False, arg_result_str=True):
    ##   {{{
    #    """Get list of months between two dates, as either strings or datetimes. Optionally include month before first date."""
    #    if (isinstance(arg_dt_first, str)):
    #        arg_dt_first = dateparser.parse(arg_dt_first)
    #    if (isinstance(arg_dt_last, str)):
    #        arg_dt_last = dateparser.parse(arg_dt_last)
    #    arg_dt_first = arg_dt_first.replace(day=1)
    #    arg_dt_last = arg_dt_last.replace(day=1)
    #    if (arg_dt_first > arg_dt_last):
    #        raise Exception("Invalid arg_dt_first=(%s) > arg_dt_last=(%s)" % (str(arg_dt_first), str(arg_dt_last)))
    #    _dt_format_convertrange = '%Y-%m-%dT%H:%M:%S%Z'
    #    _dt_format_output = '%Y-%m'
    #    _dt_freq = 'MS'
    #    _log.debug("arg_includeMonthBefore=(%s)" % str(arg_includeMonthBefore))
    #    if (arg_includeMonthBefore):
    #        arg_dt_beforeFirst = arg_dt_first + relativedelta(months = -1)
    #        arg_dt_beforeFirst = arg_dt_beforeFirst.replace(day=1)
    #        arg_dt_first = arg_dt_beforeFirst
    #    _log.debug("arg_dt_first=(%s)" % str(arg_dt_first))
    #    _log.debug("arg_dt_last=(%s)" % str(arg_dt_last))
    #    dt_Range = [ x for x in pandas.date_range(start=arg_dt_beforeFirst.strftime(_dt_format_convertrange), end=arg_dt_last.strftime(_dt_format_convertrange), freq=_dt_freq) ]
    #    if (arg_result_str):
    #        dt_Range_str = [ x.strftime(_dt_format_output) for x in dt_Range ]
    #        _log.debug("dt_Range_str=(%s)" % str(dt_Range_str))
    #        return dt_Range_str
    #    else:
    #        _log.debug("dt_Range=(%s)" % str(dt_Range))
    #        return dt_Range
    ##   }}}

#   }}}1

