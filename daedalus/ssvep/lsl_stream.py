#!/usr/bin/env python
"""
created 1/13/20 

@author DevXl

DESCRIPTION
"""
from pylsl import StreamInlet, StreamOutlet, StreamInfo, resolve_byprop, local_clock
from pyOpenBCI import OpenBCICyton
from psychopy import data, core
import collections
import numpy as np
import mne
import os


def broadcast_cyton(device, port="/dev/ttyUSB0"):

    SCALE_FACTOR_EEG = (4500000) / 24 / (2 ** 23 - 1)  # uV/count

    print("Creating LSL stream for EEG. \nName: OpenBCIEEG\nID: OpenBCItestEEG\n")

    info_eeg = StreamInfo('OpenBCIEEG', 'EEG', 8, 250, 'float32', 'OpenBCI')

    outlet_eeg = StreamOutlet(info_eeg)

    def lsl_streamers(sample):
        outlet_eeg.push_sample(np.array(sample.channels_data) * SCALE_FACTOR_EEG)

    board = OpenBCICyton(port=port)

    board.start_stream(lsl_streamers)


def get_streams(stream_names, chunk_size):
    """
    Receives all the streams

    Parameters
    ----------
    stream_names (list) name of all the streams specified when creating
        the outlet

    Returns
    -------
    inlets (dict) streams and their time correction
    """
    for stream in stream_names:
        print("looking for {} stream...".format(stream))

    inlets = collections.defaultdict(dict)
    stream_types = []
    for name in stream_names:
        stream = resolve_byprop('name', name, timeout=2)
        if name == "markers":
            inlet = StreamInlet(stream[0])
        else:
            inlet = StreamInlet(stream[0], max_chunklen=chunk_size)
        s_type = inlet.info().type()
        if s_type == "EEG" and len(stream) == 0:
            raise RuntimeError("Cant find any EEG stream")

        stream_types.append(s_type)
        inlets[name]["stream"] = inlet
        inlets[name]["init_correction"] = inlet.time_correction()

    for key, val in dict(collections.Counter(stream_types)).items():
        print("Found {} streams of {} data: ".format(val, key))

    return inlets


def get_raw_eeg(eeg_inlet, marker_inlet, record_time, chunk_size, debug=False):

    eeg_info = eeg_inlet.info()
    n_chans = eeg_info.channel_count()

    eeg_ls = collections.deque()
    eeg_ts = collections.deque()
    eeg_tc = collections.deque()
    marker_ls = collections.deque()
    marker_ts = collections.deque()
    marker_prev = collections.deque()
    drop_log = collections.deque()
    chunk_num = 1
    clock = core.MonotonicClock()

    t_init = local_clock()
    eeg_correction = eeg_inlet.time_correction()
    if marker_inlet:
        marker_correction = marker_inlet.time_correction()

    print("Start getting raw data")

    while (local_clock() - t_init) < record_time:

        try:
            eeg_data, eeg_timestamp = eeg_inlet.pull_chunk(timeout=2, max_samples=chunk_size)
            if eeg_timestamp:
                eeg_correction = eeg_inlet.time_correction()
                if len(eeg_data) < chunk_size:
                    drop_log.append(chunk_num)
                else:
                    eeg_ls.append(eeg_data)
                    eeg_ts.append(eeg_timestamp)
                    eeg_tc.append(eeg_correction)

            if marker_inlet:
                marker_data, marker_timestamp = marker_inlet.pull_sample(timeout=0)

                if marker_data:
                    if debug:
                        print("DIN: {}".format(marker_data))
                    if marker_timestamp == any(eeg_timestamp):
                        print("NICE")
                    else:
                        print("not accurate")

                    marker_ls.append([chunk_num-1, 0, marker_data[0]])
                    # marker_correction = marker_inlet.time_correction()
                    # marker_ls.append([chunk_num[0])
                    # marker_ts.append(marker_timestamp + marker_correction)
            chunk_num += 1

        except KeyboardInterrupt:
            break

    t_end = clock.getTime()
    tot_rec_t = t_end - t_init
    tot_smps = chunk_num - 1

    # construct the raw data frame for MNE structure (n_channels, n_samples)
    raw_df = np.array([])
    for chunk in eeg_ls:
        this_chunk = np.array(chunk).transpose()
        if raw_df.size == 0:
            raw_df = this_chunk
        else:
            raw_df = np.concatenate((raw_df, this_chunk), axis=1)

    # construct the epoch data frame for MNE structure (n_epochs, n_channels, n_samples)
    epoch_df = np.array([])
    for trig in range(len(marker_ls)):
        start = int(trig*chunk_size)
        stop = int(trig*chunk_size) + int(3*250)
        this_epoch = raw_df[:, start:stop]
        np.append(epoch_df, this_epoch)

    # the event data frame
    event_df = np.array(list(marker_ls))

    return raw_df, epoch_df, event_df, drop_log


def save_data(eeg_data, event_data, epoch_data, event_id, chan_names, subj, sfreq=250):
    """

    Parameters
    ----------
    eeg_data
    event_data
    sfreq

    Returns
    -------

    """
    curr_date = data.getDateStr()
    dir_name = os.path.join(os.getcwd(), "data/eeg/")
    fname = "{}_session{}_{}".format(subj["Participant"], subj["Session"], curr_date)

    print("Saving eeg data to csv file {}.csv".format(fname))
    print("Saving event data to csv file {}.csv".format(fname))
    np.savetxt("{}raw_{}.csv".format(dir_name, fname), eeg_data, delimiter=",")
    np.savetxt("{}event_{}.csv".format(dir_name, fname), event_data, delimiter=",")

    montage = 'standard_1005'

    mne_info = mne.create_info(
        ch_names=chan_names,
        ch_types="eeg",
        sfreq=sfreq,
        montage=montage
    )

    tmin = -0.1
    custom_epochs = mne.EpochsArray(epoch_data, mne_info, event_data, tmin, event_id)
    raw_mne = mne.io.RawArray(eeg_data, mne_info)

    print("Saving eeg data to fif file {}.fif".format(fname))
    print("Saving event data to fif file {}.fif".format(fname))
    custom_epochs.save('{}epoch_{}-epo.fif'.format(dir_name, fname))
    raw_mne.save('{}raw_{}.fif'.format(dir_name, fname))
    mne.write_events('{}event_{}-eve.fif'.format(dir_name, fname), event_data)