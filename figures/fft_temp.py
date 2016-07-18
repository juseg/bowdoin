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

    # read lowermost thermistor string temperature
    ts = ut.io.load_data('thstring', 'temp', bh).iloc[:, 0].resample('30T').mean()

    # get longest continuous segment
    ts = ut.al.longest_continuous(ts)

    # compute fft
    freq = np.fft.rfftfreq(ts.shape[-1], 30.0/60)
    rfft = np.fft.rfft(ts.values)
    gain = 20*np.log10(np.abs(rfft))  # gain = 10*np.log10(power)

    # plot
    ax.plot(freq, gain, c=c)

    # set title
    ax.axvline(1/24., c='k', lw=0.1)
    ax.set_ylabel('power (dB) ' + bh)

# save
grid[0].set_title('bottom temperature FFT')
grid[1].set_xlabel(r'frequency (h$^{-1}$)')
fig.savefig('fft_temp')
