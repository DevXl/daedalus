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
        self.DATE = date.today()
        self.LOG =
        self.DIRS = {
            "DATA": self.HOME_DIR / "data",
            "CONFIG": self.HOME_DIR / "config",
            "LOG": self.HOME_DIR / "log"
        }
        self.FILES = {
            "EXP_META": self.HOME_DIR / "experiment_metadata.tsv",
            "SUBJ_META": self.HOME_DIR / "data" / "subjects_metadata.tsv",
            "EXP_PARAMS": self.HOME_DIR / "config" / "experiment_parameters.json",
            "SUBJ_PARAMS": self.HOME_DIR / "config" / "subjects_parameters.json"
        }
        self.PARAMS = {
            "EXP": {},
            "SUBJ": {},
            "HARDWARE": {}
        }
        self.DATA = {
            "exp": {
                "meta": {},
                "session": {}
            },
            "subj": {
                "meta": {},
                "session": {}
            }
        }

        self.session_config: Dict = {}
        self.exp_config: Dict = {}
        self.display_config: Dict = {}
        self.metadata: Dict = {}
        self.stimuli: Dict = {}
        self.response: Dict = {}
        self.handler: Dict = {}
        self.data: Dict = {}
        self.logs: Dict = {}


    def initialize_experiment(self):
        """First run initialization"""

        logging.console.setLevel(logging.DEBUG)
        init_log_file = self.HOME_DIR / "init_log.log"
        init_log = logging.LogFile(init_log_file, filemode="w", level=logging.DEBUG)

        # data directory
        init_log.write("Load\n----------------------------------------------------------------------------------")
        if not self.DIRS["DATA"].is_dir():
            try:
                self.DIRS["DATA"].mkdir()
            except Exception as e:
                logging.error(f"Could not create the data directory because: {e}")

        # log directory
        if not self.DIRS["LOG"].is_dir():
            try:
                self.DIRS["LOG"].mkdir()
            except Exception as e:
                logging.error(f"Could not create the log directory because: {e}")

        # files
        for _file in self.FILES.values():
            if not _file.is_file():
                logging.error(f"{_file} file not found.")

        # read experiment params
        try:
            with self.FILES["EXP_PARAMS"].open() as p:
                self.PARAMS["EXP"] = json.loads(p)
        except Exception as e:
            logging.error(f"Could not open experiment parameters file because: {e}")

        # read subject params
        try:
            with self.FILES["SUBJ_PARAMS"].open() as p:
                self.PARAMS["SUBJ"] = json.loads(p)
        except Exception as e:
            logging.error(f"I could not open the subjects' parameters file because: {e}")

        # subjects metadata
        num_required_subjects = len(self.PARAMS["EXP"]["n_required"])
        subj_meta_dict = {
            "subject": [f"subj-{s:02}" for s in range(num_required_subjects)],
            "id": [uuid.uuid4().hex[:4] for _ in range(num_required_subjects)],
            "initials": [],
            "age": [],
            "handedness": [],
            "gender": [],
            "vision": [],
            "sessions_done": [],
            "sessions_tbr": [part for part in self.PARAMS["EXP"]["conditions"]["parts"]]
        }

        subj_meta_df = pd.DataFrame(subj_meta_dict)
        subj_meta_df.to_csv(self.FILES["SUBJ_META"], sep="\t",index=False)

        # subject directories
        for _subj in range(num_required_subjects):
            _path = self.DIRS["DATA"] / f"sub-{_subj:02}"
            _path.mkdir()

        # experiment metadata
        exp_meta_dict = {
            "title": self.PARAMS["EXP"]["info"]["title"],
            "version": self.PARAMS["EXP"]["info"]["version"],
            "run": [0],
            "date": date.today(),
            "logFile": str(init_log_file.relative_to(self.HOME_DIR)),
            "subject": []
        }

        exp_meta_df = pd.DataFrame(exp_meta_dict)
        exp_meta_df.to_csv(self.FILES["EXP_META"], sep="\t", index=False)

        # initial system check
        sys_results = self._check_system()
        init_log.write("SYSTEM\n----------------------------------------------------------------------------------")
        for r in sys_results:
            logging.warning(r)

        # initial devices check
        device_results = self._check_devices()
        init_log.write("DEVICES\n---------------------------------------------------------------------------------")
        for r in device_results:
            logging.warning(r)

    def register_subject(self):
        """
        Show a gui to enter new subject's information
        """
        new_subj_info = {}

        new_subj_dlg = gui.Dlg(title="New Participant Information", labelButtonOK="Next", labelButtonCancel="Cancel")
        new_subj_dlg.addField("Student ID:")
        new_subj_dlg.addField("Initials:", tip="lowercase separated by . (e.g. k.m.z)")
        new_subj_dlg.addField("Age:", choices=list(range(17, 51)))
        new_subj_dlg.addField("Gender:", ["Male", "Female", "NB"])
        new_subj_dlg.addField("Handedness:", ["Left", "Right"])
        new_subj_dlg.addFixedField("Registration Date:", self.DATE)
        new_subj_dlg.addFixedField("Registration Experiment:", self.NAME)

        user_info = new_subj_dlg.show()
        if new_subj_dlg.OK:

            # add the input data to the subject dictionary to write to file later
            new_subj_info["ID"] = uuid.uuid4().hex[:8]  # generate random ID
            new_subj_info["sID"] = user_info[0]
            new_subj_info["initials"] = user_info[1]
            new_subj_info["age"] = user_info[2]
            new_subj_info["gender"] = user_info[3][0]
            new_subj_info['hand'] = user_info[4]
            new_subj_info['date_created'] = str(user_info[5])
            new_subj_info['exp'] = user_info[5]

        else:






    def load_subject(self):
        pass

    def load_subject_database(self):
        pass

    def add_to_subject_database(self):
        pass


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

