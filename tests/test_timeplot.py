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
from decaycalc.decaycalc import DecayCalc
from timeplot.timeplot import TimePlot
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

    _data_dir = os.environ.get('mld_logs_schedule')
    _output_dir = os.path.join(tempfile.gettempdir(), "test-decaycalc")

    _test_postfix = "\n"

    if not os.path.isdir(_output_dir):
        _log.debug("mkdir _output_dir=(%s)" % str(_output_dir))
        os.mkdir(_output_dir)

    prefix = "Schedule.calc."
    postfix = ".vimgpg"

    #day_analyse = dateparser.parse("2021-01-04T00:00:00AEST")
    day_analyse = dateparser.parse("2021-01-03")

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

    def test_GetDatetimesFirstAndLast_FromFileList(self):
        located_filepaths = self.timeplot._GetAvailableFiles_Monthly(self._data_dir, self.prefix, self.postfix)
        dt_first, dt_last = self.timeplot._GetDatetimesFirstAndLast_FromFileList(located_filepaths, self.col_dt, self.delim)

    def test_GetAvailableFiles_Monthly(self):
        located_filepaths = self.timeplot._GetAvailableFiles_Monthly(self._data_dir, self.prefix, self.postfix)

    def test_CalculateRangeForDay(self):
        located_filepaths = self.timeplot._GetFiles_Monthly(self._data_dir, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
        results_dt, results_qty = self.timeplot._ReadData(located_filepaths, self.label, self.col_dt, self.col_qty, self.col_label, self.delim)
        _result_dt_list, _result_qty_list = self.decaycalc.CalculateRangeForDay(self.day_analyse, results_dt, results_qty, self.halflife, self.onset)
        _output_fname = self.day_analyse.strftime("%Y-%m-%d")
        self.timeplot._PlotResultsForDay(_result_dt_list, _result_qty_list, self._output_dir, _output_fname, True)
        if (self._flag_openPlots):
            webbrowser.open('file:%s' % self._output_dir)

    def test_GetFiles_Monthly(self):
        _results = self.timeplot._GetFiles_Monthly(self._data_dir, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
        self.assertTrue(len(_results) > 0, "Expect non-empty _results=(%s)" % str(_results))
        sys.stderr.write(self._test_postfix)

    def test_ReadData(self):
        located_filepaths = self.timeplot._GetFiles_Monthly(self._data_dir, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
        results_dt, results_qty = self.timeplot._ReadData(located_filepaths, self.label, self.col_dt, self.col_qty, self.col_label, self.delim)
        self.assertTrue(len(results_dt) > 0, "Expect non-empty results=(%s)" % results_dt)
        sys.stderr.write(self._test_postfix)

    def test_CalculateAtDT(self):
        located_filepaths = self.timeplot._GetFiles_Monthly(self._data_dir, self.prefix, self.postfix, self.dt_start, self.dt_end, True)
        results_dt, results_qty = self.timeplot._ReadData(located_filepaths, self.label, self.col_dt, self.col_qty, self.col_label, self.delim)
        remaining_qty = self.decaycalc.CalculateAtDT(self.dt_analyse, results_dt, results_qty, self.halflife, self.onset)
        sys.stderr.write(self._test_postfix)

#   }}}


