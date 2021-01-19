#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   Imports:
#   {{{3
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
#   }}}1
import multiprocessing
from timeplot.util import TimePlotUtils
#   {{{2
_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class DecayCalc(object):

    threshold_halflife_count = 16

    #   Continue: 2021-01-03T17:17:49AEST function, for a given month, and a given list of log labels, read all log data for that month, and previous month, then calculate and plot quantities for all given label item for each day in that month
    ##   Given <arguments>, (call methods to) get lists of data from file(s) in arg_data_dir, and return list of calculated qtys remaining for each datetime in arg_dt_list 
    #    pass

    def CalculateRangeForDay(self, arg_day, arg_dt_items, arg_qty_items, arg_halflife, arg_onset):
    #   {{{
        day_start, day_end = TimePlotUtils._DayStartAndEndTimes_FromDate(arg_day)
        _result_dt_list_pandas  = pandas.date_range(start=day_start, end=day_end, freq="min")
        _result_dt_list = []
        _result_qty_list = []
        for loop_dt_pandas in _result_dt_list_pandas:
            loop_dt = loop_dt_pandas.to_pydatetime()
            loop_qty = self.CalculateAtDT(loop_dt, arg_dt_items, arg_qty_items, arg_halflife, arg_onset)
            _result_dt_list.append(loop_dt)
            _result_qty_list.append(loop_qty)
        return [ _result_dt_list, _result_qty_list ]
    #   }}}

    def _PlotResultsForDay(self, arg_result_dt, arg_result_qty, arg_output_dir=None, arg_output_fname=None, arg_markNow=False):
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
        ax.set_ylim(0, 15)
        ax.set_xlim(arg_result_dt_nonetzinfo[0], arg_result_dt_nonetzinfo[-1])
        ax.xaxis.set_major_locator(MultipleLocator((1/24)))
        ax.yaxis.set_minor_locator(AutoMinorLocator(1))
        fig.autofmt_xdate()
        plt.savefig(os.path.join(arg_output_dir, arg_output_fname + ".png"))
        plt.close()
    #   }}}

    def CalculateAtDT(self, arg_dt, arg_dt_items, arg_qty_items, arg_halflife, arg_onset):
    #   {{{
        """given lists arg_qty_items/arg_dt_items, (assuming expodential decay of arg_halflife and linear onset of arg_onset), find the qty remaining at arg_dt"""
        result_qty = Decimal(0.0)
        for loop_dt, loop_qty in zip(arg_dt_items, arg_qty_items):
            #   Reconcile timezones 
            #   {{{
            if (loop_dt.tzinfo is None) and (arg_dt.tzinfo is not None):
                loop_dt = loop_dt.replace(tzinfo = arg_dt.tzinfo)
            elif (arg_dt.tzinfo is None) and (loop_dt.tzinfo is not None):
                arg_dt = arg_dt.replace(tzinfo = loop_dt.tzinfo)
            #   }}}
            #   get difference between arg_dt and loop_dt in seconds
            loop_delta_s = (arg_dt - loop_dt).total_seconds()
            loop_result_qty = Decimal(0.0)
            if (loop_delta_s > arg_onset) and (loop_delta_s < arg_halflife * self.threshold_halflife_count):
                loop_hl_fraction = (loop_delta_s - arg_onset) / arg_halflife
                loop_result_qty = loop_qty * Decimal(0.5) ** Decimal(loop_hl_fraction)
            elif (loop_delta_s > 0) and (loop_delta_s < arg_halflife * self.threshold_halflife_count):
                loop_result_qty = loop_qty * Decimal(loop_delta_s / arg_onset)
            result_qty += loop_result_qty
        return result_qty
    #   }}}

    def TotalQtyForDay(self, arg_day, arg_dt_list, arg_qty_list):
    #   {{{
        """Get total qty in list for a given day"""
        result_sum = Decimal(0.0)
        day_start, day_end = TimePlotUtils._DayStartAndEndTimes_FromDate(arg_day)
        for loop_dt, loop_qty in zip(arg_dt_list, arg_qty_list):
            #   reconcile timezones
            #   {{{
            if (loop_dt.tzinfo is None) and (day_start.tzinfo is not None):
                loop_dt = loop_dt.replace(tzinfo = day_start.tzinfo)
            if (day_start.tzinfo is None) and (loop_dt.tzinfo is not None):
                day_start = day_start.replace(tzinfo = loop_dt.tzinfo)
            if (day_end.tzinfo is None) and (loop_dt.tzinfo is not None):
                day_end = day_end.replace(tzinfo = loop_dt.tzinfo)
            #   }}}
            if (loop_dt >= day_start) and (loop_dt <= day_end):
                result_sum += Decimal(loop_qty)
        return result_sum
    #   }}}

    #def _DayStartAndEndTimes_FromDate(self, arg_day):
    ##   {{{
    #    """For a given date, return as python datetime [ first, last ] second of that day"""
    #    if not isinstance(arg_day, datetime.datetime):
    #        arg_day = dateparser.parse(arg_day)
    #    result_start = arg_day.replace(hour=0, minute=0, second=0, microsecond=0)
    #    result_end = arg_day.replace(hour=23, minute=59, second=59, microsecond=0)
    #    return [ result_start, result_end ]
    ##   }}}


#   }}}1

