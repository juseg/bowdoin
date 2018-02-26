#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import pandas as pd

# date for temperature profile
d = '2014-09-02'

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=1, ncols=2,
                            sharex=True, sharey=False, wspace=10.0,
                            left=10.0, right=2.5, bottom=10.0, top=2.5)

# loop on boreholes
for bh, c in zip(ut.bowtem_bhnames, ut.bowtem_colours):

    # load data
    t, z, b = ut.io.load_bowtem_data(bh)
    t = t['2014-07':'2016-12']
    t = t.resample('2D').mean()

    # extract days to freezing
    #d0 = t['2014-07'].notnull().idxmax()  # start of record
    d0 = pd.to_datetime(ut.bowtem_bhdates[int(bh[-1])-1])  # drilling dates
    df = t.diff().idxmin()  # date of freezing
    df[df == t.index[1]] = np.nan
    df = (df-d0).dt.total_seconds()/(24*3600)  # days to freezing

    # temperature during freezing
    #tf = pd.Series(index=df.index, data=[t.loc[df[k], k] for k in df.index])

    # plot
    for s, m in zip(ut.bowtem_sensors, ut.bowtem_markers):
        cols = (df.notnull() * df.index.str[1] == s)
        if cols.sum() > 0:
            ax[0].plot(df[cols], t.loc[d, cols].mean().T, c=c, marker=m, ls='')
            ax[1].plot(df[cols], z[cols], c=c, marker=m, ls='')
    ax[1].axhline(b, c=c, lw=0.5)

# set axes properties
ax[0].set_xscale('log')
ax[0].set_xlabel('days to freezing')
ax[0].set_ylabel(u'temperature (°C)')
ax[1].set_xlabel('days to freezing')
ax[1].set_ylabel('depth (m)')
ax[1].axhline(0.0, c='k', lw=0.5)
ax[1].invert_yaxis()

# save
ut.pl.savefig(fig)
