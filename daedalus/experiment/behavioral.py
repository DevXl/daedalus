#!/usr/bin/env python
"""
created 2/10/20 

@author DevXl

DESCRIPTION
"""
from . import BaseExperiment
from psychopy.iohub.client import ioHubConnection
from abc import abstractmethod


class EyeTracking(BaseExperiment):

    EXP_TYPE = "EYETRACKING"

    def __init__(self, path):
        super().__init__(path)
        self._hub = ioHubConnection(ioHubConfigAbsPath=self.config_file)
        self.devices = self._hub.devices

    @abstractmethod
    def run(self):
        """Experiment code"""


class PsychoPhysics(BaseExperiment):

    EXP_TYPE = "PSYCHOPHYSICS"

    def __init__(self, path):
        super().__init__(path)


class VirtualReality(BaseExperiment):

    EXP_TYPE = "VIRTUALREALITY"

    def __init__(self, path):
        super().__init(path)

