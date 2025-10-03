#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import bowdef_utils

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(bowdef_utils.boreholes):
    ax = grid[i]
    c = bowdef_utils.colors[bh]

    # read tilt unit tilt
    tiltx = bowdef_utils.load_data('tiltunit', 'tiltx', bh).resample('1h').mean()
    tilty = bowdef_utils.load_data('tiltunit', 'tilty', bh).resample('1h').mean()

    # remove empty columns
    tiltx = tiltx.dropna(axis='columns', how='all').iloc[:,-1]
    tilty = tilty.dropna(axis='columns', how='all').iloc[:,-1]

    # compute tilt velocity
    dt = 1.0/24/365
    tilt = np.arcsin(np.sqrt((np.sin(tiltx).diff()[1:])**2+
                             (np.sin(tilty).diff()[1:])**2))*180/np.pi/dt

    # get longest continuous segment
    tilt = bowdef_utils.longest_continuous(tilt)

    # compute fft
    freq = np.fft.rfftfreq(tilt.shape[-1], 10.0/60)
    rfft = np.fft.rfft(tilt.values)
    gain = 20*np.log10(np.abs(rfft))  # gain = 10*np.log10(power)

    # plot
    ax.plot(freq, gain, c=c)

    # set title
    ax.set_xlim(0.0, 60.0/10/2)
    ax.set_ylabel('power (dB) ' + bh)

# save
grid[0].set_title('tilt velocity FFT')
grid[1].set_xlabel(r'frequency (h$^{-1}$)')
bowdef_utils.savefig(fig)
