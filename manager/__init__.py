#!/usr/bin/env python
"""
created 2/25/2020

@author devxl

"""


class Session:

    def __init__(self):
        pass

    def subject_session_info(self):
        """show a gui to input experiment specific info for each session"""

        session_info = {}
        session_dlg = gui.Dlg(title="Session information")
        session_dlg.addFixedField(self.)
        exp_specific_info = self.CONFIG["subject"]
        for param in exp_specific_info.values():
            session_dlg.addField(param["description"], choices=list(param["init_vals"]))



class Task:

    def __init__(self):
        pass


class Data:

    def __init__(self):
        pass

    def register_subject(self):
        """
        Show a gui to enter new subject's information
        """
        new_subj_info = {}

        # information that's not specific to an experiment
        new_subj_dlg = gui.Dlg(title="New Participant Information", labelButtonOK="Register", labelButtonCancel="Cancel")
        new_subj_dlg.addField("Student ID:")
        new_subj_dlg.addField("Initials:", tip="lowercase separated by . (e.g. k.m.z)")
        new_subj_dlg.addField("Age:", choices=list(range(17, 51)))
        new_subj_dlg.addField("Gender:", ["Male", "Female", "NB"])
        new_subj_dlg.addField("Handedness:", ["Left", "Right"])
        new_subj_dlg.addFixedField("Registration Date:", str(date.today()))
        new_subj_dlg.addFixedField("Registration Experiment:", self.NAME)

        user_info = new_subj_dlg.show()
        if new_subj_dlg.OK:

            # add the input data to the subject dictionary to write to file later
            new_subj_info["ID"] = uuid.uuid4().hex[:8]  # generate random ID
            new_subj_info["sID"] = user_info[0]
            new_subj_info["initials"] = user_info[1]
            new_subj_info["age"] = user_info[2]
            new_subj_info["gender"] = user_info[3][0]
            new_subj_info['hand'] = user_info[4]
            new_subj_info['date_added'] = str(user_info[5])
            new_subj_info['experiment'] = user_info[6]

        else:
            self._close()

        return new_subj_info