#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
from scipy import signal

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(85.0, 65.0),
                            left=12.0, right=1.5, bottom=9.0, top=1.5)

# prepare filter
n = 2  # filter order
w = 1/24.  # cutoff frequency
b, a = signal.butter(n, w, 'high') 

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')
for i, u in enumerate(p):
    c = 'C%d' % i

    # crop, resample, and interpolate
    ts = p[u].dropna().resample('1H').mean().interpolate()

    # apply filter in both directions
    ts[:] = signal.filtfilt(b, a, ts) + 10 - i

    # plot
    ts.plot(ax=ax)

# set axes properties
ax.set_ylim(1.0, 11.0)
ax.set_ylabel('pressure head (m w.e.)')
ax.legend(ncol=3)

# save
ut.pl.savefig(fig)
