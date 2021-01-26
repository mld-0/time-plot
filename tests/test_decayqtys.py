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
from timeplot.plotdassresults import PlotDassResults
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
    _flag_openPlots = True

    _tasklog_dir = os.path.join(os.environ.get('mld_tasklogs'), "_worklog")

    _dassresults_dir = os.environ.get('mld_dass21_results')

    _pkg_testdata = "tests.data"
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

    _dass_prefix = "dass21-results."
    _dass_postfix = ".vimgpg"

    #   Continue: 2021-01-09T18:10:29AEDT test_AnalyseDataAll
    #   Continue: 2021-01-09T18:12:37AEDT get starttime/timedone from tasklogs, plot alongside data from schedule log file


    def test_PlotDecayQtys_HelloWorld(self):
        plotdecayqtys = PlotDecayQtys()

    def test_PlotDaysPerWeek_DecayQtys_ForDateRange(self):
        dt_start = dateparser.parse("2020-11-10T18:18:31AEDT")
        dt_end = dateparser.parse("2021-01-18T18:18:52AEDT")
        plotdecayqtys = PlotDecayQtys()
        plotdecayqtys.data_file_dir = self._data_dir_schedule
        plotdecayqtys.data_file_prefix = self.prefix
        plotdecayqtys.data_file_postfix = self.postfix
        plotdecayqtys.plot_save_dir = self._output_dir
        plotdecayqtys.PlotDaysPerWeek_DecayQtys_ForDateRange(dt_start, dt_end)
        if (self._flag_openPlots):
            webbrowser.open('file:%s' % self._output_dir)

    if (False):
        def test_PlotDecayQtys_PlotDaily_DecayQtys_ForDateRange_singleday(self):
            dt_start = dateparser.parse("2021-01-17T18:18:31AEDT")
            dt_end = dateparser.parse("2021-01-17T18:18:52AEDT")
            plotdecayqtys = PlotDecayQtys()
            plotdecayqtys.data_file_dir = self._data_dir_schedule
            plotdecayqtys.data_file_prefix = self.prefix
            plotdecayqtys.data_file_postfix = self.postfix
            plotdecayqtys.plot_save_dir = self._output_dir
            plotdecayqtys.PlotDaily_DecayQtys_ForDateRange(dt_start, dt_end)
            if (self._flag_openPlots):
                webbrowser.open('file:%s' % self._output_dir)
        def test_PlotDecayQtys_PlotDaily_DecayQtys_ForDateRange(self):
            dt_start = dateparser.parse("2021-01-07T18:18:31AEDT")
            dt_end = dateparser.parse("2021-01-18T18:18:52AEDT")
            plotdecayqtys = PlotDecayQtys()
            plotdecayqtys.data_file_dir = self._data_dir_schedule
            plotdecayqtys.data_file_prefix = self.prefix
            plotdecayqtys.data_file_postfix = self.postfix
            plotdecayqtys.plot_save_dir = self._output_dir
            plotdecayqtys.PlotDaily_DecayQtys_ForDateRange(dt_start, dt_end)
            if (self._flag_openPlots):
                webbrowser.open('file:%s' % self._output_dir)

#   }}}

