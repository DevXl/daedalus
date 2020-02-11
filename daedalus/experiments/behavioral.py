#!/usr/bin/env python
"""
created 2/10/20 

@author DevXl

DESCRIPTION
"""
from . import BaseExperiment
from psychopy.iohub.client import connect


class EyeTracking(BaseExperiment):

    EXP_TYPE = "EyeTracking"

    def __init__(self, path):
        super().__init__(path)
        self.hub = None
        self.devices = None


    def
