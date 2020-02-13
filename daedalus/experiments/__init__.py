#!/usr/bin/env python
"""
created 2/10/20 

@author DevXl

Implements Basic PsychoPhysics Experiment as a template
"""
from typing import Dict, List, AnyStr
from ..utils import errors
from psychopy import gui, data, core, monitors, visual, info, event, logging
from datetime import date
from psychopy.iohub.devices import Computer
from pathlib import PosixPath
import json
import csv
from math import isclose
import sys


class BaseExperiment:
    """
    Every experiment has the following components:
        - Subject
        - Display
        - Stimuli
        - Response
        - Configurations
        - Handler
        - Data
        - Logs
    """

    EXP_TYPE = "BASE"

    def __init__(self, path: PosixPath):
        self.home = PosixPath(path)
        self.subject: Dict = {}
        self.configuration: Dict = {}
        self.display: Dict = {}
        self.stimuli: Dict = {}
        self.response: Dict = {}
        self.handler: Dict = {}
        self.data: Dict = {}

        self.experiment_params: Dict = {}
        self.subject_init_params: Dict = {}
        self.subject_session_params: Dict = {}
        self.hardware_params: Dict = {}
        self.error_log: List[AnyStr] = []
        self.runtime_info: Dict = {}
        self.condition_file: PosixPath = PosixPath()
        self.config_file: PosixPath = PosixPath()
        self.stimuli = None
        self._date = data.getDateStr()

        self._load_initial_params()
        self._get_session_info()
        self.data_file = self._save_data()
        self.experiment_handler, self.trial_handler = self.generate_handler(self.condition_file)

    def _load_configs(self) -> Dict:
        """Parses the provided config files into the configurations dictionary"""
        config_file_types = ("json", "yaml", "csv")

        # files are usually located under "config" folder
        config_dir = self.home / "config"
        if config_dir.is_dir():
            config_files = list(f for f in self.config_dir.iterdir() if f.is_file())
        else:
            # sometimes they might not be there
            config_files = list(f for f in self.home.iterdir() if (f.is_file() and f.name.endswith(config_file_types)))

        # load the files and add them to the dict
        loaded_files = {
            "JSON": {},
            "CSV_paths": [],
            "YAML_paths": []
        }
        for _file in config_files:
            if _file.name.endswith(".json"):
                with open(_file, 'r') as json_file:
                    try:
                        this_json = json.load(json_file)
                        loaded_files["JSON"].update(this_json)
                    except Exception as err:
                        print(f"I couldn't open the JSON file {_file.name}.")
                        print(err)
            elif _file.name.endswith(".csv"):
                loaded_files["CSV_paths"].append(str(_file))
            elif _file.name.endswith(".yaml"):
                loaded_files["YAML_paths"].append(str(_file))
            else:
                raise FileNotFoundError("No parameter/configuration/condition file was found. I have to abort.")

        return loaded_files

    def _get_session_info(self) -> Dict:
        """Shows a GUI to get session info"""

        # construct the GUI's fields based on specified parameters in files
        params = self._load_configs()
        exp_params = params["JSON"]["EXPERIMENT"]
        subj_params = params["JSON"]["SUBJECT"]
        monitor_params = params["HARDWARE"]["Display"]

        # gui setup
        subject_dlg = gui.Dlg(title=exp_params["title"], labelButtonOK="Next")

        # subject info
        subject_dlg.addText("-----------------------------", color="Blue")
        subject_dlg.addText('|  Participant Information  |', color='Blue')
        subject_dlg.addText("-----------------------------", color="Blue")
        for key, val in subj_params:
            subject_dlg.addField(f"{key}:", val)

        # experiment info
        subject_dlg.addText("-----------------------------", color="Blue")
        subject_dlg.addText("|  Experiment Information   |", color="Blue")
        subject_dlg.addText("-----------------------------", color="Blue")
        subject_dlg.addField("Experimenter:", exp_params["users"])
        subject_dlg.addFixedField("Monitor:", monitor_params["name"])
        subject_dlg.addFixedField("Date:", date.today())
        subject_dlg.addFixedField('Version:', exp_params["version"])

        # checks
        subject_dlg.addText("-----------------------------", color="Red")
        subject_dlg.addText("|       Configuration        |", color="Red")
        subject_dlg.addText("-----------------------------", color="Red")
        subject_dlg.addField("SYSTEM_STATUS", True)
        subject_dlg.addField("INPUT_INFO", True)
        subject_dlg.addField("DEBUG_MODE", False)

        # show the dialogue
        session_info = subject_dlg.show()
        if subject_dlg.OK:

            # make gui to show requested check results or to warn the user
            warning_dlg = gui.Dlg(title="Check results", labelButtonOK="Start", labelButtonCancel="Abort and fix")

            # check input
            warning_dlg.addText("INPUT CHECKS")
            warning_dlg.addText("-----------------------------------")
            if session_info["INPUT_INFO"]:
                session_checks = self._check_user_input()
                if session_checks:
                    for e in session_checks:
                        warning_dlg.addText(f"FAILED: {e}", color="Red")
                else:
                    warning_dlg.addText("All checks have PASSED.", color="Green")
            else:
                warning_dlg.addText("I highly advise against running no checks on participant's information.",
                                    color="Red")

            # check system
            warning_dlg.addText("SYSTEM CHECKS")
            warning_dlg.addText("-----------------------------------")
            if session_info["SYSTEM_STATUS"]:
                system_checks = self._check_system()
                if system_checks:
                    for e in system_checks:
                        warning_dlg.addText(f"FAILED: {e}", color="Red")
                else:
                    warning_dlg.addText("All checks have PASSED.", color="Green")
            else:
                warning_dlg.addText("Only skip system checks if this is the 2nd+ time this script is running today.",
                                    color="Red")

            if session_info["Debug"]:
                warning_dlg.addText("DEBUG MODE ON", color="Red")

            warning_dlg.show()
            if warning_dlg.OK:
                checks_log = 

        else:
            print("User Abort.")
            self._close()

    # Getters and Setters
    @property
    def subject(self) -> Dict:
        return self.subject

    @subject.setter
    def subject(self, val: Dict):
        self.subject = val








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

