#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import util as ut


def powerfit(x, y, deg, **kwargs):
    logx = np.log(x)
    logy = np.log(y)
    p = np.polyfit(logx, logy, deg, **kwargs)
    return p

# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[i]

    # read tilt unit tilt
    tiltx = ut.io.load_data('tiltunit', 'tiltx', bh).resample('1D')
    tilty = ut.io.load_data('tiltunit', 'tilty', bh).resample('1D')
    depth = ut.io.load_depth('tiltunit', bh).squeeze()
    depth_base = ut.io.load_depth('pressure', bh).squeeze()

    # compute horizontal shear rate
    dt = 1.0/365
    exz_x = np.sin(tiltx).diff()
    exz_y = np.sin(tilty).diff()
    exz = np.sqrt(exz_x**2+exz_y**2)/dt

    # ignore two lowest units on upstream borehole
    if bh == 'upstream':
        broken = ['unit02', 'unit03']
        depth.drop(broken, inplace=True)
        exz.drop(broken, axis='columns', inplace=True)

    # fit to a power law with exp(C) = A * (rhoi*g*sin(alpha))**n
    g = 9.80665     # gravity
    rhoi = 910.0    # ice density
    sina = 0.03     # FIXME: approx. value from MEASURES
    n, C = powerfit(depth, exz.T, 1)
    A = np.exp(C) / (rhoi*g*sina)**n

    # calc deformation velocity
    vdef = 2*np.exp(C)*depth_base**(n+1)/(n+1)
    vdef = pd.Series(index=exz.index, data=vdef)

    # plot
    vdef.plot(ax=ax, c=c, label=bh)

# set labels
ax.set_ylabel(r'deformation velocity ($m\,a^{-1}$)')
ax.set_ylim(20.0, 60.0)
ax.legend()

# save
fig.savefig('ts_tilt_dvel')
