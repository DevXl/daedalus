#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created at 2/19/20
@author: devxl

Handle subject registration and data
"""
import uuid
from psychopy import gui


class BaseSubject:

    def __init__(self, name):
        self._name = name
        self._id = uuid.uuid4().hex[:8]

    def lookup_subject(self, ids: List = []):
        """give options to retrieve data from a past subject or to register a new one"""
        choose_dlg = gui.Dlg(title="Participant", labelButtonOK="Lookup", labelButtonCancel="Register new")
        choose_dlg.addText("Choose the participant for this session:")
        choose_dlg.addField("", ids)


    def register_subject(self):
        """
        Show a gui to enter new subject's information
        """
        new_subj_dlg = gui.Dlg(title="New Participant Information", labelButtonOK="Register", labelButtonCancel="Cancel")

        # two kinds of keys in subject parameters file: fixed and extra
        # fixed keys don't have description (they're pretty obvious)
        for key, val in self.PARAMS["SUBJ"]["fixed"].items():
            if isinstance(val, list):
                new_subj_dlg.addField(key, choices=val)
            else:
                new_subj_dlg.addField(key, val)

        # extras should have description TODO: check for this at startup
        for key, val in self.PARAMS["SUBJ"]["extra"].keys():
            if isinstance(val["init_vals"], list):
                new_subj_dlg.addField(val["description"], choices=val["init_vals"])
            else:
                new_subj_dlg.addField(val["description"], val["init_vals"])

        self.DATA["session"] = new_subj_dlg.show()
        if new_subj_dlg.OK:

            # write subject to meta files
            subj_meta_df = pd.read_csv(self.FILES["SUBJ_META"])
            exp_meta_df = pd.read_csv(self.FILES["EXP_META"])

            subj_meta_df



class People:
    """
    Participants for behavioral and imaging studies
    """
    def __init__(self, name: str):
        self._name = name
        self._id = uuid.uuid4().hex[:4]

