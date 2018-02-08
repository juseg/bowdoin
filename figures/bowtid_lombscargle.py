#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy.signal as sg

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=3, ncols=3,
                              sharex=True, sharey=True, hspace=2.5, wspace=2.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# somehow the periodograms show nothing without filtering
# FIXME: filter irregular signal to avoid resampling
n = 2  # filter order
w = 2.0/6/24  # cutoff frequency
b, a = sg.butter(n, w, 'high')

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')['2015-04':'2015-09'].resample('10T').mean()
for i, u in enumerate(p):
    ax = grid.flat[i]
    c = 'C%d' % i

    # crop
    ts = p[u].dropna()

    # only nulls, add text
    if ts.notnull().sum() == 0:
        ax.set_xlim(grid.flat[0].get_xlim())  # avoid reshape axes
        ax.set_ylim(grid.flat[0].get_ylim())  # avoid reshape axes
        ax.text(0.5, 0.5, 'no data', color='0.5', ha='center', transform=ax.transAxes)

    # else compute fft
    else:
        ts[:] = sg.filtfilt(b, a, ts)
        x = (ts.index - ts.index[0]).total_seconds()/3600/24
        y = ts.values
        periods = np.logspace(-0.5, 0.5, 1001)
        frequencies = 1.0 / periods
        angfreqs = 2 * np.pi * frequencies
        pgram = sg.lombscargle(x, y, angfreqs, normalize=False)

        # and plot
        ax.plot(periods, pgram, c=c)  # freq[0]=0.0
        ax.set_xscale('log')
        ax.set_yscale('log')

        # add vertical lines
        for x in [0.5, 0.5*30/29, 1.0]:
            ax.axvline(x, c='0.75', lw=0.1, zorder=1)

    # add corner tag
    ax.text(0.9, 0.1, u, color=c, transform=ax.transAxes)

# set axes properties
grid[2, 1].set_xlabel('period (day)')
grid[1, 0].set_ylabel(r'spectral power (m$^2$)', labelpad=0)

# save
ut.pl.savefig(fig)
