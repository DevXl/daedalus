#!/usr/bin/env python
"""
created 1/13/20 

@author DevXl

DESCRIPTION
"""
from pylsl import StreamInlet, StreamOutlet, StreamInfo, resolve_byprop, resolve_streams
from pyOpenBCI import OpenBCICyton
from sklearn.linear_model import LinearRegression
from psychopy import data, core
import collections
import numpy as np
import mne


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
    print("looking for {} streams...".format(len(stream_names)))

    inlets = {}
    stream_types = []
    for name in stream_names:
        stream = resolve_byprop('name', name, timeout=2)

        if len(stream) == 0:
            raise RuntimeError("Cant find any stream")

        inlet = StreamInlet(stream, max_chunklen=chunk_size)
        info = inlet.info()
        name = info.name()
        stream_types.append(info.type())
        inlets[name]["stream"] = inlet
        inlets[name]["correction"] = inlet.time_correction()

    for key, val in collections.Counter(stream_types):
        print("Found {} streams of {} data: ".format(val, key))

    return inlets


def acquire_data(eeg_inlet, marker_inlet, chan_names, record_time):
    """

    Returns
    -------

    """
    print("Start acquiring data")

    info = eeg_inlet.info()

    sfreq = info.nominal_srate()
    n_chans = info.channel_count()
    montage = 'standard_1005'

    mne_info = mne.create_info(
        ch_names=chan_names,
        ch_types="eeg",
        sfreq=sfreq,
        montage=montage
    )

    raw_df = mne.io.RawArray(data, info)


 # def read_chunk(data, idx, fi, start, stop, cals, mult):
 #        """Read a chunk of raw data"""
 #        input_fname = self._filenames[fi]
 #        data_ = np.genfromtxt(input_fname, delimiter=',', comments='%',
 #                              skip_footer=1)
 #        """
 #        Dealing with the missing data
 #        -----------------------------
 #        When recording with OpenBCI over Bluetooth, it is possible for some of
 #        the data packets, samples, to not be recorded. This does not happen
 #        often but it poses a problem for maintaining proper sampling periods.
 #        OpenBCI data format combats this by providing a counter on the sample
 #        to know which ones are missing.
 #        Solution
 #        --------
 #        Interpolate the missing samples by resampling the surrounding samples.
 #        1. Find where the missing samples are.
 #        2. Deal with the counter reset (resets after cycling a byte).
 #        3. Resample given the diffs.
 #        4. Insert resampled data in the array using the diff indices
 #           (index + 1).
 #        5. If number of missing samples is greater than the missing_tol, Values
 #           are replaced with np.nan.
 #        """
 #        # counter goes from 0 to 255, maxdiff is 255.
 #        # make diff one like others.
 #        missing_tol = self._raw_extras[fi]['missing_tol']
 #        diff = np.abs(np.diff(data_[:, 0]))
 #        diff = np.mod(diff, 126) - 1
 #        missing_idx = np.where(diff != 0)[0]
 #        missing_samps = diff[missing_idx].astype(int)
 #
 #        if missing_samps.size:
 #            missing_nsamps = np.sum(missing_samps, dtype=int)
 #            missing_cumsum = np.insert(np.cumsum(missing_samps), 0, 0)[:-1]
 #            missing_data = np.empty((missing_nsamps, data_.shape[-1]),
 #                                    dtype=float)
 #            insert_idx = list()
 #            for idx_, nn, ii in zip(missing_idx, missing_samps,
 #                                    missing_cumsum):
 #                missing_data[ii:ii + nn] = np.nanmean(data_[(idx_, idx_ + 1), :], axis=0)
 #                if nn > missing_tol:
 #                    missing_data[ii:ii + nn] *= np.nan
 #                    warnings.warn('The number of missing samples exceeded the '
 #                                  'missing_tol threshold.')
 #                insert_idx.append([idx_] * nn)
 #            insert_idx = np.hstack(insert_idx)
 #            data_ = np.insert(data_, insert_idx, missing_data, axis=0)
 #        # data_ dimensions are samples by channels. transpose for MNE.
 #        data_ = data_[start:stop, 1:].T
 #        _mult_cal_one(data, data_, idx, cals, mult)



