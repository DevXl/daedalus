#!/usr/bin/env python
"""
created 2/9/20 

@author DevXl

To calibrate the screens
"""
from psychopy import monitors


def calibrate_monitors(models):

    all_monitors = monitors.getAllMonitors()
