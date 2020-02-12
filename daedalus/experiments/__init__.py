#!/usr/bin/env python
"""
created 2/10/20 

@author DevXl

Implements Basic PsychoPhysics Experiment as a template
"""
from typing import Dict, List, AnyStr
from ..utils import errors
from psychopy import gui, data, core, monitors, visual, info, event
from psychopy.iohub.devices import Computer
from pathlib import PosixPath
import json
import csv
from math import isclose
import sys


class BaseExperiment:

    EXP_TYPE = "BASIC"

    def __init__(self, path: PosixPath):
        self.home = PosixPath(path)
        self.experiment_params: Dict = {}
        self.subject_init_params: Dict = {}
        self.subject_session_params: Dict = {}
        self.hardware_params: Dict = {}
        self.error_log: List[AnyStr] = []
        self.runtime_info: Dict = {}
        self.condition_file: PosixPath = PosixPath()
        self.config_file: PosixPath = PosixPath()
        self.stimuli: Dict[AnyStr, visual] = {}
        self._date = data.getDateStr()

        self._load_initial_params()
        self._get_session_info()
        self.data_file = self._save_data()
        self.experiment_handler, self.trial_handler = self.generate_handler(self.condition_file)

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
    
    def generate_handler(self, condition_file):
        
        _conditions = data.importConditions(condition_file)
        _trial_handler = data.TrialHandler(trialList=_conditions,
                                           nReps=self.experiment_params.get("n_reps", 1),
                                           method="fullRandom",
                                           extraInfo=self.subject_session_params,
                                           originPath=-1,
                                           name="Trial Handler")
        _experiment_handler = data.ExperimentHandler(
            name=self.experiment_params.get("name", "ExperimentHandler"),
            version=self.experiment_params.get("ver", 0),
            runtimeInfo=self.runtime_info,
            extraInfo=self.experiment_params,
            savePickle=False,
            saveWideText=True,
            dataFileName=self.data_file
        )
        
        return _experiment_handler, _trial_handler

    @property
    def stimuli(self):
        return self.stimuli

    @stimuli.setter
    def stimuli(self, val):
        self.stimuli = val

    def _save_data(self):
        
        _data_file = self.data_dir / self.subject_session_params["Initials"] / f"session{self.subject_session_params['Session']}_{self._date}.csv"
        return _data_file

    def generate_window(self, params):

        _monitor_name = params.get("Monitor", None)
        if _monitor_name not in monitors.getAllMonitors():
            self.calibrate_monitors(self.hardware_params.get("monitors", False).get(_monitor_name, False))

        this_monitor = monitors.Monitor(name=_monitor_name)
        this_window = visual.Window(fullscr=True, monitor=self._monitor)
        this_window.recordFrameIntervals = True
        
        return this_monitor, this_window
    
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
            
            self._monitor, self._window = self.generate_window(_session_params)

            if _session_params.get("Debug", True):
                raise UserWarning("Running in DEBUG mode. No checks are performed.")
            else:
                self._check_info_input()
                self._check_system()
        else:
            print("User Abort.")
            self._close()

    def _load_initial_params(self):
        
        self.data_dir = self.home / "data"
        self.config_dir = self.home / "config"

        _files = list(f for f in self.config_dir.iterdir() if f.is_file())
        _dirs = list(d for d in self.home.iterdir() if d.is_dir())

        for param_file in _files:
            
            try:
                if param_file.name.endswith(".json"):
                    with open(param_file, 'r') as json_file:
                        try:
                            this_json = json.load(json_file)
                            
                            if param_file.name.startswith("subj"):
                                self.subject_init_params = this_json
                            elif param_file.name.startswith("exp"):
                                self.experiment_params = this_json
                            elif param_file.name.startswith("hardware"):
                                self.hardware_params = this_json
                            else:
                                self.error_log.append(param_file)
                                raise RuntimeWarning(f"{param_file.name} is not defined for {self.EXP_TYPE} experiments.")
                        except TypeError:
                            self.error_log.append(param_file)
                            raise RuntimeWarning(f"{param_file.name} is not a valid JSON file.")
                    
                elif param_file.name.endswith(".csv"):
                    self.condition_file = param_file

                elif param_file.name.endswith(".yaml"):
                    self.config_file = param_file
                    
                else:
                    raise FileNotFoundError("No parameter/configuration/condition file was found!")

            except OSError:
                self.error_log.append(param_file)
                raise RuntimeWarning(f"I cant open the {param_file.name} file.")

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
                
        self.runtime_info = _run_info

    def _close(self):
        """Close the experiment runtime."""
        self._window.clos()
        core.quit()
        sys.exit(1)

