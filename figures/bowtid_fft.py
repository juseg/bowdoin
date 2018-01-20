#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=3, ncols=3,
                              sharex=True, sharey=True, hspace=2.5, wspace=2.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')
for i, u in enumerate(p):
    ax = grid.flat[i]
    c = 'C%d' % i

    # crop and resample
    ts = p[u]['2015-04':'2015-09'].interpolate()  # 6Mx10T, 2 peaks at 12h

    # only nulls, add text
    if ts.notnull().sum() == 0:
        ax.set_xlim(grid.flat[0].get_xlim())  # avoid reshape axes
        ax.set_ylim(grid.flat[0].get_ylim())  # avoid reshape axes
        ax.text(0.5, 0.5, 'no data', color='0.5', ha='center', transform=ax.transAxes)

    # else compute fft
    else:
        freq = np.fft.rfftfreq(ts.shape[-1], 1/24.0/6.0)
        rfft = np.fft.rfft(ts.values)
        ampl = np.abs(rfft)
        spow = ampl**2
        gain = 10.0*np.log10(spow)

        # and plot
        ax.plot(1/freq[1:], spow[1:], c=c)  # freq[0]=0.0
        ax.set_xscale('log')
        ax.set_yscale('log')

        # add vertical lines
        for x in [0.5, 0.5*30/29, 1.0, 14.0]:  # FIXME
            ax.axvline(x, c='0.75', lw=0.1, zorder=1)

    # add corner tag
    ax.text(0.9, 0.1, u, color=c, transform=ax.transAxes)

## zoom in around 12--24h
#ax.set_xlim(0.35, 1.35)
#ax.set_ylim(10**0.5, 10**7.5)

## zoom in around 12h
#ax.set_xlim(0.45, 0.6)
#ax.set_ylim(10**0.5, 10**7.5)

# set axes properties
grid[2, 1].set_xlabel('period (days)')
grid[1, 0].set_ylabel(r'spectral power (m$^2$)', labelpad=0)

# save
ut.pl.savefig(fig)
