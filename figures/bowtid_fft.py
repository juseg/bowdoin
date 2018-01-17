#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 80.0), nrows=3, ncols=3,
                              sharex=True, sharey=True, hspace=2.5, wspace=2.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')
for i, u in enumerate(p):
    ax = grid.flat[i]
    c = 'C%d' % i

    # crop and resample
    ts = p[u].dropna().resample('1H').mean()

    # get longest continuous segment
    ts = ut.al.longest_continuous(ts)

    # compute fft
    freq = np.fft.rfftfreq(ts.shape[-1], 1/24.0)
    rfft = np.fft.rfft(ts.values)
    ampl = np.abs(rfft)
    spow = ampl**2
    gain = 10.0*np.log10(spow)

    # plot
    ax.plot(1/freq[1:], spow[1:], c=c)  # freq[0]=0.0
    ax.set_xscale('log')
    ax.set_yscale('log')

    # add corner tag
    ax.text(0.8, 0.1, u, color=c, transform=ax.transAxes)
    ax.axvline(0.5, c='0.75', lw=0.1, zorder=1)
    ax.axvline(1.0, c='0.75', lw=0.1, zorder=1)

# set axes properties
grid[2, 1].set_xlabel('period (days)')
grid[1, 0].set_ylabel(r'spectral power (m$^2$)', labelpad=0)

# save
ut.pl.savefig(fig)
