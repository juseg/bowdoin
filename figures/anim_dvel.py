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
start = '2014-07-01'
end = '2015-08-01'

# for each borehole
exz = [None, None]
depth = [None, None]
depth_base = [None, None]
fitparams = [None, None]
for i, bh in enumerate(ut.boreholes):

    # read tilt unit tilt
    tiltx = ut.io.load_data('tiltunit', 'tiltx', bh).resample('1D')[start:end]
    tilty = ut.io.load_data('tiltunit', 'tilty', bh).resample('1D')[start:end]
    depth[i] = ut.io.load_depth('tiltunit', bh).squeeze()
    depth_base[i] = ut.io.load_depth('pressure', bh).squeeze()

    # compute horizontal shear rate
    dt = 1.0/365
    exz_x = np.sin(tiltx).diff()
    exz_y = np.sin(tilty).diff()
    exz[i] = np.sqrt(exz_x**2+exz_y**2)/dt

    # ignore two lowest units on upstream borehole
    if bh == 'upstream':
        broken = ['unit02', 'unit03']
        depth[i].drop(broken, inplace=True)
        exz[i].drop(broken, axis='columns', inplace=True)

    # fit to a power law with exp(C) = A * (rhoi*g*sin(alpha))**n
    g = 9.80665     # gravity
    rhoi = 910.0    # ice density
    sina = 0.03     # FIXME: approx. value from MEASURES
    n, C = powerfit(depth[i], exz[i].T, 1)
    fitparams[i] = pd.DataFrame(index=exz[i].index, data={'n': n, 'C': C})

# contatenate
fitparams = pd.concat(fitparams, axis=1, keys=ut.boreholes)

# initialize figure
fig, grid = ut.pl.subplots_mm(nrows=1, ncols=2, sharex=True, sharey=True,
                             left=10.0, bottom=10.0, right=5.0, top=5.0,
                             wspace=5.0, hspace=5.0)

# add common labels
figw, figh = fig.get_size_inches()*25.4
xlabel = fig.text(0.5, 2.5/figh, '', ha='center')
ylabel = fig.text(2.5/figw, 0.5, 'depth (m)', va='center', rotation='vertical')

# loop over dates
for i, date in enumerate(fitparams.index):
    datestring = date.strftime('%Y-%m-%d')
    print 'plotting frame at %s ...' % datestring

    # update xlabel
    xlabel.set_text('ice deformation on %s ($m\,a^{-1}$)' % datestring)

    # loop over boreholes
    for j, bh in enumerate(ut.boreholes):
        ax = grid[j]
        ax.cla()
        c = ut.colors[j]
        n = fitparams[bh, 'n'][date]
        C = fitparams[bh, 'C'][date]
        A = np.exp(C) / (rhoi*g*sina)**n

        # plot deformation profile
        depth_fit = np.linspace(0.0, depth_base[j], 11)
        e_fit = np.exp(C) * depth_fit**n
        v_fit = 2*np.exp(C)/(n+1) * (depth_base[j]**(n+1) - depth_fit**(n+1))
        v_obs = 2*np.exp(C)/(n+1) * (depth_base[j]**(n+1) - depth[j]**(n+1))

        # plot velocity profiles
        ax.plot(v_fit, depth_fit, c=c)
        ax.fill_betweenx(depth_fit, 0.0, v_fit, color=c, alpha=0.25)
        ax.set_title(bh)

        # add velocity arrows
        for d, v in zip(depth[j], v_obs):
            ax.arrow(0.0, d, v, 0.0, fc='none', ec=c,
                     head_width=5.0, head_length=1.0, length_includes_head=True)

        # add tilt arrows
        try:
            ax.quiver(v_obs, depth[j], -exz[j].loc[datestring]*2,
                      np.sqrt(1-(2*exz[j].loc[datestring])**2),
                      angles='xy', scale=5.0)
        except KeyError:
            pass

        # add horizontal lines
        ax.axhline(0.0, c='k')
        ax.axhline(depth_base[j], c='k')
        ax.set_ylim(300.0, 0.0)
        ax.set_xlim(50.0, 0.0)

        # add fit values
        ax.text(0.05, 0.05, r'A=%.2e$\,Pa^{-n}\,s^{-2}$, n=%.2f' % (A, n),
                transform=ax.transAxes)

    # remove right axis tick labels
    for label in ax.get_yticklabels():
        label.set_visible(False)

    # save
    fig.savefig('frames/%04d.png' % i)
