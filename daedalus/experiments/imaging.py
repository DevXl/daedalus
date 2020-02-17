#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created at 2/16/20
@author: devxl

Imaging studies: EEG and fMRI
"""
from abc import ABC

from . import BaseExperiment


class EEG(BaseExperiment, ABC):

    def __init__(self, name, path):
        super().__init__(name, path)


class FMRI(BaseExperiment, ABC):

    def __init__(self, name, path):
        super().__init__(name, path)