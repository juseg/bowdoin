#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[1-i]
    c = ut.colors[bh]

    # read pressure sensor water level
    ts = ut.io.load_data('pressure', 'wlev', bh).squeeze().resample('30T').mean()
    ts = ts.iloc[2:]  # remove the first hour corresponding to drilling

    # get longest continuous segment
    ts = ut.al.longest_continuous(ts)

    # compute fft
    freq = np.fft.rfftfreq(ts.shape[-1], 30.0/60)
    rfft = np.fft.rfft(ts.values)
    gain = 20*np.log10(np.abs(rfft))  # gain = 10*np.log10(power)

    # plot
    ax.plot(freq, gain, c=c)

    # set title
    ax.set_ylabel('power (dB) ' + bh)

# save
grid[0].set_title('water level FFT')
grid[1].set_xlabel(r'frequency (h$^{-1}$)')
fig.savefig('fft_wlev')
