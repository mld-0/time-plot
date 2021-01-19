#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   Imports:
#   {{{3
import unittest
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
import pprint
import webbrowser
import tempfile
from subprocess import Popen, PIPE, STDOUT
from io import StringIO
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from matplotlib.dates import DateFormatter
#   }}}1
from timeplot.decaycalc import DecayCalc
from timeplot.timeplot import TimePlot
from timeplot.plotdecayqtys import PlotDecayQtys
from timeplot.util import TimePlotUtils
from timeplot.plottimestamps import PlotTimestamps
#   {{{1

#   debug logging
_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class Test_DecayCalc(unittest.TestCase):
#   {{{
    decaycalc = DecayCalc()
    timeplot = TimePlot()

    #   Set True to open output directory in Finder 
    _flag_openPlots = False

    _tasklog_dir = os.path.join(os.environ.get('mld_tasklogs'), "_worklog")

    _pkg_testdata = "data"
    def _getPath_TestData(self, arg_fname):
    #   {{{
        path_test = None
        with importlib.resources.path(self._pkg_testdata, arg_fname) as p:
            path_test = str(p)
        return path_test
    #   }}}

    #   TODO: 2021-01-18T19:54:13AEDT dedicated test data as test input
    #   Use files created by 'pulse' as test input
    _data_dir_schedule = os.environ.get('mld_logs_pulse')
    _output_dir = os.path.join(tempfile.gettempdir(), "test-decaycalc")
    if not os.path.isdir(_output_dir):
        _log.debug("mkdir _output_dir=(%s)" % str(_output_dir))
        os.mkdir(_output_dir)

    prefix = "Schedule.calc."
    postfix = ".vimgpg"

    _test_postfix = "\n"

    #day_analyse = dateparser.parse("2021-01-04T00:00:00AEST")
    day_analyse = dateparser.parse("2021-01-03")

    month_analyse = "2021-01"

    dt_analyse = dateparser.parse("2021-01-03T14:13:42AEST")
    dt_start = dateparser.parse("2021-01-01T16:08:18AEST")
    dt_end = dateparser.parse("2021-01-02T16:08:18AEST")
    label = "D-IR"
    label = "Can-S"
    col_label = 0
    col_qty = 1
    col_dt = 3
    delim = ","
    onset = 20 * 60
    halflife = 30 * 60

    color_options = [ "blue", "green", "red", "black", "orange" ]

    labels_list = [ "D-IR", "Can-S" ]
    halflives_list = [ 45*60, 45*60 ]
    onset_lists = [ 20*60, 3*60 ]

    tasklog_prefix = ""
    tasklog_postfix = ".worklog.vimgpg"

    #   Continue: 2021-01-09T18:10:29AEDT test_AnalyseDataAll
    #   Continue: 2021-01-09T18:12:37AEDT get starttime/timedone from tasklogs, plot alongside data from schedule log file

    if (False):
        def test_PlotDecayQtys_HelloWorld(self):
            plotdecayqtys = PlotDecayQtys()

        def test_GetDaysPerMonthDateRange_FromFirstAndLast(self):
            dt_start = dateparser.parse("2020-11-18T18:18:31AEDT")
            dt_end = dateparser.parse("2021-01-18T18:18:52AEDT")
            #   {{{
            expected_result = [['2020-11-18', '2020-11-19', '2020-11-20', '2020-11-21', '2020-11-22', '2020-11-23', '2020-11-24', '2020-11-25', '2020-11-26', '2020-11-27', '2020-11-28', '2020-11-29', '2020-11-30'], ['2020-12-01', '2020-12-02', '2020-12-03', '2020-12-04', '2020-12-05', '2020-12-06', '2020-12-07', '2020-12-08', '2020-12-09', '2020-12-10', '2020-12-11', '2020-12-12', '2020-12-13', '2020-12-14', '2020-12-15', '2020-12-16', '2020-12-17', '2020-12-18', '2020-12-19', '2020-12-20', '2020-12-21', '2020-12-22', '2020-12-23', '2020-12-24', '2020-12-25', '2020-12-26', '2020-12-27', '2020-12-28', '2020-12-29', '2020-12-30', '2020-12-31'], ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09', '2021-01-10', '2021-01-11', '2021-01-12', '2021-01-13', '2021-01-14', '2021-01-15', '2021-01-16', '2021-01-17', '2021-01-18']]
            #   }}}
            calendar_list = TimePlotUtils._GetDaysPerMonthDateRange_FromFirstAndLast(dt_start, dt_end)
            #_log.debug("calendar_list=(%s)" % str(calendar_list))
            self.assertEqual(calendar_list, expected_result)

        #def test_PlotDecayQtys_PlotDaily_DecayQtys_ForDateRange_short(self):
        #    dt_start = dateparser.parse("2021-01-12T18:18:31AEDT")
        #    dt_end = dateparser.parse("2021-01-17T18:18:52AEDT")
        #    plotdecayqtys = PlotDecayQtys()
        #    plotdecayqtys.data_file_dir = self._data_dir_schedule
        #    plotdecayqtys.data_file_prefix = self.prefix
        #    plotdecayqtys.data_file_postfix = self.postfix
        #    plotdecayqtys.PlotDaily_DecayQtys_ForDateRange(dt_start, dt_end)

        def test_PlotDecayQtys_PlotDaily_DecayQtys_ForDateRange_singleday(self):
            dt_start = dateparser.parse("2021-01-17T18:18:31AEDT")
            dt_end = dateparser.parse("2021-01-17T18:18:52AEDT")
            plotdecayqtys = PlotDecayQtys()
            plotdecayqtys.data_file_dir = self._data_dir_schedule
            plotdecayqtys.data_file_prefix = self.prefix
            plotdecayqtys.data_file_postfix = self.postfix
            plotdecayqtys.PlotDaily_DecayQtys_ForDateRange(dt_start, dt_end)

    if (False):
        #   {{{
        def test_PlotDecayQtys_PlotDaily_DecayQtys_ForDateRange(self):
            dt_start = dateparser.parse("2020-12-18T18:18:31AEDT")
            dt_end = dateparser.parse("2021-01-18T18:18:52AEDT")
            plotdecayqtys = PlotDecayQtys()
            plotdecayqtys.data_file_dir = self._data_dir_schedule
            plotdecayqtys.data_file_prefix = self.prefix
            plotdecayqtys.data_file_postfix = self.postfix
            plotdecayqtys.PlotDaily_DecayQtys_ForDateRange(dt_start, dt_end)
        #   }}}

    #   Splits/SplitSum tests
    if (True):
        def test_AnalyseVimhSample(self):
            dt_start = dateparser.parse("2021-01-12T18:18:31AEDT")
            dt_end = dateparser.parse("2021-01-17T18:18:52AEDT")
            _vimh_sample_6day = self._getPath_TestData("vimh-6daysample.txt")
            _log.debug("_vimh_sample_6day=(%s)" % str(_vimh_sample_6day))
            plottimestamps = PlotTimestamps()
            #plottimestamps.data_file_prefix = _vimh_sample_6day
            plottimestamps.PlotDaily_TimestampSplits_ForDateRange(_vimh_sample_6day, dt_start, dt_end)

    #   Previous test functions
    if (False):
    #   {{{

        def test_AnalyseTasklogDataForMonth(self):
            _log.debug("_tasklog_dir=(%s)" % str(self._tasklog_dir))
            self.timeplot.AnalyseTasklogDataForMonth(self._tasklog_dir, self.tasklog_prefix, self.tasklog_postfix, self.month_analyse, self._output_dir)

        def test_AnalyseToday(self):
                date_start = datetime.datetime.now()
                date_end = datetime.datetime.now()
                #self.timeplot.AnalyseDataByDaysList(self._data_dir_schedule, self.prefix, self.postfix, [ date_start, date_end ], self.labels_list, self.halflives_list, self.onset_lists, self.col_dt, self.col_qty, self.col_label, self.delim, self._output_dir, self.color_options)
                self.timeplot.AnalyseDataByDaysList(self._data_dir_schedule, self.prefix, self.postfix, [ date_start, date_end ], self.labels_list, self.halflives_list, self.onset_lists, self.col_dt, self.col_qty, self.col_label, self.delim, self._output_dir, self.color_options)

        def test_TodayAnalyse(self):
            today_analyse = datetime.datetime.now()
            located_filepaths = self.timeplot._GetFiles_Monthly(self._data_dir_schedule, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
            results_dt, results_qty = self.timeplot._ReadData(located_filepaths, self.label, self.col_dt, self.col_qty, self.col_label, self.delim)
            _result_dt_list, _result_qty_list = self.decaycalc.CalculateRangeForDay(today_analyse, results_dt, results_qty, self.halflife, self.onset)
            _output_fname = today_analyse.strftime("%Y-%m-%d")
            self.timeplot._PlotResultsForDay(_result_dt_list, _result_qty_list, self._output_dir, _output_fname, True)
            if (self._flag_openPlots):
                webbrowser.open('file:%s' % self._output_dir)
            sys.stderr.write(self._test_postfix)

        def test_CalculateRangeForDay(self):
            located_filepaths = self.timeplot._GetFiles_Monthly(self._data_dir_schedule, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
            results_dt, results_qty = self.timeplot._ReadData(located_filepaths, self.label, self.col_dt, self.col_qty, self.col_label, self.delim)
            _result_dt_list, _result_qty_list = self.decaycalc.CalculateRangeForDay(self.day_analyse, results_dt, results_qty, self.halflife, self.onset)
            _output_fname = self.day_analyse.strftime("%Y-%m-%d")
            self.timeplot._PlotResultsForDay(_result_dt_list, _result_qty_list, self._output_dir, _output_fname, True)
            if (self._flag_openPlots):
                webbrowser.open('file:%s' % self._output_dir)
            sys.stderr.write(self._test_postfix)

        def test_AnalyseCurrentMonth(self):
                date_start = datetime.datetime.now()
                date_end = datetime.datetime.now()
                self.timeplot.AnalyseDataByMonthForDateRange(self._data_dir_schedule, self.prefix, self.postfix, date_start, date_end, self.labels_list, self.halflives_list, self.onset_lists, self.col_dt, self.col_qty, self.col_label, self.delim, self._output_dir, self.color_options)

        def test_ReadData(self):
            located_filepaths = self.timeplot._GetFiles_Monthly(self._data_dir_schedule, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
            results_dt, results_qty = self.timeplot._ReadData(located_filepaths, self.label, self.col_dt, self.col_qty, self.col_label, self.delim)
            self.assertTrue(len(results_dt) > 0, "Expect non-empty results=(%s)" % results_dt)
            sys.stderr.write(self._test_postfix)

        def test_CalculateAtDT(self):
            located_filepaths = self.timeplot._GetFiles_Monthly(self._data_dir_schedule, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
            results_dt, results_qty = self.timeplot._ReadData(located_filepaths, self.label, self.col_dt, self.col_qty, self.col_label, self.delim)
            remaining_qty = self.decaycalc.CalculateAtDT(self.dt_analyse, results_dt, results_qty, self.halflife, self.onset)
            sys.stderr.write(self._test_postfix)

        #def test_AnalyseAll(self):
        #    self.timeplot.AnalyseDataByMonthForAll(self._data_dir_schedule, self.prefix, self.postfix, self.labels_list, self.halflives_list, self.onset_lists, self.col_dt, self.col_qty, self.col_label, self.delim, self._output_dir, self.color_options)

        def test_AnalyseMonth(self):
            self.timeplot.AnalyseDataForMonth(self._data_dir_schedule, self.prefix, self.postfix, self.month_analyse, self.labels_list, self.halflives_list, self.onset_lists, self.col_dt, self.col_qty, self.col_label, self.delim, self._output_dir, self.color_options)
            if (self._flag_openPlots):
                webbrowser.open('file:%s' % self._output_dir)
            sys.stderr.write(self._test_postfix)

        def test_GetAvailableFiles_Monthly(self):
            located_filepaths = self.timeplot._GetAvailableFiles_Monthly(self._data_dir_schedule, self.prefix, self.postfix)
            sys.stderr.write(self._test_postfix)

        def test_GetFiles_Monthly(self):
            _results = self.timeplot._GetFiles_Monthly(self._data_dir_schedule, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
            self.assertTrue(len(_results) > 0, "Expect non-empty _results=(%s)" % str(_results))
            sys.stderr.write(self._test_postfix)

    #   }}}

#   }}}


