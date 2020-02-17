#!/usr/bin/env python
"""
created 2/10/20 

@author DevXl

Implements Basic PsychoPhysics Experiment as a template
"""
from typing import Dict, List, Literal, Union, TypeVar
from abc import abstractmethod
from ..utils import errors
from psychopy import gui, data, core, monitors, visual, info, event, logging
from datetime import date
from psychopy.iohub.devices import Computer
from pathlib import PosixPath
import json
import pandas as pd
from math import isclose
import sys
import uuid


class BaseExperiment:
    """
    Every experiment has the following components:
        - Session
        - Display
        - Stimuli
        - Response
        - Configurations
        - Handler
        - Data
        - Logs
    """

    EXP_TYPE = "BASIC"

    def __init__(self, path: str, name: str):

        self.NAME = name
        self.HOME_DIR = PosixPath(path)
        self.DATA_DIR = self.HOME_DIR / "data"

        self.session_config: Dict = {}
        self.exp_config: Dict = {}
        self.display_config: Dict = {}
        self.metadata: Dict = {}
        self.stimuli: Dict = {}
        self.response: Dict = {}
        self.handler: Dict = {}
        self.data: Dict = {}
        self.logs: Dict = {}

        _init_params = self._load_configs()
        self.exp_config = _init_params["JSON"]["EXPERIMENT"]
        self.display_config = _init_params["JSON"]["HARDWARE"]["Display"]
        self.session_config = _init_params["JSON"]["SUBJECT"]

    def initialize_experiment(self):
        """First run initialization"""

        logging.console.setLevel(logging.DEBUG)
        init_log_file = self.HOME_DIR / "init_log.log"
        init_log = logging.LogFile(init_log_file, filemode="w", level=logging.DEBUG)

        # directories


    def load_experiment_metadata(self) -> Union[pd.DataFrame, None]:
        """Loads information about participants"""

        experiment_metadata = None

        # experiment metadata will be in a csv file under exp home folder
        meta_file = self.HOME_DIR / f"{self.NAME}_metadata.csv"
        if meta_file.is_file():
            try:
                experiment_metadata = pd.read_csv(meta_file)
            except Exception as err:
                print("I can't open the experiment metadata file.")
                print(err)
        else:
            try:
                meta_file.touch()  # make an empty file if it's not there
                # TODO: headers
            except Exception as err:
                print("I can't create the experiment metadata file.")
                print(err)

        return experiment_metadata

    def load_subjects_metadata(self) -> Union[pd.DataFrame, None]:
        """Loads information about a single subject"""

        subjects_metadata = None
        # subject metadata will be a csv file in subject's data folder
        meta_file = self.HOME_DIR / "data" / "subjects_metadata.csv"  # TODO: don't hardcode
        if meta_file.is_file():
            try:
                subjects_metadata = pd.read_csv(meta_file)
            except Exception as err:
                print("I can't open subjects metadata file.")
                print(err)
        else:
            print("I didn't find a metadata file. Is this the first time this experiment is running?")

        return subjects_metadata

    def add_subject_metadata(self, new_subject: bool, subject_initials: str):

        meta_file = self.DATA_DIR / "subjcets_metadata.csv"  # TODO: don't hardcode

        rand_id = uuid.uuid4().hex[:4]
        meta_df = pd.DataFrame({
            'subject': subject_initials,
            'ID': rand_id,
            self.exp_config["EXPERIMENT"]["conditions"]["parts"].values()[0]: False
        })
        try:
            meta_df.to_csv(meta_file, index=False)
        except Exception as err:
            print("I can't write subjects metadata file.")
            print(err)

    def _load_configs(self) -> Dict:
        """Parses the provided config files (located under config/) into the configurations dictionary"""

        # files are usually located under "config" folder
        config_dir = self.HOME_DIR / "config"
        if config_dir.is_dir():
            config_files = list(f for f in self.config_dir.iterdir() if f.is_file())
        else:
            raise FileNotFoundError(f"I didn't find the config folder under {self.HOME_DIR}")  # TODO: add open file

        # load the files and add them to the dict
        loaded_files = {
            "JSON": {},
            "CSV_paths": [],
            "YAML_paths": []
        }
        for _file in config_files:
            if _file.name.endswith(".json"):
                try:
                    with open(_file, 'r') as json_file:
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
                raise FileNotFoundError("No parameter/configuration/condition file found. I have to abort.")

        return loaded_files

    def _get_session_info(self) -> List[str]:
        """Shows GUIs to get session info"""

        # load subjects
        _metadata = self.load_subjects_metadata()

        # choose subject dialogue
        choose_subj_dlg = gui.Dlg(title=self.NAME, labelButtonOK="Next", labelButtonCancel="New Participant")
        choose_subj_dlg.addText("Choose a participant", color="Blue")
        choose_subj_dlg.addField("Initials:", choices=list(_metadata.subject))

        # new subject dialogue
        new_subj_dlg = gui.Dlg(title="Participant Information", labelButtonOK="Next", labelButtonCancel="Cancel")


        # loaded subject dialogue
        _initials = ""
        _subj_df = _metadata.loc[_metadata.INITIALS == _initials, ]
        loaded_subj_dlg = gui.Dlg(title="Participant Information", labelButtonOK="Next", labelButtonCancel="Cancel")
        for key, val in self.session_config:
            if key in _subj_df.columns:
                loaded_subj_dlg.addFixedField(key, _subj_df[key].values[0])
        loaded_subj_dlg.addFixedField("Initials:", _initials)
        loaded_subj_dlg.addFixedField("ID:", _subj_df["ID"].values[0])
        loaded_subj_dlg.addFixedFiled("Session:", _subj_df["NEXT_PART"].values[0])

        # construct the GUI's fields based on specified parameters in files
        init_params = self._load_configs()
        init_exp_params = init_params["JSON"]["EXPERIMENT"]
        init_subj_params = init_params["JSON"]["SUBJECT"]
        init_hardware_params = init_params["JSON"]["HARDWARE"]

        # gui setup
        session_dlg = gui.Dlg(title=init_exp_params["title"], labelButtonOK="Next")

        # subject info
        session_dlg.addText("-----------------------------", color="Blue")
        session_dlg.addText('|  Participant Information  |', color='Blue')
        session_dlg.addText("-----------------------------", color="Blue")
        for key, val in init_subj_params:
            session_dlg.addField(f"{key}:", val)

        # devices info
        session_dlg.addText("-----------------------------", color="Blue")
        session_dlg.addText("|    Device Information     |", color="Blue")
        session_dlg.addText("-----------------------------", color="Blue")
        for _device, _types in init_hardware_params:
            session_dlg.addField(f"{_device}:", [d["name"] for d in _types])

        # experiment info
        session_dlg.addText("-----------------------------", color="Blue")
        session_dlg.addText("|  Experiment Information   |", color="Blue")
        session_dlg.addText("-----------------------------", color="Blue")
        session_dlg.addFixedField("Title:", init_exp_params["title"])
        session_dlg.addField("Experimenter:", init_exp_params["users"])
        session_dlg.addFixedField("Date:", date.today())
        session_dlg.addFixedField('Version:', init_exp_params["version"])

        # checks
        session_dlg.addText("-----------------------------", color="Red")
        session_dlg.addText("|       Configuration        |", color="Red")
        session_dlg.addText("-----------------------------", color="Red")
        session_dlg.addField("CHECK_SYSTEM_STATUS", True)
        session_dlg.addField("CHECK_SUBJECT", True)
        session_dlg.addField("CHECK_DEVICES", True)
        session_dlg.addField("DEBUG_MODE", False)

        # show the dialogue
        session_info = session_dlg.show()
        if session_dlg.OK:

            # separate info dict
            for key in init_subj_params.keys():
                self.session_config["SUBJECT"][key] = session_info[key]

            for key in init_hardware_params.keys():
                self.session_config["HARDWARE"][key] = session_info[key]

            self.session_config["EXPERIMENT"]["Experimenter"] = session_info["Experimenter"]
            self.session_config["EXPERIMENT"]["Date"] = session_info["Date"]
            self.session_config["EXPERIMENT"]["Version"] = session_info["Version"]

            # run the checks
            if session_info["CHECK_SUBJECT"]:
                _subject_check_results = self._validate_subject(init_subj_params)
            if session_info["CHECK_SYSTEM_STATUS"]:
                _sys_check_results = self._validate_sys_status()
            if session_info["CHECK_DEVICES"]:
                _devices_check_results = self._validate_devices()

            # get the report
            warning_dlg = self._report_check_results([
                _subject_check_results,
                _sys_check_results,
                _devices_check_results
            ])

            # add info about debug
            if session_info["Debug"]:
                warning_dlg.addText("*******DEBUG MODE ON*******", color="Blue")

            # show the results and ask for response
            warning_dlg.show()
            if warning_dlg.OK:
                # TODO
                pass
            else:
                print("User Abort.")
                self._close()
        else:
            print("User Abort.")
            self._close()

    def _validate_subject(self, init_params: Dict[str, Union[str, int]]) -> List[List]:
        """Checks for the type of input and history of this subject"""

        check_results = []

        # validate input type
        for key, val in self.session_config["SUBJECT"]:
            if (key in init_params.keys()) and (not isinstance(val, list)):
                if not isinstance(val, type(init_params[key])):
                    check_results.append(f"{key} parameter should be "
                                         f"{type(self.subject_init_params[key])} not {type(val)}")

        # validate subject history
        self.data["DIR"] = self.HOME_DIR / "data"
        if DATA_DIR.is_dir:

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

    def _report_checks(self, check_subject: bool, check_system: bool, check_devices: bool) -> None:
        """shows a gui to the user to let them know the errors that occurred/didn't"""

        # make the gui
        warning_dlg = gui.Dlg(title="Check results", labelButtonOK="Start", labelButtonCancel="Abort and fix")

        # messages
        _input_msg = ["INPUT CHECKS", "-----------------------------------"]
        _system_msg = ["SYSTEM CHECKS", "-----------------------------------"]
        _devices_msg = ["DEVICE CHECKS", "-----------------------------------"]

        # check results
        for _chk in [check_subject, check_system, check_devices]:
            if _chk:

        # check input
        warning_dlg.addText("INPUT CHECKS")
        warning_dlg.addText("-----------------------------------")
        if check_subject:
            _subject_checks = self._check_user_input()
            if _subject_checks:
                for e in _subject_checks:
                    warning_dlg.addText(f"FAILED => {e}", color="Red")
            else:
                warning_dlg.addText("All checks have PASSED.", color="Green")
        else:
            warning_dlg.addText("I highly advise against running no checks on participant's information.",
                                color="Red")

        # check system
        warning_dlg.addText("SYSTEM CHECKS")
        warning_dlg.addText("-----------------------------------")
        if check_system:
            _system_checks = self._check_system()
            if _system_checks:
                for e in _system_checks:
                    warning_dlg.addText(f"FAILED => {e}", color="Red")
            else:
                warning_dlg.addText("All checks have PASSED.", color="Green")
        else:
            warning_dlg.addText("Only skip system checks if this is the 2nd+ time this script is running today.",
                                color="Red")

        warning_dlg.addText("DEVICE CHECKS")
        warning_dlg.addText("-----------------------------------")
        if check_devices:
            _device_checks = self._check_devices()
            if _device_checks:
                for e in _device_checks:
                    warning_dlg.addText(f"FAILED => {e}", color="Red")
            else:
                warning_dlg.addText("All checks have PASSED.", color="Green")
        else:
            warning_dlg.addText("NO DEVICE DATA WILL BE RECORDED.\n"
                                "ABORT AND CHECK DEVICE STATUS AND CONNECTIONS.",
                                color="Red")

        self.logs["startup_checks"] =

        return warning_dlg,

    @abstractmethod
    def _check_devices(self):
        """Should be implemented to check connected devices
        based on each type of experiment (eye tracker, eeg, etc.)"""

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


    def _close(self):
        """Close the experiment runtime."""
        self._window.clos()
        core.quit()
        sys.exit(1)

