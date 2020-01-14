#!/usr/bin/env python
"""
created 1/13/20 

@author DevXl

DESCRIPTION
"""
import numpy as np
import pandas as pd
import os
import glob


def read_files(file_type, known_path=""):
    """
    Fetches csv files

    Parameters
    ----------
    file_type: (string) psycphys or log data
    known_path: (string) known path of the data files

    Returns
    -------
    data_files: (list) containing path to all data or log files
    """
    # check if the path is known
    if len(known_path) > 0:

        # if the path is passed then files are in that directory
        data_path = known_path
    else:

        # if path is not known then psychophysics data is in "current_dir/data/psycphys" and log data
        # in "current_dir/data/log"
        data_path = os.path.join(os.getcwd(), "data/{}".format(file_type))

    # look for all csv files in that directory and put the paths in a list as strings

    data_files = glob.glob(data_path + "/*.csv")

    return data_files


def to_pandas(files):
    """
    Puts all files in a pandas dataframe

    Parameters
    ----------
    files: (list) containing strings of all data files

    Returns
    -------
    df: (Pandas.DataFrame) raw data of all subjects
    """

    # go through the input list of paths and add the read the data with pandas and add subjects' dfs to a list
    pd_lst = [pd.read_csv(subj_frame, index_col=None, header=0) for subj_frame in files]

    # merge all the individual subject dfs into one big df
    df = pd.concat(pd_lst, axis=0, ignore_index=True, sort=False)

    return df


def basic_prep(df, save=False):
    """
    Initial preprocessing including replacing missing values,

    Parameters
    ----------
    df: (Pandas.DataFrame) dataframe we want to preprocess

    Returns
    -------
    prep_df: (Pandas.DataFrame) preprocessed dataframe!
    """
    # replace missing values with NaNs
    df = df.replace(to_replace="--", value=np.nan)

    # if there's a date column save the dates and subject-names as tuples in a list and get rid of it
    subj_dates = []

    for idx, date in df.date.unique():
        subj_dates.append((df["participant"][idx]), date)

    df = df[~df["date"]]

    # remove the trials that did not run successfully and remove the ran column
    df = df[df["ran"] == 1]
    df = df[~df["ran"]]

    # remove the order column (useless if we have TrialNumber)
    if df["TrialNumber"]:
        df = df[~df["order"]]