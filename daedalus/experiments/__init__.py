#!/usr/bin/env python
"""
created 2/10/20 

@author DevXl

DESCRIPTION
"""
from ..utils import errors
from psychopy import gui, data, core, monitors, visual, info, event
from psychopy.iohub.devices import Computer
from pathlib import Path
import json
import csv
import abc
from math import isclose
import sys


class BaseExperiment:

    EXP_TYPE = "BASE"

    def __init__(self, path):
        self.home = Path(path)
        self.experiment_params = dict()
        self.subject_init_params = dict()
        self.subject_session_params = dict()
        self.hardware_params = dict()
        self.error_log = list()
        self._window = None
        self._monitor = None
        self._stimuli = None
        self._handler = None

        self._load_initial_params()

    @abc.abstractmethod
    def run(self):
        """All experiment code should go here"""

    @staticmethod
    def calibrate_monitors(mons):
        pass

    @staticmethod
    def calculate_duration(conditions):
        pass

    def force_quit(self):

        if 'escape' in event.getKeys():
            self._save_data()
            self._close()

    def _generate_stimuli(self):
        pass

    def _save_data(self):
        pass

    def _generate_window(self, this_session_params):

        _monitor_name = this_session_params.get("Monitor", None)
        if _monitor_name not in monitors.getAllMonitors():
            self.calibrate_monitors(self.hardware_params.get("monitors", False).get(_monitor_name, False))

        self._monitor = monitors.Monitor(name=_monitor_name)
        self._window = visual.Window(fullscr=True, monitor=self._monitor)

    def _get_session_info(self):

        _config_dlg = gui.Dlg(title=self.experiment_params.get("name", "New Participant"),
                             labelButtonOK="Validate")
        _config_dlg.addText('Participant\'s Information', color='Blue')
        for key, val in self.subject_init_params.items():
            _config_dlg.addField(f"{key}:", val)

        _config_dlg.addText("Configuration", color="Blue")
        _config_dlg.addField("Monitor:", [m for m in self.hardware_params.get("monitors", None)])
        _config_dlg.addFixedField("Date:", data.getDateStr())
        _config_dlg.addFixedField('Version:', [v for v in self.experiment_params.get("ver", 0)])
        _config_dlg.addField("Debug:", False)
        _session_params = _config_dlg.show()

        if _config_dlg.OK:
            self._generate_window(_session_params)

            if _session_params.get("Debug", True):
                raise UserWarning("Running in DEBUG mode. No checks are performed.")
            else:
                self._check_info_input()
                self._check_system()
        else:
            print("User Abort.")
            self._close()

    def _load_initial_params(self):

        _files = list(f.name for f in self.home.iterdir() if f.is_file())
        _dirs = list(d for d in self.home.iterdir() if d.is_dir())
        self.data_dir = self.home / "data"

        for param_file in _files:
            try:
                with open(param_file, 'r') as json_file:
                    try:
                        this_params = json.load(json_file)
                        if param_file.startswith("subj"):
                            self.subject_init_params = this_params
                        elif param_file.startswith("exp"):
                            self.experiment_params = this_params
                        elif param_file.startswith("hardware"):
                            self.hardware_params = this_params
                        else:
                            self.error_log.append(param_file)
                            raise RuntimeWarning(f"{param_file} is not defined for {self.EXP_TYPE} experiments.")
                    except TypeError:
                        self.error_log.append(param_file)
                        raise RuntimeWarning(f"{param_file} is not a valid JSON file.")

            except OSError:
                self.error_log.append(param_file)
                raise RuntimeWarning(f"I cant open the {param_file} file.")

        if not self.data_dir.is_dir():
            try:
                self.data_dir.mkdir()
            except PermissionError:
                raise Exception(errors.permission_msg("data", 'directory'))

    def _check_info_input(self):

        for key, val in self.subject_session_params:
            if (key in self.subject_init_params.keys()) and (not isinstance(val, list)):
                if not isinstance(val, type(self.subject_init_params[key])):
                    raise ValueError(f"{key} parameter should be "
                                     f"{type(self.subject_init_params[key])} not {type(val)}")

        self.all_subjects_log = self.data_dir / "subjLog.csv"

        try:
            with open(self.all_subjects_log, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)

                for row in csv_reader:
                    if (row["ID"] == self.subject_init_params["Initials"]) and (row["ID"] not in ["name", "test"]):
                        _missingSessions = list(set(range(max(row["sessions"]) + 1)) - set(row["sessions"]))
                        _conflictSession = self.subject_session_params["Session"] in row["sessions"]

                        if len(_missingSessions):
                            raise ValueError(f"This subject has not participated in the "
                                             f"{_missingSessions} sessions.")
                        if _conflictSession:
                            raise ValueError(f"This subject has already participated in session"
                                             f"{self.subject_init_params['Session']}")
        except FileNotFoundError:
            try:
                self.all_subjects_log.touch()
                with open(self.all_subjects_log, 'w') as csv_file:
                    csv_writer = csv.writer(csv_file, delimeter=",")
                    csv_writer.writerow(["ID", "sessions"])
                    csv_writer.writerow([self.subject_init_params["Initials"], [0]])
            except PermissionError:
                raise Exception(errors.permission_msg("All Subjects' Log", 'file'))
        except OSError:
            raise Exception(f"{self.all_subjects_log.name} is not a valid CSV file")

    def _check_system(self, thresh=0.20):

        _run_info = info.RunTimeInfo(author=self.experiment_params.get("author", None),
                                    version=self.experiment_params.get("ver", 0),
                                    win=self._window,
                                    refreshTest=True,
                                    userProcsDetailed=True,
                                    verbose=True)
        self._window.close()

        if _run_info["windowRefreshTimeSD_ms"] > thresh:
            raise RuntimeWarning(f"Monitor has high refresh rate variability: "
                                 f"{_run_info['windowRefreshTimeSD_ms']}")

        if not isclose(self.subject_session_params.get("monitor", None).get("refresh", 0), _run_info["rate"]):
            raise RuntimeWarning(f"Monitor shows {_run_info['rate']} per second which is not the desired refresh rate.")

        if _run_info["systemMemFreeRAM"] < 1000:
            raise RuntimeWarning(f"Not enough available RAM: "
                                 f"{round(_run_info['systemMemFreeRAM'] / 1000)} GB is available.")

        _priority = Computer.getPriority()
        try:
            Computer.setPriority("realtime", disable_gc=True)
        except BaseException as e:
            raise RuntimeWarning(f"I could not raise the priority from {_priority.upper()} to REALTIME.")

        if _run_info["systemUserProcFlagged"]:
            for proc in _run_info["systemUserProcFlagged"]:
                raise ResourceWarning(f"Process with ID {proc[1]} is flagged. "
                                      f"Close the {proc[0]} application.")

    def _close(self):
        """Close the experiment runtime."""
        self._window.clos()
        core.quit()
        sys.exit()

