#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt

"""Utils to plot tilt data."""

def powerfit(x, y, deg, **kwargs):
    """Fit to a power law."""
    logx = np.log(x)
    logy = np.log(y)
    p = np.polyfit(logx, logy, deg, **kwargs)
    return p


def glenfit(depth, exz, g=9.80665, rhoi=910.0, slope=0.03):
    """Fit to a power law with exp(C) = A * (rhoi*g*slope)**n."""
    # FIXME: the slope (sin alpha) is an approximate value from MEASURES
    n, C = powerfit(depth, exz, 1)
    A = np.exp(C) / (rhoi*g*slope)**n
    return n, A


def vsia(depth, depth_base, n, A, g=9.80665, rhoi=910.0, slope=0.03):
    """Return simple horizontal shear velocity profile."""
    C = A * (rhoi*g*slope)**n
    v = 2*C/(n+1) * (depth_base**(n+1) - depth**(n+1))
    return v


def plot_profile(depth, exz, depth_base, ax=None, c='k', n=101):
    """Fit and plot tilt velocity profile."""

    # get current axes if None provided
    ax = ax or plt.gca()

    # prepare depth vector for fitting curve
    depth_fit = np.linspace(0.0, depth_base, n)

    # fit to glen's law
    n, A = glenfit(depth, exz)

    # compute velocity profiles
    v_fit = vsia(depth_fit, depth_base, n, A)
    v_obs = vsia(depth, depth_base, n, A)

    # plot fitted velocity profiles
    ax.plot(v_fit, depth_fit, c=c)
    ax.fill_betweenx(depth_fit, 0.0, v_fit, color=c, alpha=0.25)

    # add velocity arrows at observation points
    for d, v in zip(depth, v_obs):
        ax.arrow(0.0, d, v, 0.0, fc='none', ec=c,
                 head_width=5.0, head_length=1.0, length_includes_head=True)

    # add tilt arrows
    ax.quiver(v_obs, depth, -exz*2, np.sqrt(1-(2*exz)**2),
              angles='xy', scale=5.0)

    # add horizontal lines
    ax.axhline(0.0, c='k')
    ax.axhline(depth_base, c='k')

    # add fit values
    ax.text(0.05, 0.05, r'A=%.2e$\,Pa^{-n}\,s^{-2}$, n=%.2f' % (A, n),
            transform=ax.transAxes)
