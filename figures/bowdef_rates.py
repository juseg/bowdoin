#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin strain rate time series."""

import absplots as apl
import numpy as np
import pandas as pd

import bowstr_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 15, 'right': 2.5, 'bottom': 10, 'top': 2.5})

    # plot strain rate as sin(tilt) = sqrt(1-(cos(tx)*cos(ty))**2)
    tilx = bowstr_utils.load(variable='tilx').resample('1D').mean().diff()
    tily = bowstr_utils.load(variable='tily').resample('1D').mean().diff()
    # FIXME wrong formula and a factor half is missing! strain = 0.5*tan(tilt)
    strain = (1 - (np.cos(tilx) * np.cos(tily)) ** 2) ** 0.5
    strain = strain[strain.index >= '2014-07-17']
    strain *= 3600 * 24 * 365.25 / pd.to_timedelta('1D').total_seconds()
    strain.plot(ax=ax, xlabel='', ylabel=r'strain rate ($a^{-1}$)')

    # set axes properties
    ax.legend(loc='upper right', ncols=2)
    ax.set_xlim('20140701', '20170801')
    ax.set_ylim(-0.01, 0.33)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
