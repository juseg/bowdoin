#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=1, ncols=3,
                              sharex=False, sharey=False, wspace=12.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# for each tilt unit
z = ut.io.load_bowtid_data('depth').iloc[0]
p = ut.io.load_bowtid_data('wlev')['20140827':'20141019']  # all sensors
#p = ut.io.load_bowtid_data('wlev')['20140901':'20150330']  # clean signal
#p = ut.io.load_bowtid_data('wlev')['20150401':'20150930']  # high frequency
p = p.resample('10T').mean().interpolate().diff()[1:]/3.6  # Pa s-1
for i, u in enumerate(p):
    c = 'C%d' % i
    offset = 9-i
    ts = p[u]

    # plot filtered water level
    ax = grid[0]
    (ts+offset).plot(ax=ax, c=c)

    # use first series as reference
    if i == 0:
        tsref = ts

    # plot cross correlation
    ax = grid[1]
    dt = (ts.index[:] - ts.index[0]).total_seconds()/3600.0
    shift = np.concatenate([-dt[:0:-1], dt])
    xcorr = np.correlate(ts, tsref, mode='full')
    xcorr /= 2*xcorr.max()
    ax.plot(shift, xcorr+offset, c=c)

    # find maximum within 24 hours
    idxmax = (xcorr*(abs(shift)<=24.0)).argmax()
    ax.plot(shift[idxmax], xcorr[idxmax]+offset, c=c, marker='o')

    # plot phase shifts
    ax = grid[2]
    ax.plot(shift[idxmax], z[u], c=c, marker='o')
    ax.text(shift[idxmax]+0.1, z[u]-1.0, u, color=c)

# set axes properties
grid[0].set_ylim(-1.0, 10.0)
grid[0].set_ylabel('pressure change ($Pa\,s^{-1}$)')
grid[0].legend(ncol=2, loc='lower right')
grid[1].axvline(0.0, ls=':')
grid[1].set_xlim(-12.0, 12.0)
grid[1].set_ylim(-1.0, 10.0)
grid[1].set_xlabel('phase shift (h)')
grid[1].set_ylabel('cross-correlation')
grid[2].axvline(0.0, ls=':')
grid[2].set_xlim(-2.0, 2.0)
grid[2].invert_yaxis()
grid[2].set_xlabel('phase shift (h)')
grid[2].set_ylabel('depth (m)')

# save
ut.pl.savefig(fig)
