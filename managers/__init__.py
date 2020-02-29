#!/usr/bin/env python
"""
created 2/25/2020

@author devxl

"""
from psychopy import gui
import uuid
import sys
import pandas as pd
from datetime import date


class SessionManager:

    def __init__(self, experiment, data_dir):

        self.EXP = experiment
        self.DATA_DIR = data_dir
        self.SUBJECT = {}
        _meta_file = self.DATA_DIR / "participants.tsv"
        self.metadata = pd.read_csv(_meta_file, sep="\t")

    def initiate_session(self, params):
        """start a new session of the experiment"""

        _subject = self._choose_subject()
        session = 0
        if _subject == 'new':
            general_info = self._register_subject()
        else:
            general_info = _subject
            session = _subject['sessions_completed'][-1] + 1

        session_info = self._get_session_info(session_num=session, extra_params=params)

        self.SUBJECT["ID"] = general_info.ID.item()
        self.SUBJECT["session"] = session
        self.SUBJECT[""]

    def _choose_subject(self):
        """show a gui to choose a subject for this session or register a new one"""

        _initials = self.metadata.name.tolist()  # subjects' initials
        _sids = self.metadata.sID.tolist()  # subjects' student ids

        # for the sake of gui selection
        _initials.insert(0, 'Select')
        _sids.insert(0, 'Select')

        # choose subject dialogue
        choose_subj_dlg = gui.Dlg(title=self.EXP, labelButtonOK="Next", labelButtonCancel="Register new participant")
        choose_subj_dlg.addText("Choose a participant by Initials or ID", color="Blue")
        choose_subj_dlg.addField("Initials:", choices=_initials)
        choose_subj_dlg.addField("Student ID:", choices=_sids)

        _session_subject = None
        selected = False
        while not selected:

            choose_subj_info = choose_subj_dlg.show()
            if choose_subj_dlg.OK:
                # TODO: check for the match between initials and ID

                if choose_subj_info[0] != 'Select':
                    _session_subject = self.metadata[self.metadata.name == choose_subj_info[0]]
                    selected = True
                elif choose_subj_info[1] != 'Select':
                    _session_subject = self.metadata[self.metadata.sID == choose_subj_info[1]]
                    selected = True
                else:
                    selected = False

            else:
                _session_subject = 'new'
                selected = True

        return _session_subject

    def _register_subject(self):
        """register a new subject (not specific to the experiment)"""

        new_subj_info = {}

        # information that's not specific to an experiment
        new_subj_dlg = gui.Dlg(title="New Participant Information", labelButtonOK="Register",
                               labelButtonCancel="Cancel")
        new_subj_dlg.addField("Student ID:")
        new_subj_dlg.addField("Initials:", tip="lowercase separated by . (e.g. k.m.z)")
        new_subj_dlg.addField("Age:", choices=list(range(17, 51)))
        new_subj_dlg.addField("Gender:", ["Male", "Female", "NB"])
        new_subj_dlg.addField("Handedness:", ["Left", "Right"])
        new_subj_dlg.addFixedField("Registration Date:", str(date.today()))
        new_subj_dlg.addFixedField("Registration Experiment:", self.EXP)

        _user_input = new_subj_dlg.show()
        if new_subj_dlg.OK:

            # add the input data to the subject dictionary to write to file later
            new_subj_info["ID"] = uuid.uuid4().hex[:8]  # generate random ID
            new_subj_info["sID"] = _user_input[0]
            new_subj_info["name"] = _user_input[1]
            new_subj_info["age"] = _user_input[2]
            new_subj_info["gender"] = _user_input[3][0]
            new_subj_info['hand'] = _user_input[4]
            new_subj_info['date_added'] = str(_user_input[5])
            new_subj_info['experiment'] = _user_input[6]
            new_subj_info['sessions_completed'] = []

        else:
            sys.exit()

        new_sub_df = pd.DataFrame(new_subj_info)
        return new_sub_df

    def _get_session_info(self, session_num, extra_params):
        """show a gui to input experiment specific info for each session"""

        session_info = {}
        session_dlg = gui.Dlg(title="Session information")
        session_dlg.addFixedField("Participant:", self.SUB['name'].item())
        session_dlg.addFixedField("Student ID:", self.SUB['sID'].item())
        session_dlg.addFixedField("Session:", session_num)

        for param in extra_params.values():
            session_dlg.addField(param["description"], choices=list(param["init_vals"]))

        _user_input = session_dlg.show()
        if session_dlg.OK:

            k = 3
            for key in extra_params.keys():
                session_info[key] = _user_input[k]
                k += 1
        else:
            sys.exit()

        return session_info


class TaskManager:

    def __init__(self):
        pass


class DataManager:

    def __init__(self):
        pass



    def load_subject(self, name="all"):
        """loads a specific or all subjects"""

        sub_df = pd.read_csv()