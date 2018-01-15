#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import pandas as pd
import scipy.signal as sg
import matplotlib.dates as mdates


# initialize figure
figw, figh = 85.0, 65.0
fig, grid = ut.pl.subplots_mm(figsize=(figw, figh), nrows=9, ncols=1,
                              sharex=True, sharey=False, hspace=1.5, wspace=1.5,
                              left=9.0, right=15.0, bottom=9.0, top=1.5)
cax = fig.add_axes([1-13.5/figw, 9.0/figh, 3.0/figw, 1-10.5/figh])

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')
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
    im = ax.pcolormesh(t.to_pydatetime(), f, gain, cmap='magma',
                       vmin=-60.0, vmax=20.0)

    # add corner tag
    ax.text(0.95, 0.2, u, color=c, transform=ax.transAxes,
            bbox=dict(ec='none', fc='w', alpha=0.75, pad=1))

    # set axes properties
    ax.set_xlim(p.index[0], p.index[-1])
    ax.set_ylim(0.0, 4.0)
    ax.set_yticks([1.0, 3.0])

# add colorbar
cb = fig.colorbar(im, cax=cax, extend='both')
cb.set_label('power spectral density (dB)')

# set axes properties
grid[4].set_ylabel('frequency (day$^{-1})$', labelpad=2)

# save
ut.pl.savefig(fig)
