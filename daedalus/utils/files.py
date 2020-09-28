#!/usr/bin/env python
"""
created 8/5/2020

@author DevXI

"""
from pathlib import Path


def check_dir(*args: Path) -> dict:
    """Checks whether directories exist or not and if they have the appropriate files"""

    report = {}
    for d in args:
        if d.exists():
            report[d] = (True, '{} directory already exists.'.format(d))
        else:
            try:
                d.mkdir(exist_ok=False)
                report[d] = (True, 'I made the {} directory for you.'.format(d))
            except Exception as e:
                report[d] = (False, 'I could not make the {} directory because {}.'.format(d, e))

    return report


def check_file(*args: Path) -> dict:
    """
    Checks whether file or files exist or not.
    """

    report = {}
    for f in args:
        if f.exists():
            report[f] = (True, '{} file already exists.'.format(f))
        else:
            # TODO: if a file doesn't exist, make it and populate it with defaults.
            report[f] = (False, 'I did not find the {} file'.format(f))

    return report









