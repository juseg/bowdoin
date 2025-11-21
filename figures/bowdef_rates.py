#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation tilt rates."""

import absplots as apl
import numpy as np
import pandas as pd

import bowstr_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 15, 'right': 2.5, 'bottom': 10, 'top': 2.5})

    # plot tilt rate
    tilx = bowstr_utils.load(variable='tilx').resample('1D').mean().diff()
    tily = bowstr_utils.load(variable='tily').resample('1D').mean().diff()
    tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
    tilt = tilt[tilt.index >= '2014-07-17']
    tilt *= 3600 * 24 * 365.25 / pd.to_timedelta('1D').total_seconds()
    tilt.plot(ax=ax, xlabel='', ylabel=r'tilt rate ($°\,a^{-1}$)')

    # set axes properties
    ax.legend(loc='upper right', ncols=2)
    ax.set_xlim('20140701', '20170801')
    ax.set_ylim(-1, 21)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
