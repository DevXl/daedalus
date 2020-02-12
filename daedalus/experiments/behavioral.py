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

    EXP_TYPE = "EyeTracking"

    def __init__(self, path):
        super().__init__(path)
        self._hub = ioHubConnection(ioHubConfigAbsPath=self.config_file)
        self.devices = self._hub.devices

    @abstractmethod
    def run(self):
        """Experiment code"""


class PsychoPhysics(BaseExperiment):

    def __init__(self, path):
        super().__init__(path)
