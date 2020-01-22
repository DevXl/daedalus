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


def get_streams(stream_names, chunk_size):
    """
    Receives all specified streams

    Parameters
    ----------
    stream_names (list) name of all the outlets
    chunk_size (int) number of chunks in each sample

    Returns
    -------
    inlets (dict) LSL streams with their name as key and StreamInlet object as value
    """
    inlets = collections.defaultdict(dict)

    # loop through the names and find the streams that match
    for name in stream_names:
        print("looking for {} stream...".format(name))
        stream = resolve_byprop('name', name, timeout=2)
        if len(stream):
            print("{} found!\n\n".format(name))
        else:
            raise RuntimeError("Can't find the stream")

        # don't want to read the markers in chunks
        if name == "Markers":
            inlets[name] = StreamInlet(stream[0])
        else:
            inlets[name] = StreamInlet(stream[0], max_chunklen=chunk_size)

    return inlets


def get_raw_eeg(inlets, record_time, chunk_size, debug=False):
    """
     Reads LSL inlets and parses data to MNE-fif format

     Parameters
     -----------
     inlets (dict) LSLStream inlets: one EEG and one Markers
     record_time (float) duration to record data
     chunk_size (int) number of chunks in each sample
     debud (bool) show debug messages or not

     Returns
     -------
     eeg_data (dict) holding raw_eeg, raw_events, and the drop_log
    """ 
    # get the EEG and Markers inlets into local variables
    eeg_found = 0
    for key, val in inlets.items():
        if val.info().type() == "EEG":
            eeg_inlet = val
            eeg_found += 1
        if val.info().type() == "Markers":
            marker_inlet = val
    
    if eeg_found > 1:
        raise RuntimeError("Only one EEG stream is accepted but {} provided.".format(eeg_found))

    # setup values for EEG
    eeg_info = eeg_inlet.info()
    n_chans = eeg_info.channel_count()
    eeg_ls = collections.deque()
    eeg_ts = collections.deque()
    eeg_tc = collections.deque()

    # setup values for Markers
    marker_ls = collections.deque()

    # keep track of the recording
    drop_log = collections.deque()
    chunk_num = 1

    # start timing
    t_init = local_clock()
    eeg_correction = eeg_inlet.time_correction()
    if marker_inlet:
        marker_correction = marker_inlet.time_correction()

    # start recording
    if debug:
        print("Start getting raw data")

    while (local_clock() - t_init) < record_time:
        try:
            eeg_data, eeg_timestamp = eeg_inlet.pull_chunk(timeout=2, max_samples=chunk_size)
            if eeg_timestamp:
                eeg_correction = eeg_inlet.time_correction()
                if len(eeg_data) != chunk_size:
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

    t_end = local_clock().getTime()
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

    # the event data frame
    event_df = np.array(list(marker_ls))

    # data dict
    eeg_data = {"eeg_raw": raw_df, "event_raw": event_df, "drop_raw": drop_log}

    return eeg_data


def save_data(eeg_data, event_data, chan_names, subj, sfreq=250):
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
    dir_name = os.path.join(os.getcwd(), "data", "eeg")
    fname = "{}_session{}_{}".format(subj["Participant"], subj["Session"], curr_date)

    print("Saving eeg data to csv file {}.csv".format(fname))
    print("Saving event data to csv file {}.csv".format(fname))
    np.savetxt("{}{}_raw.csv".format(dir_name, fname), eeg_data, delimiter=",")
    np.savetxt("{}{}_eve.csv".format(dir_name, fname), event_data, delimiter=",")

    montage = 'standard_1005'

    mne_info = mne.create_info(
        ch_names=chan_names,
        ch_types="eeg",
        sfreq=sfreq,
        montage=montage
    )

    # custom_epochs = mne.EpochsArray(epoch_data, mne_info, event_data, tmin, event_id)
    raw_mne = mne.io.RawArray(eeg_data, mne_info)

    print("Saving eeg data to fif file {}.fif".format(fname))
    print("Saving event data to fif file {}.fif".format(fname))
    raw_mne.save('{}{}_raw.fif'.format(dir_name, fname))
    mne.write_events('{}event_{}-eve.fif'.format(dir_name, fname), event_data)