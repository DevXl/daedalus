#!/usr/bin/env python
"""
created 8/18/2020

@author DevXI

"""
import numpy as np
from PyQt5 import QtWidgets
import sys
import pyglet


def to_frame(time: float, refresh_rate: int) -> int:
    """
    Converts time given in milliseconds to number of corresponding frames

    Parameters
    ----------
    time : float
    refresh_rate : int

    Returns
    -------
    int
    """
    return int(time * refresh_rate)


def jitter(time: int, lag) -> float:
    """
    Adds or subtracts some jitter to a time period

    Parameters
    ----------
    time : float
    lag : float
        minimum/maximum amount of jitter

    Returns
    -------
    float
        modified duration
    """
    durations = np.linspace(-lag, lag, num=10)
    time += np.random.choice(durations, 1)

    return time/1000

# TODO: add jitter position function


def get_screens():
    """
    Use pyglet to find screens and their resolution

    Returns
    -------

    """

    pl = pyglet.canvas.get_display()
    screens = pl.get_screens()

    return screens
