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

class PlotTimestamps(object):
    default_color_options = [ 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple', 'tab:red'  ]
    decaycalc = DecayCalc()
    dtscanner = DTScanner()

    plot_save_dir = os.path.join(tempfile.gettempdir(), "PlotDecayQtys")

    #data_file_path = None

    def __init__(self):
        pass

    def PlotDaily_TimestampSplits_ForDateRange(self, path_log, arg_date_start, arg_date_end, arg_split, arg_restrictFuture=True):
    #   {{{
        _log.debug("arg_date_start=(%s), arg_date_end=(%s)" % (str(arg_date_start), str(arg_date_end)))
        range_calendar_list = TimePlotUtils.CalendarRange_Monthly_DateRangeFromFirstAndLast(arg_date_start, arg_date_end)
        range_months_list = TimePlotUtils.MonthlyDateRange_FromFirstAndLast(arg_date_start, arg_date_end)
        _now = datetime.datetime.now()
        if (len(range_calendar_list) != len(range_months_list)):
            raise Exception("(len(range_calendar_list)=(%s) != len(range_months_list))=(%s)" % (len(range_calendar_list), len(range_months_list)))
        for loop_month, loop_days_list in zip(range_months_list, range_calendar_list):
            intervals_list = self._ReadTimestampsSplits(path_log, arg_date_start, arg_date_end, arg_split)
            for loop_day in loop_days_list:
                loop_mins_x, loop_y = self._FillMinuteRangeForDayFromSplits(intervals_list, loop_day)
                #_log.debug("loop_y=(%s)" % str(loop_y))
                try:
                    self._PlotTimestampMinuteRangeForDay(loop_mins_x, loop_y, self.plot_save_dir, "splits-" + str(loop_day), True)
                except Exception as e:
                    _log.debug("%s, %s" % (type(e), str(e)))
    #   }}}


    def PlotDaily_TimestampSplits(self, loop_day, intervals_list):
        pass

    def _DivideSplitsByDay(self, days_list, splits_list):
        result_days_list = []
        for loop_day in days_list:
            pass

    def _FillMinuteRangeForDayFromSplits(self, splits_list, arg_day):
    #   {{{
        day_start, day_end = TimePlotUtils._DayStartAndEndTimes_FromDate(arg_day)
        day_mins_list = pandas.date_range(start=day_start, end=day_end, freq="min")
        day_y = [0] * len(day_mins_list)
        for loop_i, loop_min in enumerate(day_mins_list):
            pass
            #   Does loop_min fall between any pair of datetimes in splits_list
            #   Reconcile timezones:
            #   {{{
            for loop_split_start, loop_split_end in splits_list:
                if (loop_min.tzinfo is None) and (loop_split_start.tzinfo is not None):
                    loop_min = loop_min.replace(tzinfo = loop_split_start.tzinfo)
                if (loop_split_start.tzinfo is None) and (loop_min.tzinfo is not None):
                    loop_split_start = loop_split_start.replace(tzinfo = loop_min.tzinfo)
                if (loop_split_end.tzinfo is None) and (loop_min.tzinfo is not None):
                    loop_split_end= loop_split_end.replace(tzinfo = loop_min.tzinfo)
            #   }}}
                #_log.debug("loop_split_start=(%s)" % str(loop_split_start))
                if (loop_min >= loop_split_start and loop_min <= loop_split_end):
                    #_log.debug("loop_split_start=(%s), loop_split_end=(%s)" % (str(loop_split_start), str(loop_split_end)))
                    day_y[loop_i] = 1
        return [ day_mins_list, day_y ]
    #   }}}


    #   Continue: 2021-01-29T20:59:50AEDT replace dtscan cli call with python method call
    def _ReadTimestampsSplits(self, path_log, arg_date_start, arg_date_end, arg_split):
    #   {{{
        self.dtscanner._scan_qfstart = arg_date_start
        self.dtscanner._scan_qfend = arg_date_end
        self.dtscanner._scan_qfinterval = 'd'

        f = open(path_log, "r")
        result_splits = self.dtscanner.splits(f, arg_split, False)
        _log.debug("result_splits:\n%s" % pprint.pformat(result_splits, width=120))
        f.close()
        result_splits_list = []

        for loop_line in result_splits:
            loop_line_split = loop_line.split()
            #_log.debug("loop_line_split=(%s)" % str(loop_line_split))
            try:
                loop_split_dts = [ dateparser.parse(loop_line_split[3]), dateparser.parse(loop_line_split[4]) ]
                result_splits_list.append(loop_split_dts)
            except Exception as e:
                pass 
        _log.debug("len(result_splits_list)=(%s)" % len(result_splits_list))
        return result_splits_list
    #   }}}

    #   TODO: 2021-01-19T17:31:22AEDT Multiple arg_result_qty lists, with a label for each
    def _PlotTimestampMinuteRangeForDay(self, arg_result_dt, arg_result_qty, arg_output_dir=None, arg_output_fname=None, arg_markNow=False):
    #   {{{
        """plot datetimes and corresponding quantities, and save to given dir with given filename. If current datetime is in datetime range, mark it on plot"""
        #   TODO: 2021-01-04T14:42:45AEST handle multiple lists for arg_result_qty
        from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
        #   Remove timezone from datetimes
        arg_result_dt_nonetzinfo = []
        for loop_dt in arg_result_dt:
            arg_result_dt_nonetzinfo.append(loop_dt.replace(tzinfo=None))
        #   Hide log output for matplotlib
        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.WARNING)
        fig, ax = plt.subplots()
        ax.plot(arg_result_dt_nonetzinfo, arg_result_qty)
        #   If 'now' is between loop_dt[0] and loop_dt[-1], mark it with a dot
        _now = datetime.datetime.now()
        _now_y = 1
        #   If current time is between start/end of arg_result_dt, include point on plot
        if (arg_markNow) and (_now > arg_result_dt_nonetzinfo[0] and _now < arg_result_dt_nonetzinfo[-1]):
            for loop_dt, loop_qty in zip(arg_result_dt_nonetzinfo, arg_result_qty):
                if (loop_dt > _now):
                    _now_y = loop_qty
                    break
            ax.plot([_now], [_now_y], marker='o', markersize=3, color='red')
        myFmt = DateFormatter("%H")
        ax.xaxis.set_major_formatter(myFmt)
        #ax.set_ylim(0, 15)
        ax.set_xlim(arg_result_dt_nonetzinfo[0], arg_result_dt_nonetzinfo[-1])
        ax.xaxis.set_major_locator(MultipleLocator((1/24)))
        ax.yaxis.set_minor_locator(AutoMinorLocator(1))
        fig.autofmt_xdate()
        plt.savefig(os.path.join(arg_output_dir, arg_output_fname + ".png"))
        plt.close()
    #   }}}



#   }}}1

