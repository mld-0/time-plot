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
from decaycalc.decaycalc import DecayCalc
from readblock.readblock import ReadBlock

_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class TimePlot(object):

    decaycalc = DecayCalc()
    readblock = ReadBlock()

    default_color_options = [ 'tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple' ]

    #   TODO: 2021-01-17T19:58:29AEDT rename schedule related 'Data' in function names

    #   Continue: 2021-01-03T17:17:49AEST function, for a given month, and a given list of log labels, read all log data for that month, and previous month, then calculate and plot quantities for all given label item for each day in that month
    ##   Given <arguments>, (call methods to) get lists of data from file(s) in arg_data_dir, and return list of calculated qtys remaining for each datetime in arg_dt_list 
    #def CalculateFromFilesRange_Monthly(self, arg_dt_list, arg_data_dir, arg_halflife, arg_onset, arg_file_prefix, arg_file_postfix):
    #    pass

    #   TODO: 2021-01-17T20:11:30AEDT start and done times, per day, from ~/.vimh

    def AnalyseTasklogDataForMonth(self, arg_tasklog_dir, arg_prefix, arg_postfix, arg_date_month, arg_output_dir):
    #   {{{
        """Get and plot start/done times from a tasklog for a given month"""
        if (isinstance(arg_date_month, str)):
            arg_date_month = dateparser.parse(arg_date_month)
            arg_date_month = arg_date_month.replace(day=1)
        y = arg_date_month.year
        m = arg_date_month.month
        days_list = ['{:04d}-{:02d}-{:02d}'.format(y, m, d) for d in range(1, calendar.monthrange(y, m)[1] + 1)]
        monthly_str = arg_date_month.strftime("%Y-%m")
        monthly_path_tasklog = os.path.join(arg_tasklog_dir, arg_prefix + monthly_str + arg_postfix)
        if not (os.path.isfile(monthly_path_tasklog)):
            raise FileNotFoundError("Not found, monthly_path_tasklog=(%s)" % str(monthly_path_tasklog))
        _log.debug("monthly_path_tasklog=(%s)" % str(monthly_path_tasklog))
        file_results_list = self.readblock.SearchTasklogs_DefaultSearchLabels( [ monthly_path_tasklog ] )
        #_log.debug("results_list=(%s)" % str(results_list))

        results_byday_date = []
        results_byday_starttime = []
        results_byday_timedone = []
        results_byday_quality = []
        results_byday_elapsed = []

        results_starttime = []
        results_timedone = []
        results_elapsed = []
        results_quality = []

        for results_list in file_results_list:
            for loop_result in results_list:
                try:
                    loop_starttime = loop_result['starttime']
                    loop_starttime = dateparser.parse(loop_starttime)
                    loop_timedone = loop_result['timedone']
                    loop_timedone = dateparser.parse(loop_timedone)
                    loop_quality = loop_result['quality']
                except Exception as e:
                    _log.error("%s, %s" % (type(e), str(e)))
                    raise Exception("Dict item (starttime, timedone, quality) not found for results of SearchTasklogs_DefaultSearchLabels")
                results_starttime.append(loop_starttime)
                results_timedone.append(loop_timedone)
                results_quality.append(loop_quality)

        for loop_day in days_list:
            _log.debug("loop_day=(%s)" % str(loop_day))
            results_byday_date.append(loop_day)
            loop_day_start, loop_day_end = self.decaycalc._DayStartAndEndTimes_FromDate(loop_day)
            #_log.debug("loop_day_start=(%s)" % str(loop_day_start))
            #_log.debug("loop_day_end=(%s)" % str(loop_day_end))

            loop_results_starttime = []
            loop_results_timedone = []
            loop_results_quality = []
            loop_results_elapsed = []

            #   TODO: 2021-01-17T20:00:05AEDT optimise -> parse each starttime/timedone only once, not once for each day

            for loop_starttime, loop_timedone, loop_quality in zip(results_starttime, results_timedone, results_quality):
                if (loop_starttime.tzinfo is None) and (loop_day_start.tzinfo is not None):
                    loop_starttime = loop_starttime.replace(tzinfo = loop_day_start.tzinfo)
                if (loop_day_start.tzinfo is None) and (loop_starttime.tzinfo is not None):
                    loop_day_start = loop_day_start.replace(tzinfo = loop_starttime.tzinfo)
                if (loop_day_end.tzinfo is None) and (loop_starttime.tzinfo is not None):
                    loop_day_end = loop_day_end.replace(tzinfo = loop_starttime.tzinfo)

                if (loop_starttime >= loop_day_start) and (loop_starttime <= loop_day_end):
                    try:
                        loop_elapsed = (loop_timedone - loop_starttime)
                    except Exception as e:
                        loop_elapsed = None
                    if (loop_elapsed is not None):
                        loop_results_starttime.append(loop_starttime)
                        loop_results_timedone.append(loop_timedone)
                        loop_results_quality.append(loop_quality)
                        loop_results_elapsed.append(loop_elapsed)
                    else:
                        _log.warning("loop_elapsed is None, skip, for loop_starttime=(%s), loop_timedone=(%s)" % (str(loop_starttime), str(loop_timedone)))

            results_byday_starttime.append(loop_results_starttime)
            results_byday_timedone.append(loop_results_timedone)
            results_byday_quality.append(loop_results_quality)
            results_byday_elapsed.append(loop_results_elapsed)

            self._PlotTaskBlocksForDay(loop_results_starttime, loop_results_timedone, loop_results_quality, loop_day, arg_output_dir)

        #_log.debug("results_byday_starttime=(%s)" % pprint.pformat(results_byday_starttime))
        #_log.debug("results_byday_timedone=(%s)" % pprint.pformat(results_byday_timedone))
        #_log.debug("results_byday_quality=(%s)" % pprint.pformat(results_byday_quality))
        #_log.debug("results_byday_elapsed=(%s)" % pprint.pformat(results_byday_elapsed))
        #   }}}

    #   TODO: 2021-01-17T20:43:06AEDT use time-quality as y-values
    def _PlotTaskBlocksForDay(self, arg_starttimes, arg_timedones, arg_qualities, arg_date, arg_output_dir):
    #   {{{
        """Given list of starttimes, timedones, qualities, from a given day, plot intervals between start/done times for that day"""
        _day_start, _day_end = self.decaycalc._DayStartAndEndTimes_FromDate(arg_date)
        _log.debug("arg_date=(%s)" % str(arg_date))
        _log.debug("_day_start=(%s), _day_end=(%s)" % (str(_day_start), str(_day_end)))
        _log.debug("len(arg_starttimes)=(%s)" % len(arg_starttimes))

        _result_dt_list_pandas  = pandas.date_range(start=_day_start, end=_day_end, freq="min")
        _result_y = [0] * len(_result_dt_list_pandas)

        #   Plot a square for each pair in arg_starttimes/arg_timedones, with height given by arg_qualities
        plot_save_path = os.path.join(arg_output_dir, arg_date + "-tasklog.png")
        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.WARNING)
        fig, ax = plt.subplots()
        ax.set_xlim(_day_start, _day_end)

        for loop_startime, loop_timedone, loop_quality in zip(arg_starttimes, arg_timedones, arg_qualities):
            loop_startime = loop_startime.replace(tzinfo=None)
            loop_timedone = loop_timedone.replace(tzinfo=None)
            #_log.debug("quality=(%s)" % str(loop_quality))
            #_log.debug("loop_startime=(%s)" % str(loop_startime))
            for loop_i, loop_x in enumerate(_result_dt_list_pandas):
                pass
                #_log.debug("loop_x=(%s)" % str(loop_x))
                if (loop_x > loop_startime and loop_x < loop_timedone):
                    _result_y[loop_i] = 1

        ax.plot(_result_dt_list_pandas, _result_y)

        myFmt = DateFormatter("%H")
        ax.xaxis.set_major_formatter(myFmt)
        ax.xaxis.set_major_locator(MultipleLocator((1/24)))
        ax.yaxis.set_minor_locator(AutoMinorLocator(1))
        fig.autofmt_xdate()
        plt.savefig(plot_save_path)
        plt.close()
    #   }}}


    def AnalyseDataByMonthForAll(self, arg_data_dir, arg_file_prefix, arg_file_postfix, arg_labels_list, arg_halflives_list, arg_onset_lists, arg_col_dt, arg_col_qty, arg_col_label, arg_col_delim, arg_output_dir, arg_color_options=None, flag_restrictFuture=True):
    #   {{{
        """call AnalyseDataForMonth, for each month between first and last date in input"""
        located_filepaths = self._GetAvailableFiles_Monthly(arg_data_dir, arg_file_prefix, arg_file_postfix)
        #self._data_dir, self.prefix, self.postfix)
        _log.debug("located_filepaths=(%s)" % str(located_filepaths))
        dt_first, dt_last = self._GetDatetimesFirstAndLast_FromFileList(located_filepaths, arg_col_dt, arg_col_delim)
        _log.debug("dt_first=(%s), dt_last=(%s)" % (str(dt_first), str(dt_last)))
        return self.AnalyseDataByMonthForDateRange(arg_data_dir, arg_file_prefix, arg_file_postfix, dt_first, dt_last, arg_labels_list, arg_halflives_list, arg_onset_lists, arg_col_dt, arg_col_qty, arg_col_label, arg_col_delim, arg_output_dir, arg_color_options, flag_restrictFuture)
    #   }}}

    def AnalyseDataByMonthForDateRange(self, arg_data_dir, arg_file_prefix, arg_file_postfix, arg_date_start, arg_date_end, arg_labels_list, arg_halflives_list, arg_onset_lists, arg_col_dt, arg_col_qty, arg_col_label, arg_col_delim, arg_output_dir, arg_color_options=None, flag_restrictFuture=True):
    #   {{{
        """As per Analyse Month, for all days between arg_date_start and arg_date_end"""
        if (isinstance(arg_date_start, str)):
            arg_date_start = dateparser.parse(arg_date_start)
        if (isinstance(arg_date_end, str)):
            arg_date_end = dateparser.parse(arg_date_end)

        _log.debug("arg_date_start=(%s)" % str(arg_date_start))
        _log.debug("arg_date_end=(%s)" % str(arg_date_end))
        located_filepaths = self._GetAvailableFiles_Monthly(arg_data_dir, arg_file_prefix, arg_file_postfix)
        #_log.debug("located_filepaths=(%s)" % str(located_filepaths))

        #   Continue: 2021-01-09T19:17:44AEDT Get list of months between arg_date_start, arg_date_end, and call self.AnalyseDataForMonth() for each
        months_list = []
        loop_date = arg_date_start
        while loop_date <= arg_date_end:
            months_list.append(loop_date.strftime("%Y-%m"))
            loop_date += relativedelta(months=1)
        _log.debug("months_list=(%s)" % str(months_list))

        for loop_month in months_list:
            self.AnalyseDataForMonth(arg_data_dir, arg_file_prefix, arg_file_postfix, loop_month, arg_labels_list, arg_halflives_list, arg_onset_lists, arg_col_dt, arg_col_qty, arg_col_label, arg_col_delim, arg_output_dir, arg_color_options, flag_restrictFuture)
        #   }}}

    def AnalyseDataForMonth(self, arg_data_dir, arg_file_prefix, arg_file_postfix, arg_date_month, arg_labels_list, arg_halflives_list, arg_onset_lists, arg_col_dt, arg_col_qty, arg_col_label, arg_col_delim, arg_output_dir, arg_color_options=None, flag_restrictFuture=True):
    #   {{{
        if (isinstance(arg_date_month, str)):
            arg_date_month = dateparser.parse(arg_date_month)
            arg_date_month = arg_date_month.replace(day=1)
        #_now = datetime.datetime.now()
        #   For month of arg_date_month, get days_list
        y = arg_date_month.year
        m = arg_date_month.month
        days_list = ['{:04d}-{:02d}-{:02d}'.format(y, m, d) for d in range(1, calendar.monthrange(y, m)[1] + 1)]
        #_log.debug("days_list=(%s)" % str(days_list))
        return self.AnalyseDataByDaysList(arg_data_dir, arg_file_prefix, arg_file_postfix, days_list, arg_labels_list, arg_halflives_list, arg_onset_lists, arg_col_dt, arg_col_qty, arg_col_label, arg_col_delim, arg_output_dir, arg_color_options, flag_restrictFuture)
    #   }}}

    def AnalyseDataByDaysList(self, arg_data_dir, arg_file_prefix, arg_file_postfix, arg_days_list, arg_labels_list, arg_halflives_list, arg_onset_lists, arg_col_dt, arg_col_qty, arg_col_label, arg_col_delim, arg_output_dir, arg_color_options=None, flag_restrictFuture=True):
    #   {{{
        _now = datetime.datetime.now()
        _log.debug("arg_data_dir=(%s)" % str(arg_data_dir))
        _log.debug("arg_file_prefix=(%s)" % str(arg_file_prefix))
        _log.debug("arg_file_postfix=(%s)" % str(arg_file_postfix))
        _log.debug("arg_days_list=(%s)" % str(arg_days_list))
        _log.debug("arg_labels_list=(%s)" % str(arg_labels_list))
        _log.debug("arg_halflives_list=(%s)" % str(arg_halflives_list))
        _log.debug("arg_onset_lists=(%s)" % str(arg_onset_lists))
        _log.debug("flag_restrictFuture=(%s)" % str(flag_restrictFuture))
        _log.debug("_now=(%s)" % str(_now))

        ##   Get filepaths for arg_date_month
        ##located_filepaths = self._GetAvailableFiles_Monthly(arg_data_dir, arg_file_prefix, arg_file_postfix)
        ##   For month of arg_date_month, get days_list
        #y = arg_date_month.year
        #m = arg_date_month.month
        #arg_days_list = ['{:04d}-{:02d}-{:02d}'.format(y, m, d) for d in range(1, calendar.monthrange(y, m)[1] + 1)]
        ##_log.debug("days_list=(%s)" % str(days_list))
        #_log.debug("arg_days_list=(%s)" % str(arg_days_list))

        located_filepaths = self._GetFiles_Monthly(arg_data_dir, arg_file_prefix, arg_file_postfix, arg_days_list[0], arg_days_list[-1], True)
        #located_filepaths = self._GetAvailableFiles_Monthly(arg_data_dir, arg_file_prefix, arg_file_postfix)
        _log.debug("located_filepaths\n%s" % str(located_filepaths))

        #   For loop_date in days_list, get results_dt and results_qty lists for each label, and plot together for said day
        result_dt = []
        results_qtys = []

        labels_list = []
        data_dt_list = dict()
        data_qty_list = dict()
        for loop_label in arg_labels_list:
            loop_data_dt_list, loop_data_qty_list = self._ReadData(located_filepaths, loop_label, arg_col_dt, arg_col_qty, arg_col_label, arg_col_delim)
            data_dt_list[loop_label] = loop_data_dt_list
            data_qty_list[loop_label] = loop_data_qty_list
            #data_dt_list = data_dt_list + loop_data_dt_list
            #data_qty_list = data_qty_list + loop_data_qty_list

        #for loop_day, loop_halflife, loop_onset  in zip(days_list, arg_halflives_list, arg_onset_lists):
        #_paths_plot_save = []
        for loop_day in arg_days_list:
            loop_day_date = None
            if not isinstance(loop_day, datetime.datetime):
                loop_day_date = dateparser.parse(loop_day)
            else:
                loop_day_date = loop_day
                loop_day = loop_day_date.strftime("%Y-%m-%d")
            _log.debug("loop_day=(%s)" % str(loop_day))
            #_log.debug("loop_day_date=(%s)" % str(loop_day_date))
            if (flag_restrictFuture) and (_now < loop_day_date):
                _log.debug("restrictFuture, break")
                break
            loop_result_dt_list = []
            loop_result_labels_list = []
            loop_result_qty_list = []
            #for loop_i, loop_label in enumerate(arg_labels_list):
            for loop_label, loop_halflife, loop_onset in zip(arg_labels_list, arg_halflives_list, arg_onset_lists):
                _log.debug("loop_label=(%s), loop_halflife=(%s), loop_onset=(%s)" % (str(loop_label), str(loop_halflife), str(loop_onset)))
                result_dt_list, result_qty_list = self.decaycalc.CalculateRangeForDay(loop_day, data_dt_list[loop_label], data_qty_list[loop_label], loop_halflife, loop_onset)
                loop_result_dt_list = result_dt_list
                loop_result_labels_list.append(loop_label)
                loop_result_qty_list.append(result_qty_list)

            #   length len mismatch check:
            #   {{{
            if (len(loop_result_labels_list) != len(loop_result_qty_list)):
                raise Exception("mismatch, len(loop_result_labels_list)=(%s) != len(loop_result_qty_list)=(%s)" % (len(loop_result_labels_list), len(loop_result_qty_list)))
            for loop_qty_list in loop_result_qty_list:
                if (len(loop_result_dt_list) != len(loop_qty_list)):
                    raise Exception("mismatch, len(loop_result_dt_list)=(%s) != len(loop_qty_list)=(%s)" % (len(loop_result_dt_list), len(loop_qty_list)))
            #   }}}

            #   Continue: 2021-01-08T23:41:01AEDT results are loop_result_qty_list for each of arg_labels_list, plot this data for each day i.e: loop itteration
            self.PlotResultsItemsForDay(loop_result_dt_list, loop_result_qty_list, loop_result_labels_list, arg_output_dir, loop_day, arg_color_options, True)
            #_paths_plot_save.append(_plot_save)
    #   }}}

    def _GetAvailableFiles_Monthly(self, arg_data_dir, arg_file_prefix, arg_file_postfix):
    #   {{{
        """Get a sorted list of the files in arg_data_dir of the form 'arg_file_prefix + %Y-%m + arg_file_postfix'"""
        filematches_regex = arg_file_prefix + "[0-9][0-9][0-9][0-9]-[0-9][0-9]" + arg_file_postfix
        filematches_glob = os.path.join(arg_data_dir, filematches_regex)
        _log.debug("filematches_glob=(%s)" % str(filematches_glob))
        filematches_list = glob.glob(filematches_glob)
        filematches_list.sort()
        _log.debug("filematches_list:\n%s" % pprint.pformat(filematches_list))
        return filematches_list
    #   }}}

    def _GetDatetimesFirstAndLast_FromFileList(self, arg_files_list, arg_col_dt, arg_delim):
    #   {{{
        """Get list of datetimes in file, sort, and return [ first, last ]. Note that sorting datetimes is only possible if they either all do, or all do not, have timezone info"""
        datetimes_list = []
        for loop_file in arg_files_list:
            loop_results_dt, loop_results_qty = self._ReadData([ loop_file ], None, arg_col_dt, None, None, arg_delim)
            datetimes_list = datetimes_list + loop_results_dt
        try:
            datetimes_list.sort()
        except Exception as e:
            _log.warning("%s, %s" % (type(e), str(e)))
            _log.warning("Failed to sort datetimes_list, using in order read from file")
        #_log.debug("datetimes_list=(%s)" % str(datetimes_list))
        result_dt_first = datetimes_list[0] 
        result_dt_last = datetimes_list[-1] 
        _log.debug("result_dt_first=(%s)" % str(result_dt_first))
        _log.debug("result_dt_last=(%s)" % str(result_dt_last))
        return [ result_dt_first, result_dt_last ]
    #   }}}

    def _ReadData(self, arg_files_list, arg_label, arg_col_dt, arg_col_qty, arg_col_label, arg_delim):
    #   {{{
        """Given a list of files, get as a list qtys and datetimes (from columns arg_col_qty and arg_col_dt), for lines where value in column arg_col_label==arg_label (if arg_label is not None, otherwise read every line). Return [ results_dt, results_qty ] lists, sorted chronologicaly"""
        _log.debug("arg_label=(%s)" % str(arg_label))
        _log.debug("cols: (dt, qty, label)=(%s, %s, %s), delim=(%s)" % (arg_col_dt, arg_col_qty, arg_col_label, arg_delim))
        results_dt = []
        results_qty = []
        for loop_filepath in arg_files_list:
            loop_filestr = self._DecryptGPGFileToString(loop_filepath)
            for loop_line in loop_filestr.split("\n"):
                loop_line_split = loop_line.split(arg_delim)
                if not (len(loop_line_split) <= 1):
                    #_log.debug("loop_line_split=(%s)" % str(loop_line_split))
                    if (arg_label is None) or (loop_line_split[arg_col_label] == arg_label):
                        loop_qty = None
                        if (arg_col_qty is not None):
                            loop_qty_str = loop_line_split[arg_col_qty]
                            loop_qty = Decimal(loop_qty_str)
                        loop_dt_str = loop_line_split[arg_col_dt]
                        loop_dt_str = self._Fix_Datetime_Format(loop_dt_str)

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

                        #_log.debug("loop_dt_str=(%s)" % str(loop_dt_str))
                        #_log.debug("loop_qty=(%s)" % str(loop_qty))
                        #_log.debug("loop_dt=(%s)" % str(loop_dt))
                        results_dt.append(loop_dt)
                        results_qty.append(loop_qty)

        if (len(results_dt) != len(results_qty)):
            raise Exception("mismatch, len(results_dt)=(%s), len(results_qty)=(%s)" % (str(len(results_dt)), str(len(results_qty))))
        _log.debug("len(results)=(%s)" % str(len(results_dt)))
        return [ results_dt, results_qty ]
        #   }}}

    def _Fix_Datetime_Format(self, arg_dt_str):
    #   {{{
        """If datetime is in 'dts' format, i.e: (2021-01-02)-(21-17-11) or (2021-01-02)-(2117-11), transform to iso format 2021-01-02T21:17:11, otherwise return as-is"""
        #   
        regex_dts = r"\((\d{4}-\d{2}-\d{2})\)-\((\d{2})-?(\d{2})-?(\d{2})\)"
        _match_regex = re.match(regex_dts, arg_dt_str)
        if (_match_regex is not None):
            arg_dt_str = _match_regex.group(1) + "T" + _match_regex.group(2) + ":" + _match_regex.group(3) + ":" + _match_regex.group(4)
        return arg_dt_str
    #   }}}

    def PlotResultsItemsForDay(self, arg_result_dt, arg_result_qty_list, arg_labels_list, arg_output_dir=None, arg_output_fname=None, arg_color_options=None, arg_markNow=False):
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

        _log.debug("arg_output_dir=(%s)" % str(arg_output_dir))
        _log.debug("arg_output_fname=(%s)" % str(arg_output_fname))

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
            _log.debug("_path_save=(%s)" % str(_path_save))
            return _path_save
        else:
            #plt.ioff()
            #plt.show(block=False)
            plt.show()
            plt.close()
            pass
    #   }}}

    def _PlotResultsForDay(self, arg_result_dt, arg_result_qty, arg_output_dir=None, arg_output_fname=None, arg_markNow=False):
    #   {{{
        """plot datetimes and corresponding quantities, and save to given dir with given filename. If current datetime is in datetime range, mark it on plot"""
    #   TODO: 2021-01-04T14:42:45AEST handle multiple lists for arg_result_qty
        #   Remove timezone from datetimes
        arg_result_dt_noTZ = []
        for loop_dt in arg_result_dt:
            arg_result_dt_noTZ.append(loop_dt.replace(tzinfo=None))
        #   Hide debug log output for matplotlib
        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.WARNING)
        fig, ax = plt.subplots()
        ax.plot(arg_result_dt_noTZ, arg_result_qty)
        #   If 'now' is between loop_dt[0] and loop_dt[-1], mark it with a dot
        _now = datetime.datetime.now()
        _now_y = 1
        #   If current time is between start/end of arg_result_dt, include point on plot
        if (arg_markNow) and (_now > arg_result_dt_noTZ[0] and _now < arg_result_dt_noTZ[-1]):
            for loop_dt, loop_qty in zip(arg_result_dt_noTZ, arg_result_qty):
                if (loop_dt > _now):
                    _now_y = loop_qty
                    break
            ax.plot([_now], [_now_y], marker='o', markersize=3, color='red')
        myFmt = DateFormatter("%H")
        ax.xaxis.set_major_formatter(myFmt)
#        ax.set_ylim(0, 15)
        ax.set_xlim(arg_result_dt_noTZ[0], arg_result_dt_noTZ[-1])
        ax.xaxis.set_major_locator(MultipleLocator((1/24)))
        ax.yaxis.set_minor_locator(AutoMinorLocator(1))
        fig.autofmt_xdate()
        plt.savefig(os.path.join(arg_output_dir, arg_output_fname + ".png"))
        plt.close()
    #   }}}

    def _EncryptString2GPGByteArray(self, text_str, gpg_key_id, flag_ascii_armor=False):
    #   {{{
        """Take a string, encrypt that string with the system gpg keychain, and return result as a bytearray"""
        t_start = time.time()
        #   convert string(text_str) -> bytearray(cmd_encrypt_input)
        cmd_encrypt_input = bytearray()
        cmd_encrypt_input.extend(text_str.encode())
        #   gpg encrypt arguments
        cmd_gpg_encrypt = [ "gpg", "-o", "-", "-q", "--encrypt", "--recipient", gpg_key_id ]
        if (flag_ascii_armor == True):
            cmd_gpg_encrypt.append("--armor")
        #   Use Popen, call cmd_gpg_encrypt, using PIPE for stdin/stdout/stderr
        p = Popen(cmd_gpg_encrypt, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        result_data_encrypt, result_stderr = p.communicate(input=cmd_encrypt_input)
        result_stderr = result_stderr.decode()

        rc = p.returncode
        if (rc != 0):
            raise Exception("Failed to encrypt, rc=(%s)" % str(rc))

        t_end = time.time()
        t_elapsed = round(t_end - t_start, 2)
        #   printdebug:
        _log.debug("encrypt dt=(%s)" % (str(t_elapsed)))
        _log.debug("cmd_gpg_encrypt=(%s)" % str(cmd_gpg_encrypt))
        _log.debug("result_stderr=(%s)" % str(result_stderr))
        _log.debug("text_str_len=(%s)" % str(len(text_str)))
        _log.debug("result_data_encrypt_len=(%s)" % str(len(result_data_encrypt)))

        return result_data_encrypt
    #   }}}

    def _CopyAndDivideDataByMonth(self, arg_source_path, arg_dest_dir, arg_dest_prefix, arg_dest_postfix, arg_dt_first, arg_dt_last, arg_overwrite=False, arg_includeMonthBefore=False, arg_gpg_key=None):
    #   {{{
        """Copy lines from single source file arg_source_path to file(s) in arg_dest_dir, for range of months, copying lines containing given month to destination file for said month"""
        dt_Range_str = self._GetMonthRange(arg_dt_first, arg_dt_last, arg_includeMonthBefore, True)

        for loop_dt_str in dt_Range_str:
            loop_data = ""
            with open(arg_source_path, "r") as f:
                for loop_line in f:
                    loop_line = loop_line.strip()
                    #   If loop_line contains loop_dt_str, append it to loop_data
                    if not loop_line.find(loop_dt_str) == -1:
                        loop_data += loop_line + '\n'
            _log.debug("loop_dt_str=(%s) lines(loop_data)=(%s)" % (str(loop_dt_str), len(loop_data.split('\n'))))

            loop_dest_filename = arg_dest_prefix + loop_dt_str + arg_dest_postfix
            loop_dest_filepath = os.path.join(arg_dest_dir, loop_dest_filename)
            _log.debug("loop_dest_filename=(%s)" % str(loop_dest_filename))

            if os.path.isfile(loop_dest_filepath) and not arg_overwrite:
                _log.debug("skip write, arg_overwrite=(%s)" % str(arg_overwrite))
                return 

            if not (arg_gpg_key is None):
                #   TODO: 2021-01-11T18:46:45AEDT if hash of loop_data matches hash of decrypted contents of loop_dest_filepath, skip write
                loop_data_enc = self._EncryptString2GPGByteArray(loop_data, arg_gpg_key, False)
                with open(loop_dest_filepath, "wb") as f:
                    f.write(loop_data_enc)
            else:
                with open(loop_dest_filepath, "w") as f:
                    f.write(loop_data)
    #   }}}

    def _GetMonthRange(self, arg_dt_first, arg_dt_last, arg_includeMonthBefore=False, arg_result_str=True):
    #   {{{
        if (isinstance(arg_dt_first, str)):
            arg_dt_first = dateparser.parse(arg_dt_first)
        arg_dt_first = arg_dt_first.replace(day=1)
        if (isinstance(arg_dt_last, str)):
            arg_dt_last = dateparser.parse(arg_dt_last)
        arg_dt_last = arg_dt_last.replace(day=1)
        if (arg_dt_first > arg_dt_last):
            raise Exception("Invalid arg_dt_first=(%s) > arg_dt_last=(%s)" % (str(arg_dt_first), str(arg_dt_last)))
        _dt_format_convertrange = '%Y-%m-%dT%H:%M:%S%Z'
        _dt_format_output = '%Y-%m'
        _dt_freq = 'MS'

        arg_dt_beforeFirst = arg_dt_first
        _log.debug("arg_includeMonthBefore=(%s)" % str(arg_includeMonthBefore))

        if (arg_includeMonthBefore):
            arg_dt_beforeFirst = arg_dt_first + relativedelta(months = -1)
        arg_dt_beforeFirst = arg_dt_beforeFirst.replace(day=1)

        _log.debug("arg_dt_first=(%s)" % str(arg_dt_first))
        _log.debug("arg_dt_beforeFirst=(%s)" % str(arg_dt_beforeFirst))
        _log.debug("arg_dt_last=(%s)" % str(arg_dt_last))

        dt_Range = [ x for x in pandas.date_range(start=arg_dt_beforeFirst.strftime(_dt_format_convertrange), end=arg_dt_last.strftime(_dt_format_convertrange), freq=_dt_freq) ]
        dt_Range_str = [ x.strftime(_dt_format_output) for x in dt_Range ]

        _log.debug("dt_Range=(%s)" % str(dt_Range))
        _log.debug("dt_Range_str=(%s)" % str(dt_Range_str))

        if (arg_result_str):
            return dt_Range_str
        else:
            return dt_Range
    #   }}}

    def _GetFiles_Monthly(self, arg_data_dir, arg_file_prefix, arg_file_postfix, arg_dt_first, arg_dt_last, arg_includeMonthBefore=False):
    #   {{{ 
        """Get a list of the files in arg_data_dir, where each file is of the format 'arg_file_prefix + date_str + arg_file_postfix', and date_str is %Y-%m for each year and month between one month before arg_dt_first, and arg_dt_last"""
        dt_Range_str = self._GetMonthRange(arg_dt_first, arg_dt_last, arg_includeMonthBefore, True)

        #   Raise exception if arg_data_dir doesn't exist
        if not os.path.isdir(arg_data_dir):
            raise Exception("dir not found arg_data_dir=(%s)" % str(arg_data_dir))
        #   Get list of files of format 'arg_file_prefix + date_str + arg_file_postfix' which exist, with warning for those which don't. Raise exception if no files are found
        located_filepaths = []
        for loop_dt_str in dt_Range_str:
            loop_candidate_filename = arg_file_prefix + loop_dt_str + arg_file_postfix
            loop_candidate_filepath = os.path.join(arg_data_dir, loop_candidate_filename)
            if os.path.isfile(loop_candidate_filepath):
                located_filepaths.append(loop_candidate_filepath)
        _log.debug("located_filepaths:\n%s" % pprint.pformat(located_filepaths))
        if len(located_filepaths) == 0:
            raise Exception("no files located")
        return located_filepaths
    #   }}}

    def _DecryptGPGFileToString(self, arg_path_file):
    #   {{{
        """Given a path to gpg encrypted file, decrypt file using system gpg/keychain, raise Exception if file is not decryptable, or if it doesn't exist"""
        _log.debug("file=(%s)" % str(os.path.basename(arg_path_file)))
        cmd_gpg_decrypt = ["gpg", "-q", "--decrypt", arg_path_file ]
        p = Popen(cmd_gpg_decrypt, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        result_data_decrypt, result_stderr = p.communicate()
        result_str = result_data_decrypt.decode()
        result_stderr = result_stderr.decode()
        rc = p.returncode
        if (rc != 0):
            raise Exception("gpg decrypt non-zero returncode=(%s), result_stderr=(%s)" % (str(rc), str(result_stderr)))
        _log.debug("lines=(%s)" % str(result_str.count("\n")))
        return result_str
    #   }}}

#   }}}1


