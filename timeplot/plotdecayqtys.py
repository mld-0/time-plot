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

class PlotDecayQtys(object):
    default_color_options = [ 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple', 'tab:red'  ]
    decaycalc = DecayCalc()

    #   Source data from 'data_file_dir/data_file_prefix+<date-str>+data_file_postfix'
    data_file_dir = None
    data_file_prefix = None
    data_file_postfix = None

    plot_save_dir = os.path.join(tempfile.gettempdir(), "PlotDecayQtys")

    _data_labels = []
    _data_halflives = []
    _data_onsets = []

    data_column_dt = None
    data_column_qty = None
    data_column_label = None
    data_delim = ","

    _data_labels_file = [ 'timeplot', 'data-items.txt' ]
    _data_cols_file = [ 'timeplot', 'data-columns.txt' ]

    flag_restrictFuture = True

    def __init__(self):
    #   {{{
        self._ReadResource_DataLabels()
        self._ReadResource_DataCols()
        #   Create plot_save_dir
        #   {{{
        if not os.path.isdir(self.plot_save_dir):
            _log.debug("mkdir plot_save_dir=(%s)" % str(self.plot_save_dir))
            os.mkdir(self.plot_save_dir)
        #   }}}
    #   }}}

    def PlotDaily_DecayQtys_ForDateRange(self, arg_date_start, arg_date_end, arg_restrictFuture=True):
    #   {{{
        range_calendar_list = TimePlotUtils._GetDaysPerMonthDateRange_FromFirstAndLast(arg_date_start, arg_date_end)
        range_months_list = TimePlotUtils._GetMonthlyDateRange_FromFirstAndLast(arg_date_start, arg_date_end)
        _now = datetime.datetime.now()

        if (len(range_calendar_list) != len(range_months_list)):
            raise Exception("(len(range_calendar_list)=(%s) != len(range_months_list))=(%s)" % (len(range_calendar_list), len(range_months_list)))

        for loop_month, loop_days_list in zip(range_months_list, range_calendar_list):
            #loop_month_previous = loop_month + relativedelta(months=-1)
            loop_files_list = TimePlotUtils._GetFiles_FromMonthlyRange(self.data_file_dir, self.data_file_prefix, self.data_file_postfix, loop_month, loop_month, True)
            data_dt_lists = dict()
            data_qty_lists = dict()
            for loop_label in self._data_labels:
                loop_data_dt_list, loop_data_qty_list = self._ReadData(loop_files_list, loop_label)
                data_dt_lists[loop_label] = loop_data_dt_list
                data_qty_lists[loop_label] = loop_data_qty_list
            for loop_day in loop_days_list:
                loop_day_date = dateparser.parse(loop_day)
                if (arg_restrictFuture) and (_now < loop_day_date):
                    _log.debug("restrict future, break")
                    break
                self.PlotDaily_DecayQtys(loop_day, data_dt_lists, data_qty_lists)
    #   }}}

    def PlotDaily_DecayQtys(self, loop_day, data_dt_lists, data_qty_lists):
    #   {{{
        loop_dt_list = []
        loop_qty_lists = []
        for loop_label, loop_halflife, loop_onset in zip(self._data_labels, self._data_halflives, self._data_onsets):
            _log.debug("loop_day=(%s), loop_label=(%s)" % (str(loop_day), str(loop_label)))
            loop_dt_list, result_loop_qty_list = self.decaycalc.CalculateRangeForDay(loop_day, data_dt_lists[loop_label], data_qty_lists[loop_label], loop_halflife, loop_onset)
            loop_qty_lists.append(result_loop_qty_list)
        self._PlotResultsItemsForDay(loop_dt_list, loop_qty_lists, self._data_labels, self.plot_save_dir, "decayqty-" + loop_day, self.default_color_options, True)
    #   }}}

    def PlotDaysPerWeek_DecayQtys_ForDateRange(self, arg_date_start, arg_date_end):
        pass
    def PlotWeeksPerYear_DecayQtys_ForDateRange(self, arg_date_start, arg_date_end):
        pass

    def _ReadData(self, arg_files_list, arg_label):
    #   {{{
        """Given a list of files, get as lists qtys and datetimes (from columns self.data_column_qty and self.data_column_dt, columns defined by self.data_delim), for lines where value in column self.data_column_label==arg_label (if arg_label is None, read every line). Return [ results_dt, results_qty ]"""
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

                if (len(loop_line.strip()) == 0):
                    #_log.warning("empty loop_line=(%s)" % str(loop_line))
                    continue
                if (len(loop_line_split) <= 1):
                    _log.warning("len(loop_line_split)=(%s), loop_line_split=(%s)" % (len(loop_line_split), str(loop_line_split)))
                    continue

                if (arg_label is None) or (loop_line_split[self.data_column_label] == arg_label):
                    loop_qty_str = loop_line_split[self.data_column_qty]
                    loop_qty = Decimal(loop_qty_str)

                    loop_dt_str = loop_line_split[self.data_column_dt]
                    loop_dt_str = TimePlotUtils._Fix_DatetimeStr(loop_dt_str)

                    #   Attempt parsing with datetime.datetime.strptime() on account of slowness of dateparser.parse
                    loop_dt = None
                    #   {{{
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
                    #   }}}
                    if (loop_dt is None):
                        loop_dt = dateparser.parse(loop_dt_str)

                    if (loop_dt is None):
                        raise Exception("Failed to parse loop_dt_str=(%s)" % str(loop_dt_str))
                    if (loop_qty is None):
                        raise Exception("Failed to parse loop_qty=(%s)" % str(loop_qty))

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

    def _PlotResultsItemsForDay(self, arg_result_dt, arg_result_qty_list, arg_labels_list, arg_output_dir=None, arg_output_fname=None, arg_color_options=None, arg_markNow=False):
    #   {{{
        """Plot list of list of qty values, against single list of time, with labels and colours specified. Show figure if arg_output_dir is None, otherwise save it."""
        #   Remove timezone from datetimes (so they appear correctly on plot)
        arg_result_dt_noTZ = []
        for loop_dt in arg_result_dt:
            arg_result_dt_noTZ.append(loop_dt.replace(tzinfo=None))
        #   Hide debug log output from matplotlib
        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.WARNING)
        #   Plot qty list corresponding to each label
        fig, ax = plt.subplots()
        ax.set_xlabel('time')
        myFmt = DateFormatter("%H")
        #ax.xaxis.set_major_formatter(myFmt)
        _check_showPlot = False

        #_log.debug("arg_output_dir:\n%s" % str(arg_output_dir))
        #_log.debug("arg_output_fname=(%s)" % str(arg_output_fname))

        #   Setup axis list, one axis for each non-zero list in arg_result_qty_list
        ax_list = [ ]
        #   {{{
        loop_i = 0
        while (loop_i < len(arg_labels_list)):
            _found_gtZero = False
            loop_qty_list = arg_result_qty_list[loop_i]
            for loop_qty_value in loop_qty_list:
                if (loop_qty_value > 0):
                    _found_gtZero = True
                    break
            if (_found_gtZero):
                if (len(ax_list) > 0):
                    ax_list.append(ax_list[loop_i-1].twinx())
                else:
                    ax_list.append(ax)
            loop_i += 1
        #   }}}
        if (arg_color_options is None):
            arg_color_options = self.default_color_options
        for loop_ax, loop_label, loop_qty_list, loop_color  in zip(ax_list, arg_labels_list, arg_result_qty_list, arg_color_options):
            #   Check loop_qty_list contains at least one non-zero value, otherwise do not plot (prevents distorition of axis by align_yaxis_np for all-zero case)
            _found_gtZero = False
            for loop_qty_value in loop_qty_list:
                if (loop_qty_value > 0):
                    _found_gtZero = True
                    _check_showPlot = True
                    break
            if (_found_gtZero):
                loop_ax.set_ylabel(loop_label, color=loop_color)
                loop_ax.xaxis.set_major_formatter(myFmt)
                loop_ax.set_xlim(arg_result_dt_noTZ[0], arg_result_dt_noTZ[-1])
                loop_ax.tick_params(axis='y', labelcolor=loop_color)
                loop_ax.plot(arg_result_dt_noTZ, loop_qty_list, color=loop_color)
                loop_ax.xaxis.set_major_locator(MultipleLocator((1/24)))
                loop_ax.yaxis.set_minor_locator(AutoMinorLocator(1))

                #   if arg_markNow, and current time is on plot, include point/line <on first/last> plot line
                _now = datetime.datetime.now()
                if (arg_markNow) and (_now > arg_result_dt_noTZ[0] and _now < arg_result_dt_noTZ[-1]):
                    _now_y = 1
                    _log.debug("mark _now=(%s)" % str(_now))
                    for loop_dt, loop_qty in zip(arg_result_dt_noTZ, loop_qty_list):
                        #if (_now < arg_result_dt_noTZ[0] and _now > arg_result_dt_noTZ[-1]):
                        if (loop_dt >= _now):
                            _now_y = loop_qty
                            _log.debug("loop_label=(%s)" % str(loop_label))
                            _log.debug("_now_y=(%s)" % str(_now_y))
                            #_log.debug("loop_qty_list=(%s)" % str(loop_qty_list))
                            break
                    loop_ax.plot([_now], [_now_y], marker='o', markersize=3, color=loop_color)

        if not (_check_showPlot):
            _log.warning("_check_showPlot=(%s), noting to plot, skip day" % str(_check_showPlot))
            return 

        fig.tight_layout()
        fig.autofmt_xdate()

        if not (arg_output_dir is None):
            _path_save = os.path.join(arg_output_dir, arg_output_fname + ".png")
            plt.savefig(_path_save)
            plt.close()
            _log.debug("_path_save:\n%s" % str(_path_save))
            return _path_save
        else:
            #plt.ioff()
            #plt.show(block=False)
            plt.show()
            plt.close()
            pass
    #   }}}

    def _ReadResource_DataLabels(self):
    #   {{{
        """Read resource file _data_labels_file to _data_labels, _data_halflives, _data_onsets as tab-delimited values. Halflives/onsets values from file are in minutes - convert to seconds (*60)"""
        file_poll_items = importlib.resources.open_text(*self._data_labels_file)
        _log.debug("file_poll_items=(%s)" % str(file_poll_items))
        self._data_labels = []
        self._data_halflives = []
        self._data_onsets = []
        for loop_line in file_poll_items:
            loop_line = loop_line.strip()
            loop_line = loop_line.split("\t")
            if (len(loop_line) > 1):
                self._data_labels.append(loop_line[0])
                self._data_halflives.append(60 * int(loop_line[1]))
                self._data_onsets.append(60 * int(loop_line[2]))
        file_poll_items.close()
        _log.debug("_data_labels=(%s)" % str(self._data_labels))
        _log.debug("_data_halflives=(%s)" % str(self._data_halflives))
        _log.debug("_data_onsets=(%s)" % str(self._data_onsets))
    #   }}}

    def _ReadResource_DataCols(self):
    #   {{{
        """Read resource file _data_cols_file to _data_cols as tab-delimited integers. Values (in order): [ label, qty, datetime ]"""
        file_data_cols = importlib.resources.open_text(*self._data_cols_file)
        _log.debug("file_data_cols=(%s)" % str(file_data_cols))
        filedata = file_data_cols.read().strip()
        _data_cols_str = filedata.split("\t")
        self.data_column_label = int(_data_cols_str[0])
        self.data_column_qty = int(_data_cols_str[1])
        self.data_column_dt = int(_data_cols_str[2])
        file_data_cols.close()
        _log.debug("cols, (lbl, qty, dt)=(%s, %s, %s)" % (str(self.data_column_label), str(self.data_column_qty), str(self.data_column_dt)))
    #   }}}

#   }}}1

