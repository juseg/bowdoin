# Copyright (c) 2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin deformation paper utils.
"""

import numpy as np
import pandas as pd

# Global parameters
# -----------------

COLOURS = dict(bh1='C0', bh2='C1', bh3='C2', err='0.75')
MARKERS = dict(I='^', P='s', T='o')
DRILLING_DATES = dict(bh1='20140716', bh2='20140717', bh3='20140722')


# Data loading methods
# --------------------

def load(filename):
    """Load preprocessed data file and return data with duplicates removed."""
    data = pd.read_csv(filename, parse_dates=True, index_col='date')
    data = data.groupby(level=0).mean()
    return data


def load_strain_rate(borehole, freq='1D'):
    """
    Return horizontal shear strain rate from tilt relative to a start date
    or between two dates.

    Parameters
    ----------
    borehole: string
        Borehole name bh1 or bh3.
    freq: string
        Frequency to resample average tilts before time differentiation.

    Returns
    -------
    exz: series
        Strain rates in s-1.
    """

    # load borehole data
    prefix = '../data/processed/bowdoin.' + borehole.replace('err', 'bh3')
    tilx = load(prefix+'.inc.tilx.csv').resample(freq).mean()
    tily = load(prefix+'.inc.tily.csv').resample(freq).mean()

    # compute near horizontal shear strain
    exz_x = np.sin(tilx).diff()
    exz_y = np.sin(tily).diff()
    exz = np.sqrt(exz_x**2+exz_y**2)

    # convert to strain rate in a-1
    exz /= pd.to_timedelta(freq).total_seconds()

    # return strain rate
    return exz
