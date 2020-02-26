#!/usr/bin/env python
"""
created 1/13/20

@author DevXl

Helper functions for building experiment quicker!
"""
from psychopy import gui, data, core, visual, event, monitors
from psychopy.tools.filetools import fromFile, toFile
import subprocess
import os


def get_info(name):
    """
    Show GUI to get experiment information

    Parameters
    ----------
    name (str) name of the experiment

    Returns
    -------
    exp_info (dict) containing subject, session, setting, number of trials, method, and date information
    """

    # parameters needed for the experiment
    exp_info = {
            'Participant': '',
            'Session': '',
            'debug': False,
            'Date': data.getDateStr(),
            'Monitor': 'ASUS_ROG',
    }

    # make a dialogue to change params
    dlg = gui.DlgFromDict(exp_info, title=name, fixed=['Date'])

    if dlg.OK:
        # if the OK button is clicked save and proceed
        toFile('exp_info.pickle', exp_info)
    else:
        # quit if it's not
        core.quit()

    return exp_info


def save_data(handler, win, inf, ex=False):

    """
    Saves experiment data

    Parameters
    ----------
    handler (psychopy.TrialHandler) experiment handler
    win (psychopy.Window) experiment's window
    inf (dict) experiment information
    ex (bool) save and exit if True, only save if False

    Returns
    -------
    None
    """

    file_name = "psyc_{}_session{}_{}".format(inf['Participant'], inf['Session'], inf['Date'])
    handler.saveAsWideText("data/psyc/" + file_name + ".csv")
    win.saveFrameIntervals(fileName="data/log/" + file_name + ".txt", clear=True)

    if ex:
        exit_msg = visual.TextStim(win=win, pos=[0, 0], height=0.5, wrapWidth=10, text="Exiting...")
        exit_msg.draw()
        win.flip()
        core.wait(1)
        win.close()
        core.quit()


def force_end(window, inf, handler):
    """
    Forces the experiment to save data and quit

    Parameters
    ----------
    window (psychopy.Window) experiment's window
    expinfo (dict) experiment information
    handler (psychopy.TrialHandler) experiment handler

    Returns
    -------
    None
    """
    if 'escape' in event.waitKeys():
        save_data(handler, window, inf, True)


def time_calc(num_blocks, num_conditions, trial_dur, num_datapoints=20):
    """
    Calculates the duration and number of trials required to reach the desired number of data points per condition

    Parameters
    ----------
    num_conditions (int) how many conditions are in the experiment
    trial_dur (float) duration of each trial in seconds
    num_datapoints (int) how many data points we want to get

    Returns
    -------
    block_dur (float) duration of each block in minutes
    num_trials (int) number of trials
    session_dur (float) entire data collection session in minutes
    """

    # rest time
    interstim_rest_dur = .5  # delay to start the trial
    actual_trial_dur = trial_dur + interstim_rest_dur
    max_rest_dur = 3 * 60  # 3 minute breaks (self-initiate option)

    # total times
    total_task_dur = actual_trial_dur * num_conditions * num_datapoints
    total_rest_dur = max_rest_dur * (num_blocks - 1)
    session_dur = total_task_dur + total_rest_dur

    # number of trials per block and in total
    block_dur = total_task_dur / num_blocks
    num_trials_per_block = block_dur / actual_trial_dur
    num_trials = num_trials_per_block * num_blocks

    return block_dur, num_trials, session_dur


def get_screen(name, debug, cmd=True):

    # All monitors available in the lab
    models = {
        "laptop": [
            1920, 1080, 33.1, 60
        ],
        "cerberus": [
            1280, 800, 64, 60
        ],
        "ASUS_ROG": [
            1920, 1080, 54.5, 240
        ],
        "CRT": [
            1024, 768, 50, 60
        ],
        "BenQ": [
            1920, 1080, 60, 60
        ]
    }

    # This specific monitor's specs
    mon = models[name]
    dims = mon[0], mon[1]
    width = mon[2]
    rf = mon[3]

    mon_info = {
        "name": mon,
        "width_px": dims[0],
        "height_px": dims[1],
        "width_cm": width,
        "refresh_rate": rf
    }

    # Select the monitor via Commandline
    if cmd:
        get_ext_monitor_cmd = "xrandr --screen {} --output {} --mode {}x{} --rate {}".format(not debug, name, dims[0],
                                                                                             dims[1], rf)
        subprocess.run(get_ext_monitor_cmd.split())

    view_dist = 57.

    exp_monitor = monitors.Monitor(name, width=width, distance=view_dist)
    exp_monitor.setSizePix(dims)
    exp_monitor.save()

    exp_window = visual.Window(monitor=exp_monitor, size=dims, color='grey', fullscr=False if debug else True,
                               units="deg", allowGUI=True, screen=1)

    exp_window.recordFrameIntervals = True

    return exp_window, mon_info, exp_monitor
