#!/usr/bin/env python
"""
created 1/13/20 

@author DevXl

DESCRIPTION
"""
from pylsl import StreamInlet, StreamOutlet, StreamInfo, resolve_byprop, resolve_streams
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
        inlet = StreamInlet(stream[0], max_chunklen=chunk_size)
        # info = inlet.info()
        # name = info.name()
        s_type = inlet.info().type()
        if s_type == "EEG" and len(stream) == 0:
            raise RuntimeError("Cant find any EEG stream")

        stream_types.append(s_type)
        inlets[name]["stream"] = inlet
        inlets[name]["correction"] = inlet.time_correction()

    for key, val in dict(collections.Counter(stream_types)).items():
        print("Found {} streams of {} data: ".format(val, key))

    return inlets


def acquire_data(eeg_inlet, marker_inlet, record_time, chunk_size, debug=False):
    """

    Returns
    -------

    """
    print("Start acquiring data")

    eeg_info = eeg_inlet.info()
    n_chans = eeg_info.channel_count()

    eeg_ls = collections.deque()
    eeg_ts = collections.deque()
    marker_ls = collections.deque()
    marker_ts = collections.deque()
    marker_prev = collections.deque()
    drop_log = collections.deque()
    sample_num = 1
    prev_marker = 0
    clock = core.MonotonicClock()

    t_init = clock.getTime()
    time_correction = eeg_inlet["correction"]

    while (clock.getTime() - t_init) < record_time:

        this_chunk = collections.deque()
        try:
            eeg_data, eeg_timestamp = eeg_inlet["stream"].pull_chunk(timeout=2,
                                                           max_samples=chunk_size)
            if eeg_timestamp:
                if len(eeg_data) < chunk_size or len(eeg_data) != len(eeg_timestamp):
                    drop_log.append(sample_num)
                else:
                    eeg_ls.append(eeg_data)
                    eeg_ts.append(eeg_timestamp)

            if marker_inlet:
                marker_data, marker_timestamp = marker_inlet["stream"].pull_sample(timeout=0)

                if marker_timestamp:
                    if debug:
                        print("DIN: {}".format(marker_data[0]))

                    marker_ls.append(marker_data[0])
                    marker_ts.append(marker_timestamp)
                    marker_ts.append(prev_marker)
                    prev_marker = marker_data[0]
                else:
                    marker_ls.append(0)
                    marker_ts.append(eeg_timestamp)
                    prev_marker = 0
            sample_num += 1

        except KeyboardInterrupt:
            break

    # for i in range(chunk_size):
    #     this_sample = collections.deque()
    #     this_sample.append(eeg_timestamp[i] + time_correction)
    #     this_sample.extend(eeg_data[i])
    #     this_chunk.append(list(this_sample))
    # this_sample.append(marker_data[0])
    #
    # this_marker = [sample_num, prev_marker, marker_data[0]]
    # prev_marker = marker_data[0]
    t_end = clock.getTime()
    tot_rec_t = t_end - t_init
    # eeg_ls = list(eeg_ls)
    # eeg_ts = list(eeg_ts)
    eeg_df = np.array()
    print(eeg_ls[0])
    print(len(eeg_ls[0]))
    print(eeg_ts[0])
    print(len(eeg_ts[0]))

    for i in range(sample_num):
        for j in range(chunk_size):
            for k in range(n_chans):
                eeg_df.append([eeg_ts[i][j]])
                eeg_df.append()
    print(list(eeg_ls))
    if marker_inlet:
        print(len(list(marker_ls)), list(marker_ls)[0])
        print(len(list(marker_ts)), list(marker_ts)[0])
    print("Total of {}s data ({} samples) successfully collected...".format(tot_rec_t, sample_num-1))
    print("Number of dropped chunks: {}".format(len(list(drop_log))))

    eeg_df = np.asarray(list(eeg_ls))
    event_df = np.asarray(list(marker_ls))

    return eeg_df, event_df, drop_log


def save_data(eeg_data, event_data, event_id, chan_names, subj, sfreq=250):
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
    eeg_fname = os.path.join(os.getcwd(), "data/eeg/eeg_{}_session{}_{}".format(
        subj["Participant"], subj["Session"], curr_date))
    event_fname = os.path.join(os.getcwd(), "data/eeg/event_{}_session{}_{}".format(
        subj["Participant"], subj["Session"], curr_date))

    print("Saving eeg data to csv file {}.csv".format(eeg_fname))
    print("Saving event data to csv file {}.csv".format(event_fname))
    np.savetxt("{}.csv".format(eeg_fname), eeg_data, delimiter=",")
    np.savetxt("{}.csv".format(event_fname), event_data, delimiter=",")

    montage = 'standard_1005'

    mne_info = mne.create_info(
        ch_names=chan_names,
        ch_types="eeg",
        sfreq=sfreq,
        montage=montage
    )

    tmin = -0.1
    custom_epochs = mne.EpochsArray(eeg_data, mne_info, event_data, tmin, event_id)

    print("Saving eeg data to fif file {}.fif".format(eeg_fname))
    print("Saving event data to fif file {}.fif".format(event_fname))
    custom_epochs.save('{}-epo.fif'.format(eeg_fname))
    mne.write_events('{}-eve.fif'.format(event_fname), event_data)