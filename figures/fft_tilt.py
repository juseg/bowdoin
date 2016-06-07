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
    c = ut.colors[i]

    # read tilt unit tilt
    tiltx = ut.io.load_data('tiltunit', 'tiltx', bh).resample('1H').mean()
    tilty = ut.io.load_data('tiltunit', 'tilty', bh).resample('1H').mean()

    # remove empty columns
    tiltx = tiltx.dropna(axis='columns', how='all').iloc[:,-1]
    tilty = tilty.dropna(axis='columns', how='all').iloc[:,-1]

    # compute tilt velocity
    dt = 1.0/24/365
    tilt = np.arcsin(np.sqrt((np.sin(tiltx).diff()[1:])**2+
                             (np.sin(tilty).diff()[1:])**2))*180/np.pi/dt

    # get longest continuous segment
    tilt = ut.al.longest_continuous(tilt)

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
fig.savefig('fft_tilt')
