#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[i]

    # plot thermistor string temperature (in ice only)
    df = ut.io.load_data('thstring', 'temp', bh)
    df = df[df.columns[df.max()<5.0]]
    df.plot(ax=ax, c=c, legend=False)

    # identify freezing times
    for d in df.diff().abs().idxmax():
        ax.axvline(d, c=c, ls='--')

    # plot tilt unit temperature
    df = ut.io.load_data('tiltunit', 'temp', bh)
    df.plot(ax=ax, c='0.75', legend=False)

    # identify freezing times
    for d in df.diff().abs().idxmax():
        ax.axvline(d, c='0.75', ls='--')

    # plot pressure sensor temperature
    ts = ut.io.load_data('pressure', 'temp', bh)
    ts.plot(ax=ax, c='k', legend=False)

    # set title
    ax.set_ylabel('temperature ' + bh)

# save
fig.savefig('ts_temp')
