#!/usr/bin/env python2

import pandas as pd
import matplotlib.pyplot as plt

# parameters
boreholes = ['upstream', 'downstream']
colors = ['b', 'r']
lines = [None, None]

# interval to match tilt unit pressure against water level from bottom
wlev_calib_intervals = [['2014-07-18', '2014-07-22'],
                        ['2014-07-29', '2014-08-02']]

# initialize figure
fig, ax = plt.subplots(1, 1)

# for each borehole
for i, bh in enumerate(boreholes):

    # plot pressure sensor water level
    filename = 'data/processed/bowdoin-pressure-%s.csv' % bh
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    wlev = df['wlev'].resample('30T')  # resample and fill with nan
    wlev = wlev[2:]  # remove the first hour corresponding to drilling
    wlev.plot(c=colors[i], lw=2.0)
    lines[i] = ax.get_lines()[-1]  # select last line for the legend

    # subset water level series for calibration
    calint = wlev_calib_intervals[i]
    wlev = wlev[calint[0]:calint[1]]

    # open tilt unit water level data
    filename = 'data/processed/bowdoin-inclino-%s.csv' % bh
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    pcols = [col for col in df.columns if col.startswith('p')]

    # infer unit height above the bedrock from pressure sensor data
    # plot only if there is a good match with pressure sensor data
    for col, tiltwlev in (df[pcols]*9.80665).iteritems():
        diff = tiltwlev[wlev.index]-wlev  # difference over calib interval
        tiltwlev -= diff.mean()  # correct for inferred unit height
        if diff.std() < 1.0:  # std of difference below one meter
            tiltwlev.plot(ax=ax, c='k', alpha=0.2, legend=False)

# set axes properties
ax.set_ylabel('water level (m)')
ax.legend(lines, boreholes)

# save
fig.savefig('timeseries')
