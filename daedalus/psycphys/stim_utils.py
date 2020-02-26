#!/usr/bin/env python
"""
created 1/13/20 

@author DevXl

Stimulus commonly used in psychophysics experiment
"""
from psychopy import visual
import os
import glob


def get_statics(window, pos):
    """
    For generating non-moving stimulus like the target, fixation, and messages

    Parameters
    ----------
    window (psychopy.Window) win param for psychopy.visual stuff
    pos (list or tuple) position of the **target** stimulus

    Returns
    -------
    statics (dict) containing multiple visual objects as keys: target, fixation (tuple: inner, outer), rest message,
        start message, instruction message, and trial end message
    """
    # streams
    left_stream = visual.ImageStim(win=window, pos=[(pos[0]-6), pos[1]], size=6)
    right_stream = visual.ImageStim(win=window, pos=[(pos[0]+6), pos[1]], size=6)
    streams = left_stream, right_stream

    # cues
    loc_cue = visual.TextStim(win=window, pos=[0, 0], height=2, wrapWidth=20, text="")
    cat_cue = visual.ImageStim(win=window, pos=[pos[0], (pos[1]+1)], size=1)
    cues = loc_cue, cat_cue

    # Fixation made of two concentric circles
    fixation_inner = visual.Circle(win=window, size=0.3, pos=[-p for p in pos])
    fixation_outer = visual.Circle(win=window, size=0.6, pos=[-p for p in pos])
    fixation = fixation_inner, fixation_outer

    # Text messages
    rest_msg = visual.TextStim(win=window, pos=[0, 0], height=0.8, wrapWidth=20,
                               text="Time for a break! Press ENTER to continue when ready...")
    start_msg = visual.TextStim(win=window, pos=[0, 0], height=0.8, wrapWidth=20,
                                text="Press 'C' when you are ready to start!")
    instruction_msg = visual.TextStim(win=window, pos=[0, 0], height=0.8, wrapWidth=20,
                                      text="Please fixate at the middle of the concentric circles.\n"
                                           "Whenever you DON'T SEE the dot HOLD DOWN the SPACEBAR\n" 
                                           "When you SEE the dot RELEASE the SPACEBAR")
    end_msg = visual.TextStim(win=window, pos=[0, 0], height=0.8, wrapWidth=20,
                              text="Thank you for your participation!\n")
    init_msg = visual.TextStim(win=window, pos=[0, 0], height=0.8, wrapWidth=20,
                               text="Press C to start the trial")
    practice_msg = visual.TextStim(win=window, pos=[0, 0], height=0.8, wrapWidth=20,
                                   text="Ready for some practice trials?\n\nPress 'C'!\n")

    # The dict that contains statics as values
    statics = {
        "practice": practice_msg,
        "images": streams,
        "fixation": fixation,
        "rest": rest_msg,
        "start": start_msg,
        "instruction": instruction_msg,
        "finish": end_msg,
        "init": init_msg,
        "cues": cues
    }

    return statics


def load_stim(category, file_type, known_path=""):
    """
    Loads the stimulus paths

    Parameters
    ----------
    category (str) faces, places, composites, etc.
    file_type (str) file extensions
    known_path (str) the path to use for loading the files in case it is known

    Returns
    -------
    all_stims (list) an array containing all the files' paths
    """
    # check if the path is known
    if len(known_path):

        # if the path is passed then files are in that directory
        stim_path = known_path
    else:

        # if path is not known then faces stims are in "current_dir/stim/faces" and palces stims are
        # in "current_dir/stim/places"
        stim_path = os.path.join(os.getcwd(), "stim/{}".format(category))

    # look for all csv files in that directory and put the paths in a list as strings

    stim_files = glob.glob(stim_path + "/*." + file_type)

    return stim_files


def flicker(freq, num_frames, refresh_rate):
    """
    Gives the on and off frames for SSVEP

    Parameters
    ----------
    freq (float) the rate in hz the stimulus is supposed to flicker at

    num_frames (int) number of frames the stimulus is presented for

    refresh_rate (int) monitor's refresh rate

    Returns
    -------
    frames (tuple) two arrays corresponding to "on" and "off" frame numbers
    """

    freq_frame = (refresh_rate / 2) / freq
    on_frames = []
    off_frames = []
    frame_counter = 0

    for fr in range(int(num_frames)):

        if frame_counter < freq_frame:
            change_state = False
            frame_counter += 1
        else:
            change_state = True
            frame_counter = 1

        if change_state:
            on_frames.append(fr)
        else:
            off_frames.append(fr)

    frames = on_frames, off_frames

    return frames
