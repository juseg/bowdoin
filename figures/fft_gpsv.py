#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import util as ut

d0 = '2015-04-01'

# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)
c = ut.colors[2]

# read GPS velocity data
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T')

# get longest continuous segment
ts = ut.io.longest_continuous(ts)

# compute fft
freq = np.fft.rfftfreq(ts.shape[-1], 15.0/60)
rfft = np.fft.rfft(ts.values)
gain = 20*np.log10(np.abs(rfft))  # gain = 10*np.log10(power)

# plot
ax.plot(freq, gain, c=c)

# set title
ax.axvline(1/24., c='k', lw=0.1)
ax.set_ylabel('power (dB)')

# save
ax.set_title('GPS velocity FFT')
ax.set_xlabel(r'frequency (h$^{-1}$)')
fig.savefig('fft_gpsv')
