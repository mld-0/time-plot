#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3:
#   }}}1
import re
import os
import logging
import pprint
import glob
import datetime
import dateutil.parser
from decimal import Decimal
from subprocess import Popen, PIPE, STDOUT
#   {{{2
logging.getLogger('matplotlib').setLevel(logging.WARNING)

_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

logging.getLogger('decaycalc').setLevel(logging.DEBUG)

class ScheduleReader(object):

    data_file_dir = os.environ.get('mld_logs_pulse')
    data_file_prefix = "Schedule.calc."
    data_file_postfix = ".vimgpg"

    col_datetimes = 3
    col_label = 0
    col_qty = 1
    col_delim = ','

    flag_assume_tz = True

    def _GPGDecryptFileToString(self, arg_path_file):
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

    def _Fix_DTS_DatetimeStr(self, arg_dt_str):
        #   {{{
        """If datetime string is in 'dts' format, '(2021-01-02)-(21-17-11)' or '(2021-01-02)-(2117-11)', transform to iso format '2021-01-02T21:17:11', otherwise return as-is"""
        regex_dts = r"\((\d{4}-\d{2}-\d{2})\)-\((\d{2})-?(\d{2})-?(\d{2})\)"
        _match_regex = re.match(regex_dts, arg_dt_str)
        if (_match_regex is not None):
            arg_dt_str = _match_regex.group(1) + "T" + _match_regex.group(2) + ":" + _match_regex.group(3) + ":" + _match_regex.group(4)
        return arg_dt_str
        #   }}}

    def GetMonthlyFilesList(self):
        #   {{{
        """Get list of monthly log files (denoted with YYYY-MM in name) contained in a given dir"""
        if not os.path.isdir(self.data_file_dir):
            raise Exception(f"not found, data_file_dir=({data_file_dir})")
        filematches_regex = self.data_file_prefix + "[0-9][0-9][0-9][0-9]-[0-9][0-9]" + self.data_file_postfix
        filematches_glob = os.path.join(self.data_file_dir, filematches_regex)
        _log.debug("filematches_glob=(%s)" % str(filematches_glob))
        filematches_list = glob.glob(filematches_glob)
        filematches_list.sort()
        _log.debug("filematches_list:\n%s" % (filematches_list))
        return filematches_list
        #   }}}
        

    def ReadItemData(self, schedule_label, schedule_files_list=None, is_gpg=True):
        """Read Schedule, either using monthly files found by GetMonthlyFilesList(), or those passed in schedule_files_list, and return list of datetimes and corresponding qtys for items matching schedule_label"""
        if (schedule_files_list is None):
            schedule_files_list = self.GetMonthlyFilesList()
        if (schedule_files_list is None) or (len(schedule_files_list) == 0):
            raise Exception(f"invalid schedule_files_list=({schedule_files_list})")

        _log.debug(f"schedule_label=({schedule_label})")

        results_datetime = []
        results_qty = []

        for loop_path in schedule_files_list:
            #   Read file to loop_filestr
            #   {{{
            loop_filestr = None
            if (is_gpg):
                loop_filestr = self._GPGDecryptFileToString(loop_path)
            else:
                with open(loop_path, "r") as f:
                    loop_filestr = f.read()
            #   }}}
            for loop_line in loop_filestr.split('\n'):
                if len(loop_line.strip()) == 0:
                    continue
                loop_line_split = loop_line.split(self.col_delim)
                if len(loop_line_split) <= 1:
                    _log.warning(f"len(loop_line_split)=({len(loop_line_split)}), loop_line_split=({loop_line_split}), loop_line=({loop_line})")
                    continue

                if (schedule_label is None) or (loop_line_split[self.col_label] == schedule_label):
                    loop_qty_str = loop_line_split[self.col_qty]
                    loop_qty = Decimal(loop_qty_str)
                    loop_datetime_str = loop_line_split[self.col_datetimes]
                    loop_datetime_str = self._Fix_DTS_DatetimeStr(loop_datetime_str)
                    #   TODO: 2021-03-12T17:08:57AEDT attempt parse with faster method first

                    loop_datetime = dateutil.parser.parse(loop_datetime_str)
                    #if (self.flag_assume_tz is True) and (loop_datetime.tzinfo is None):
                    #    loop_datetime = loop_datetime.replace(tzinfo = datetime.datetime.now().astimezone().tzinfo)

                    results_datetime.append(loop_datetime)
                    results_qty.append(loop_qty)

        if len(results_datetime) != len(results_qty):
            raise Exception(f"mismatch, len(results_datetime)=({len(results_datetime)}), len(results_qty)=({len(results_qty)})")

        _log.debug(f"len(results)=({len(results_qty)})")

        return results_datetime, results_qty



#   }}}1
