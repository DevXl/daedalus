#!/usr/bin/env python
"""
created 07/22/20
​
@author DevXI and Maria Mora
​
Implements Basic PsychoPhysics Experiment as a template
"""
from psychopy import gui, data, core, monitors, info, logging, visual, event
from psychopy.iohub.devices import Computer
from pathlib import Path
# import logging
import json
import sys
import abc
import platform
from typing import Dict, List
from daedalus.utils.misc import jitter, get_screens


class BaseExperiment:
    """
    Template of experiments with basic functionality.
    Mostly deals with setting up primitive objects and settings like subject info, system checks, logging, etc.

    Basically every experiment needs the following attributes/functionalities:
        - Path to Home and other directories.
        - Experimental or debug MODE.
        - Settings that are specific to the experiment (metadata, conditions, etc.). An example of this can be found
            in docs/examples. This file should live under config/ directory of the experiment.
        - Parameters are data about the subject and are collected from input gui and boxes.
        - A monitor and a window that is made from that monitor.
        - Keeping track of timings.
        - Initiate flow via handlers.
        - Feedback, logs, and warnings.

    Parameters
    ----------
    title : str
        Experiment's name.

    debug : bool
        For development use. If set to True bypasses many repetitive stages.
    """

    def __init__(self, title: str, debug: bool) -> None:

        self.NAME = title
        self.MODE = debug

        self.HOME_DIR = Path('.').resolve()

        # TODO: show a dialogue to select participant
        # TODO: experiment selection gui
        # TODO: move from json to YAML to add comment to settings and other files
        self._settings = None
        self._parameters = dict()
        self._monitor = None
        self._window = None
        self._data_paths = dict()
        self._timing = dict()
        self._handlers = dict()
        self.warnings = {
            "Files": [],
            "System": []
        }

        self.startup()

    @property
    def settings(self) -> Dict:
        """
        Read the settings file provided on config/settings.json.

        Returns
        -------
        dictionary of settings indicated by the experimenter.
        """

        # to avoid running the script everytime we access settings
        if self._settings is None:

            # find the default settings file
            _filepath = ""
            default_json = self.HOME_DIR / "config" / "settings.json"
            if default_json.exists():
                _filepath = str(default_json)
            else:
                self.warnings["files"].append("Default settings file not found.")

            # read and parse it
            if _filepath:
                try:
                    with open(_filepath) as pf:
                        _settings = json.load(pf)
                # for corrupted files or other issues
                except IOError as i:
                    self.warnings["files"].append(f"Unable to open the parameters file: {i}")

        return _settings

    @property
    def parameters(self) -> dict:
        """
        Shows a gui dialog to get subject info.

        Returns
        -------
        dict of subject input.
        """

        # to avoid running the script everytime we access settings
        if not self._parameters:

            # TODO: check if there already is a pickled or json info file

            # information that's not specific to an experiment
            sub_dlg = gui.Dlg(title="Participant Information", labelButtonOK="Register", labelButtonCancel="Quit")

            # experiment
            sub_dlg.addText(text="Experiment", color="blue")
            sub_dlg.addFixedField("Title:", self.NAME)
            sub_dlg.addFixedField("Date:", str(data.getDateStr()))

            # subject
            sub_dlg.addText(text="Participant info", color="blue")
            sub_dlg.addField("NetID:", tip="Leave blank if you do not have one")
            sub_dlg.addField("Initials:", tip="Lowercase letters separated by dots (e.g. g.o.d)")
            sub_dlg.addField("Age:", choices=list(range(18, 81)))
            sub_dlg.addField("Gender:", choices=["Male", "Female"])
            sub_dlg.addField("Handedness:", choices=["Right", "Left"])
            sub_dlg.addField("Vision:", choices=["Normal", "Corrected"])
            # add the extra questions from params file
            extra_params = self.settings.get("SUBJECT")
            if extra_params:
                for key, val in extra_params:
                    sub_dlg.addField(key, val)

            # monitor
            sub_dlg.addText(text="Monitor", color="blue")
            screens = get_screens()
            sub_dlg.addField(label="Screen number:", choices=list(range(1, len(screens)+1)),
                             tip="Select 1 for the main screen")
            sub_dlg.addField(label="Monitor width (cm):", tip="one decimal point precision e.g. 33.6")
            sub_dlg.addField("Viewing distance (cm)", tip="one decimal point precision e.g. 57.5")

            sub_info = sub_dlg.show()
            if sub_dlg.OK:
                # TODO: save to file
                # TODO: give unique id w/ uuid
                self._parameters["date"] = sub_info[1]
                self._parameters["netid"] = sub_info[2]
                self._parameters["name"] = sub_info[3]
                self._parameters["age"] = int(sub_info[4])
                self._parameters["sex"] = sub_info[5]
                self._parameters["handedness"] = sub_info[6]
                self._parameters["vision"] = sub_info[7]
                self._parameters["screen_number"] = int(sub_info[8]) - 1
                self._parameters["screen_width"] = float(sub_info[9])
                self._parameters["screen_distance"] = float(sub_info[10])
            else:
                core.quit()

        return self._parameters

    @property
    def monitor(self):
        """
        Creates and saves a monitor with user's initials.

        Returns
        -------
        psychopy.monitors.Monitor
        """

        if self._monitor is None:

            screen = get_screens()[self.parameters.get("screen_number")]

            self._monitor = monitors.Monitor(name="{}_monitor".format(self.parameters.get("name")))
            self._monitor.setSizePix((int(screen.width), int(screen.height)))
            self._monitor.setWidth(self.parameters.get("screen_width"))
            self._monitor.setDistance(self.parameters.get("screen_distance"))
            self._monitor.save()

        return self._monitor

    @property
    def window(self):
        """
        Creates a window to display stimuli.

        Returns
        -------
        psychopy.visual.Window
        """

        if self._window is None:

            # generate the window
            self._window = visual.Window(
                name="ExperimentWindow",
                monitor=self.monitor,
                winType="pyglet",
                fullscr=True,
                screen=self.parameters["screen_number"],
                checkTiming=True,
                gammaErrorPolicy='ignore',
                allowGUI=False,
                color=[0, 0, 0],
                units='deg'
            )

        return self._window

    @property
    def data_paths(self) -> Dict[str, str]:
        """
        Path to data files that are used to save experiment (session), log, and subject information files.
        Saves the files under a folder with {subject_initials}_{date}/ format.

        Returns
        -------
        dictionary of form {'session': '', 'log': '', 'sub': ''}
        """
        if not self._data_paths:

            _dir = self.parameters["name"] / data.getDateStr()

            # file extensions will be added while saving
            self._data_paths["session"] = str(_dir / "session_data")
            self._data_paths["log"] = str(_dir / "log_data")
            self._data_paths["sub"] = str(_dir / "sub_data")
            self._data_paths["frames"] = str(_dir / "frame_intervals")

        return self._data_paths

    @property
    def timing(self) -> Dict[str, int]:
        """
        Compiles the timing of different stages (and adds jitter)

        Returns
        -------
        dict :

        """

        if not self._timing:

            self._timing["trial"] = 0
            self._timing["total"] = 0

            # timing values are dicts under 'durations' in the experiment settings
            for key, val in self.settings.get('EXPERIMENT').get('durations').items():

                # the first index is the duration. second one is how much random jitter it should have.
                duration = jitter(val[0], val[1])
                self._timing[key] = duration
                self._timing["trial"] += duration

            self._timing["total"] = int(self._timing["trial"] *
                                        (self.settings["data_points"]["main"] + self.settings["data_points"]["practice"])
                                        / 60 / 1000)

        return self._timing

    @property
    def handlers(self) -> Dict:
        """
        Experiment handler added by default. To add more use add_handler().

        Returns
        -------
        dict
        """
        if not self._handlers:

            # experiment handler
            self._handlers["exp"] = data.ExperimentHandler(
                name=f"{self.NAME}Handler",
                version=self.settings.get("EXPERIMENT")["version"],
                extraInfo=self.parameters,
                savePickle=False,
                saveWideText=False
            )

        return self._handlers

    def startup(self):
        """
        Check system status and ask which monitor to set up.

        Returns
        -------

        """

        # run checks
        self._check_paths()
        self._system_status()

        # add the check results to a gui
        report_gui = gui.Dlg(title='Report', labelButtonOK='Continue', size=100,
                             labelButtonCancel="Quit", screen=self.parameters["screen_number"])

        for key in self.warnings.keys():
            report_gui.addText(text=f"{key}", color="blue")
            vals = self.warnings[key]
            if len(vals):
                for i in vals:
                    report_gui.addText(text=f"{i}", color='red')
            else:
                report_gui.addText(text="All Passed.", color='green')

        # show it
        _resp = report_gui.show()

        # check debug mode
        if not self.MODE:
            if not report_gui.OK:
                self.end()

    def add_handler(self, name: str, conditions: List[Dict]) -> None:
        """
        Adds a psychopy TrialHandler to self.handlers.
        Also, adds it as a loop to the experiment handler.

        Parameters
        ----------
        name : str

        conditions : list
            can be generated using psychopy.data.importConditions() or by looping through lists of conditions.
        """

        # trial handler
        self.handlers[name] = data.TrialHandler(
            name=f"{name}Handler",
            trialList=conditions,
            nReps=int(self.settings.get("EXPERIMENT")["data_points"][name]),
            method='random'
        )

        # add it to the high-level experiment handler too
        self.handlers["exp"].addLoop(self.handlers[name])

    def init_logging(self, clock):
        """
        Generates the log file to populate with messages throughout the experiment.

        Parameters
        ----------
        clock : psychopy.clock.Clock
            experiment's global clock that is used to timestamp events.

        Returns
        -------

        """
        logging.setDefaultClock(clock)

        # use ERROR level for the console and DEBUG for the logfile
        logging.console.setLevel(logging.ERROR)
        log_data = logging.LogFile(self.data_paths["log"], filemode='w', level=logging.DEBUG)

        return log_data

    def save(self):
        """
        # TODO: add upload to NAS psychopy.web.requireInternetAccess
        Save the experiment into a file
        """
        for handler in self.handlers:
            handler.saveAsWideText(self.data_paths["session"], delim=',')

        self.window.saveFrameIntervals(self.data_paths["frames"])

    def end(self):
        """
        Closes the experiment
        """
        self.window.close()
        core.quit()
        sys.exit()

    def force_quit(self, key: str = 'space') -> None:
        """
        Quits the experiment during runtime if a key (default 'space') is pressed.

        Parameters
        ----------
        key : str
            keyboard button to press to quit the experiment.
        """
        pressed = event.getKeys()
        if key in pressed:
            self.window.close()
            core.quit()
            sys.exit()

    def _check_paths(self):
        """
        Finds out if critical paths exist.
        """
        data_dir = self.HOME_DIR / "data"
        config_dir = self.HOME_DIR / "config"

        if not config_dir.exists():
            self.warnings["Files"].append("Config directory not found.")
        if not data_dir.exists():
            self.warnings["Files"].append("Data directory not found.")

    def _system_status(self):
        """
        Check system status: windowRefreshTimeSD, systemMemFreeFRAM, systemUserProcFlagged, priority
        """

        # TODO: Add comments
        # TODO: Log everything

        # initial system check
        _run_info = info.RunTimeInfo(
            # win=self.window,
            refreshTest='grating',
            userProcsDetailed=True,
            verbose=True
        )
        thresh = 0.20  # refresh rate standard deviation threshold

        # start logging
        logging.info("SYSTEM CHECKS\n======")

        # check internet connection for saving files to server
        if not _run_info["systemHaveInternetAccess"]:
            self.warnings["System"].append("No internet access.")

        # check the monitor refresh time
        refresh_sd = _run_info["windowRefreshTimeSD_ms"]
        if refresh_sd > thresh:
            self.warnings["System"].append(f"Monitor refresh rate is too unreliable: {refresh_sd}")

            # if _run_info["windowIsFullScr"]:
            flagged = _run_info['systemUserProcFlagged']
            if len(flagged):
                s = "Quit and close these programs to fix the refresh rate issue:\n"
                app_set = {}
                for i in range(len(_run_info['systemUserProcFlagged']) - 1):
                    if _run_info['systemUserProcFlagged'][i][0] not in app_set:
                        app_set.update({_run_info['systemUserProcFlagged'][i][0]: 0})
                while len(app_set) != 0:
                    s += f"\t--{app_set.popitem()[0]}\n"
                self.warnings["System"].append(s)

        if _run_info["systemMemFreeRAM"] < 1000:
            self.warnings["System"].append(
                "Not enough available RAM: {round(_run_info['systemMemFreeRAM'] / 1000)} GB is available."
            )

        # if it's Mac OS X (these methods don't run on that platform)
        if platform == "darwin":
            self.warnings["System"].append("Could not raise the priority because you are on Mac OS X.")
        else:
            Computer.setPriority("realtime", disable_gc=True)


