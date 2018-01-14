#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import scipy.signal as sg
import matplotlib.pyplot as plt
import util as ut

start = '2015-06'
end = '2015-09'

# initialize figure
fig, grid = ut.pl.subplots_mm(2, 1, right=15.0, sharex=True)

# select one borehole
bh = 'upper'
c = ut.colors[bh]

# load data
exz = ut.io.load_strain_rate(bh, '2H')[start:end]
depth = ut.io.load_depth('tiltunit', bh).squeeze()
depth_base = ut.io.load_depth('pressure', bh).squeeze()

# ignore two lowest units on upper borehole
if bh == 'upper':
    broken = ['UI02', 'UI03']
    depth.drop(broken, inplace=True)
    exz.drop(broken, axis='columns', inplace=True)

# fit to a Glen's law
n, A = ut.al.glenfit(depth, exz.T)

# calc deformation velocity
vdef = ut.al.vsia(0.0, depth_base, n, A)
vdef = pd.Series(index=exz.index, data=vdef)
time = vdef.index.values
vals = vdef.values

# plot time series on top
ax = grid[0]
ax.plot(time, vals, c=c)
ax.set_ylabel(r'deformation ($m\,a^{-1}$)', labelpad=2)
ax.set_ylim(0.0, 100.0)

# calculate sample frequency
dt = (time[1]-time[0])/pd.to_timedelta('1D')
fs = 1 / dt

# compute spectrogram and corresponding time coordinate
nfft = 48
f, t, spec = sg.spectrogram(vals, nperseg=nfft, fs=fs, noverlap=0)
freq = '%dD' % (nfft/fs)
periods = spec.shape[1]
t = (pd.date_range(time[0], freq=freq, periods=periods) +
     pd.to_timedelta(freq)/2.0)

# log-scale amplitude values
spec = np.log10(spec)

# plot amplitudes
ax = grid[1]
im = ax.pcolormesh(t, f, spec, cmap='Greys', vmin=-2.0, vmax=2.0)

# set log scale in frequency
ax.set_yscale('log')
ax.set_ylim(f[1], f[-1])
ax.set_ylabel('frequency (day$^{-1})$', labelpad=2)

# add colorbar
figw, figh = 85.0, 65.0
cax = fig.add_axes([72.5/figw, 10.0/figh, 2.5/figw, 1-15.0/figh])
cbar = fig.colorbar(im, cax=cax)
cbar.set_label('Amplitude', labelpad=2)

# save
ut.pl.savefig(fig)
