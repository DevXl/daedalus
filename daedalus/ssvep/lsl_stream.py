#!/usr/bin/env python
"""
created 1/13/20 

@author DevXl

DESCRIPTION
"""
from pylsl import StreamInlet, StreamOutlet, StreamInfo, resolve_byprop
from pyOpenBCI import OpenBCICyton
from sklearn.linear_model import LinearRegression
from psychopy import data, core
import numpy as np
import mne


def broadcast_stream(device, port="/dev/ttyUSB0"):

    SCALE_FACTOR_EEG = (4500000) / 24 / (2 ** 23 - 1)  # uV/count

    print("Creating LSL stream for EEG. \nName: OpenBCIEEG\nID: OpenBCItestEEG\n")

    info_eeg = StreamInfo('OpenBCIEEG', 'EEG', 8, 250, 'float32', 'OpenBCI')

    outlet_eeg = StreamOutlet(info_eeg)

    def lsl_streamers(sample):
        outlet_eeg.push_sample(np.array(sample.channels_data) * SCALE_FACTOR_EEG)

    board = OpenBCICyton(port=port)

    board.start_stream(lsl_streamers)


def get_stream(stream_type, chunk_size, filename="", jitter=False):
    """
    Receive a stream and translate to numpy array
    Also saves a csv version

    Parameters
    ----------
    stream_type (str) "Markers" or "EEG"

    Returns
    -------
    df (np.array) containing the collected data
    """
    # check if the filename is provided
    # TODO: find a better way
    if len(filename) > 0:
        f_name = filename
    else:
        f_name = "stream{}_{}.csv".format(stream_type, data.getDateStr())

    print("looking for a {} stream...".format(stream_type))
    streams = resolve_byprop('type', stream_type, timeout=2)

    if len(streams) == 0:
        raise RuntimeError("Cant find any stream")

    inlets = {}
    print("Found {} streams of {} data: ".format(len(streams), stream_type))
    for i, stream in streams:
        inlets[i] = StreamInlet(stream, max_chunklen=chunk_size)

    print("Start acquiring data")
    time_correction = inlets[0].time_correction()

    info = inlet.info()
    description = info.desc()

    sfreq = info.nominal_srate()
    n_chans = info.channel_count()

    mne_info = mne.create_info(n_chans, sfreq)

    ch = description.child('channels').first_child()
    ch_names = [ch.child_value('label')]
    for i in range(1, n_chans):
        ch = ch.next_sibling()
        ch_names.append(ch.child_value('label'))



