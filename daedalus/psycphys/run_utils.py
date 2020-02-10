#!/usr/bin/env python
"""
created 2/9/20 

@author DevXl

Handles making/checking files and folders for subject, experiment, data, etc.
"""
from psychopy import gui
from psychopy.platform_specific import rush
import math


def check_paths(path, *argv):

    paths = {}
    # configs = {}

    project_home = path.parent.parent
    paths["home"] = project_home
    config_files = list(map(lambda p: project_home / "config" / p, argv))
    for i, path in config_files:
        if path.is_file():
            paths[argv[i]] = path
            # with open(path, 'r') as config_file:
            #     configs.update(json.load(config_file))
        else:
            raise FileNotFoundError(f"I cant locate the {argv[i]} file.")

    data_dir = project_home / "data"
    logExp_file = data_dir / "logExperiment.log"

    if data_dir.is_dir():
        paths["data"] = data_dir
        paths["logExp"] = logExp_file
    else:
        raise NotADirectoryError

    info = {"subject": "", "session": range(0, 4)}
    init_gui = gui.DlgFromDict(info, title="Experiment initialization",
                               labels={"subject": "Participant initials:",
                                       "session": "Session"},
                               tip={"subject": "in capital letters separated by dots e.g. K.I.R",
                                    "session": "0: Training"},
                               )
    init_gui.addField(label="Participant initials:", tip="in capital letters separated by dots e.g. K.I.R")
    init_gui.addField(label="Session", choices=range(0, 4), tip="0: Training")

    if init_gui.OK:
        if any(ch.isdigit() for ch in info['subject']):
            raise ValueError("Name initials cannot contain numbers.")
        subject = info['subject']
        session = info['session']
    else:
        raise SystemExit("User cancelled.")

    subj_dir = data_dir / subject
    past_sees_dirs = list(e.relative_to(subj_dir) for e in subj_dir.iterdir() if e.is_dir())
    this_sess_dir = subj_dir / session

    if subj_dir.is_dir():
        for d in past_sees_dirs:
            if this_sess_dir == past_sees_dirs:
                raise IsADirectoryError(
                      f"{subject} has already participated in session {session}."
                      f"Check for a conflict in initials.")
            elif this_sess_dir < int(d):
                raise NotADirectoryError(
                       f"{subject} has already participated in the {d} session of the experiment "
                       f"but I could not find that directory.")
            try:
                this_sess_dir.mkdir()
            except PermissionError:
                raise Exception(permission_msg(this_sess_dir, 'directory'))
    else:
        try:
            subj_dir.mkdir()
        except PermissionError:
            raise Exception(permission_msg(subj_dir, 'directory'))

    paths["subject"] = subj_dir
    paths["session"] = this_sess_dir

    return paths, subject,  session


def check_demographics(info):

    demog_log = []
    if not (any(ch.isdigit() for ch in info["age"])):
        demog_log.append("Age is not a number.")

    if any(ch.isdigit() for ch in info['sleep']):
        demog_log.append("Average hours of sleep is not a number.")

    if info['vision'] == "Other":
        raise Exception("Participant should have only normal or corrected to normal vision.")

    return demog_log


def check_system(info, rt):

    sys_log = []

    refresh_SDthreshhold = 0.20  # ms
    if info["windowRefreshTimeSD_ms"] > refresh_SDthreshhold:
        sys_log.append(f"Monitor has high refresh rate variability: "
                       f"{info['windowRefreshTimeSD_ms']}")

    actual_rate = math.ceil(1000 / info["windowRefreshTimeAvg_ms"])
    if actual_rate == info["rate"]:
        sys_log.append(f"Monitor shows {actual_rate} per second as opposed to {rt}.")

    if info["systemMemFreeRAM"] < 1000:
        sys_log.append(f"Not enough available RAM: "
                       f"{math.floor(info['systemMemFreeRAM']/1000)} GB is available")

    if not info['psychopyHaveExtRush']:
        try:
            rush(True)
        except PermissionError:
            sys_log.append("Not enough permission to rush().")

    if info["systemUserProcFlagged"]:
        for proc in info["systemUserProcFlagged"]:
            sys_log.append(f"Process with ID {proc[1]} is flagged. "
                           f"Close the {proc[0]} application.")
            raise ResourceWarning(proc)

    return sys_log


def permission_msg(name, f):
    return f"I don't have enough permission to make the {name} {f}."

