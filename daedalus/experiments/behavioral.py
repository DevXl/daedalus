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

    def __init__(self, path, **kwargs):
        super().__init__(path)
        kwagrs["iohub_config_name"] = self.config_file
        self._hub = connect.launchHubServer(kwargs)
        self.devices = self._hub.devices
        
        
            
        
        
