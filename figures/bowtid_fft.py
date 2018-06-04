#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=3, ncols=3,
                              sharex=True, sharey=True, hspace=2.5, wspace=2.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# get freezing dates
t = ut.io.load_bowtid_data('temp')['20140717':].resample('1H').mean()
df = abs(t-(0.1*t.max()+0.9*t.min())).idxmin()  # date of freezing

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')['2014-07':]
for i, u in enumerate(p):
    ax = grid.flat[i]
    c = 'C%d' % i

    # crop and resample
    ts = p[u][df[u]:].dropna().resample('1H').mean().interpolate().diff()[1:]/3.6

    # only nulls, add text
    if ts.notnull().sum() == 0:
        ax.set_xlim(grid.flat[0].get_xlim())  # avoid reshape axes
        ax.set_ylim(grid.flat[0].get_ylim())  # avoid reshape axes
        ax.text(0.5, 0.5, 'no data', color='0.5', ha='center', transform=ax.transAxes)

    # else compute fft
    else:
        freq = np.fft.rfftfreq(ts.shape[-1], 1.0)
        rfft = np.fft.rfft(ts.values)
        ampl = np.abs(rfft)
        spow = ampl**2
        gain = 10.0*np.log10(spow)

        # and plot
        ax.plot(1/freq[1:], spow[1:], c=c)  # freq[0]=0.0
        ax.set_xscale('log')
        ax.set_yscale('log')

        # add vertical lines
        for x in [12.0, 12.0*30/29, 24.0, 24.0*14]:
            ax.axvline(x, c='0.75', lw=0.1, zorder=1)

    # add corner tag
    ax.text(0.9, 0.1, u, color=c, transform=ax.transAxes)

# set axes properties
grid[2, 1].set_xlabel('period (h)')
grid[1, 0].set_ylabel(r'spectral power ($Pa^2 s^{-2}$)', labelpad=0)

# save
ut.pl.savefig(fig)

## save different zooms
#ut.pl.savefig(fig, suffix='_z0')
#ax.set_xscale('linear')
#ax.set_xticks([12.0, 24.0])
#ax.set_xlim(6.0, 30.0)
#ut.pl.savefig(fig, suffix='_z1')
#ax.set_xticks([12.0, 12.0*30/29])
#ax.set_xlim(11.5, 13.0)
#ut.pl.savefig(fig, suffix='_z2')
