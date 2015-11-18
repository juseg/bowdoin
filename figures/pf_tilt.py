#!/usr/bin/env python2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import util as ut
import scipy.optimize


def powerfit(x, y, deg, **kwargs):
    logx = np.log(x)
    logy = np.log(y)
    p = np.polyfit(logx, logy, deg, **kwargs)
    return p

# dates to plot
start = '2014-11-01'
end = '2015-07-01'

# initialize figure
fig, grid = plt.subplots(1, 2, sharey=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[i]

    # read data values
    tiltx = ut.io.load_data('tiltunit', 'tiltx', bh)
    tilty = ut.io.load_data('tiltunit', 'tilty', bh)
    depth = ut.io.load_depth('tiltunit', bh).squeeze()
    depth_base = ut.io.load_depth('pressure', bh).squeeze()

    # take daily means for start and end values
    tx0 = tiltx[start].mean()
    ty0 = tilty[start].mean()
    tx1 = tiltx[end].mean()
    ty1 = tilty[end].mean()

    # compute deformation rate in horizontal plane
    exz_x = np.sin(tx1)-np.sin(tx0)
    exz_y = np.sin(ty1)-np.sin(ty0)
    exz = np.sqrt(exz_x**2+exz_y**2)

    # remove null values
    notnull = exz.notnull()
    depth = depth[notnull]
    exz = exz[notnull]

    # fit to a power law with C = A * (rho*g*sin(alpha))**n
    n, C = powerfit(depth, exz, 1)

    # plot deformation profile
    depth_fit = np.linspace(0.0, depth_base, 11)
    e_fit = np.exp(C) * depth_fit**n
    v_fit = 2*np.exp(C)/(n+1) * (depth_base**(n+1) - depth_fit**(n+1))
    v_obs = 2*np.exp(C)/(n+1) * (depth_base**(n+1) - depth**(n+1))

    # plot velocity profiles
    ax.plot(v_fit, depth_fit, c=c)
    ax.fill_betweenx(depth_fit, 0.0, v_fit, color=c, alpha=0.2)
    ax.set_title(bh)

    # add velocity arrows
    for d, v in zip(depth, v_obs):
        ax.arrow(0.0, d, v, 0.0, fc='none', ec=c,
                 head_width=5.0, head_length=1.0, length_includes_head=True)

    # add tilt arrows
    ax.quiver(v_obs, depth, -exz*2, np.sqrt(1-(2*exz)**2),
              angles='xy', scale=5.0)

    # add horizontal lines
    ax.axhline(0.0, c='k')
    ax.axhline(depth_base, c='k')
    ax.set_ylim(300.0, 0.0)
    ax.set_xlim(25.0, 0.0)

# save
fig.savefig('pf_tilt')
