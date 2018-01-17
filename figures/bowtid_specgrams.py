#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import pandas as pd
import scipy.signal as sg
import matplotlib.colors as mcolors


# initialize figure
figw, figh = 150.0, 75.0
fig, grid = ut.pl.subplots_mm(figsize=(figw, figh), nrows=9, ncols=1,
                              sharex=True, sharey=False, hspace=2.5,
                              left=10.0, right=15.0, bottom=10.0, top=2.5)
cax = fig.add_axes([1-12.5/figw, 10.0/figh, 2.5/figw, 1-12.5/figh])

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')
norm = mcolors.LogNorm(1e-6, 1e2)
for i, u in enumerate(p):
    ax = grid.flat[i]
    c = 'C%d' % i

    # crop, resample, and interpolate
    ts = p[u].dropna().resample('1H').mean().interpolate()
    ts.plot(ax=ax, visible=False)  # prepare axes in pandas format

    # calculate sample frequency
    dt = (ts.index[1]-ts.index[0])/pd.to_timedelta('1D')
    fs = 1 / dt

    # compute spectrogram and corresponding time coordinate
    nfft = 16*24
    f, t, spec = sg.spectrogram(ts, nperseg=nfft, fs=fs, noverlap=0)
    freq = '%dD' % (nfft/fs)
    periods = spec.shape[1]
    t = (pd.date_range(ts.index[0], freq=freq, periods=periods) +
         pd.to_timedelta(freq)/2.0)

    # log-scale amplitude values
    gain = 10.0*np.log10(spec)

    # plot amplitudes
    im = ax.pcolormesh(t.to_pydatetime(), f, spec, cmap='Greys', norm=norm)

    # add corner tag
    ax.text(0.95, 0.2, u, color=c, transform=ax.transAxes,
            bbox=dict(ec='none', fc='w', alpha=0.75, pad=1))

    # set axes properties
    ax.set_xlim(p.index[0], p.index[-1])
    ax.set_ylim(0.0, 4.0)
    ax.set_yticks([1.0, 3.0])

# add colorbar
cb = fig.colorbar(im, cax=cax, extend='both')
cb.set_label(r'power spectral density (m${^2}$ day)', labelpad=0)

# set axes properties
grid[4].set_ylabel('frequency (day$^{-1})$')

# save
ut.pl.savefig(fig)
