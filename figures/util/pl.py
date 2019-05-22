#!/usr/bin/env python2
# coding: utf-8

"""Plotting tools."""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import gpxpy

import util as ut
import util.al as al



# Geographic data
# ---------------

ll = ccrs.PlateCarree()


# Axes preparation
# ----------------


def unframe(ax, edges=['bottom', 'left']):
    """Unframe axes to leave only specified edges visible."""

    # remove background patch
    ax.patch.set_visible(False)

    # adjust bounds
    active_spines = [ax.spines[s] for s in edges]
    for s in active_spines:
        s.set_smart_bounds(True)

    # get rid of extra spines
    hidden_spines = [ax.spines[s] for s in ax.spines if s not in edges]
    for s in hidden_spines:
        s.set_visible(False)

    # set ticks positions
    ax.xaxis.set_ticks_position([['none', 'top'], ['bottom', 'both']]
                                ['bottom' in edges]['top' in edges])
    ax.yaxis.set_ticks_position([['none', 'right'], ['left', 'both']]
                                ['left' in edges]['right' in edges])

    # set label positions
    if 'right' in edges and not 'left' in edges:
        ax.yaxis.set_label_position('right')
    if 'top' in edges and not 'bottom' in edges:
        ax.xaxis.set_label_position('top')


# Timeseries elements
# -------------------

def resample_plot(ax, ts, freq, c='b'):
    """Plot resampled mean and std of a timeseries."""
    avg = ts.resample(freq).mean()
    std = ts.resample(freq).std()
    avg.plot(ax=ax, color=c, ls='-')
    # for some reason not working
    ax.fill_between(avg.index, avg-2*std, avg+2*std, color=c, alpha=0.25)


def rolling_plot(ax, ts, window, c='b'):
    """Plot rolling window mean and std of a timeseries."""
    avg = pd.rolling_mean(ts, window)
    std = pd.rolling_std(ts, window)
    avg.plot(ax=ax, color=c, ls='-')
    ax.fill_between(avg.index, avg-2*std, avg+2*std, color=c, alpha=0.25)


def plot_vsia_profile(depth, exz, depth_base, ax=None, c='k', n=101,
                      annotate=True):
    """Fit and plot tilt velocity profile."""

    # get current axes if None provided
    ax = ax or plt.gca()

    # prepare depth vector for fitting curve
    depth_fit = np.linspace(0.0, depth_base, n)

    # fit to glen's law
    n, A = al.glenfit(depth, exz)

    # compute velocity profiles
    v_fit = al.vsia(depth_fit, depth_base, n, A)
    v_obs = al.vsia(depth, depth_base, n, A)

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
    if annotate:
        ax.text(0.05, 0.05, r'A=%.2e$\,Pa^{-n}\,s^{-2}$, n=%.2f' % (A, n),
                transform=ax.transAxes)


# Map elements
# ------------

def shading(z, dx=None, dy=None, extent=None, azimuth=315.0, altitude=30.0,
            transparent=False):
    """Compute shaded relief map."""

    # get horizontal resolution
    if (dx is None or dy is None) and (extent is None):
        raise ValueError("Either dx and dy or extent must be given.")
    rows, cols = z.shape
    dx = dx or (extent[1]-extent[0])/cols
    dy = dy or (extent[2]-extent[3])/rows

    # convert to anti-clockwise rad
    azimuth = -azimuth*np.pi / 180.
    altitude = altitude*np.pi / 180.

    # compute cartesian coords of the illumination direction
    xlight = np.cos(azimuth) * np.cos(altitude)
    ylight = np.sin(azimuth) * np.cos(altitude)
    zlight = np.sin(altitude)

    # for transparent shades set horizontal surfaces to zero
    if transparent is True:
        zlight = 0.0

    # compute hillshade (dot product of normal and light direction vectors)
    u, v = np.gradient(z, dx, dy)
    return (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)


def slope(z, dx=None, dy=None, extent=None, smoothing=None):
    """Compute slope map with optional smoothing."""

    # get horizontal resolution
    if (dx is None or dy is None) and (extent is None):
        raise ValueError("Either dx and dy or extent must be given.")
    rows, cols = z.shape
    dx = dx or (extent[1]-extent[0])/cols
    dy = dy or (extent[2]-extent[3])/rows

    # optionally smooth data
    if smoothing:
        import scipy.ndimage as ndimage
        z = ndimage.filters.gaussian_filter(z, smoothing)

    # compute gradient along each coordinate
    u, v = np.gradient(z, dx, dy)

    # compute slope
    slope = (u**2 + v**2)**0.5
    return slope


def extent_from_coords(x, y):
    """Compute image extent from coordinate vectors."""
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2
    return w, e, s, n


def coords_from_extent(extent, cols, rows):
    """Compute coordinate vectors from image extent."""

    # compute dx and dy
    (w, e, s, n) = extent
    dx = (e-w) / cols
    dy = (n-s) / rows

    # prepare coordinate vectors
    xwcol = w + 0.5*dx  # x-coord of W row cell centers
    ysrow = s + 0.5*dy  # y-coord of N row cell centers
    x = xwcol + np.arange(cols)*dx  # from W to E
    y = ysrow + np.arange(rows)*dy  # from S to N

    # return coordinate vectors
    return x, y


def add_waypoint(name, ax=None, bbox=None, color=None, fontweight='bold',
                 marker='o', text=None, textpos='ul', offset=10):
    """Plot and annotate waypoint from GPX file"""

    # get current axes if None given
    ax = ax or plt.gca()

    # invisible bbox if None given
    bbox = bbox or dict(pad=0, ec='none', fc='none')

    # open GPX file
    with open('../data/locations.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

        # find the right waypoint
        for wpt in gpx.waypoints:
            if wpt.name == name:

                # plot waypoint
                proj = ax.projection
                xy = proj.transform_point(wpt.longitude, wpt.latitude, ll)
                ax.plot(*xy, color=color, marker=marker)

                # add annotation
                if text:
                    xloc = textpos[1]
                    yloc = textpos[0]
                    px = {'c': 0.5, 'l': 1, 'r': 0}[xloc]
                    py = {'c': 0.5, 'l': 1, 'u': 0}[yloc]
                    dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*offset
                    dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*offset
                    ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
                    va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
                    ax.annotate(text, xy=xy, xytext=(dx, dy), color=color,
                                textcoords='offset points', ha=ha, va=va,
                                bbox=bbox, fontweight=fontweight,
                                arrowprops=dict(arrowstyle='->', color=color,
                                                relpos=(px, py)))

                # break the for loop
                break


def waypoint_scatter(names, ax=None, text=True, textloc='ur', offset=15,
                     alpha=1.0, **kwargs):
    """Draw annotated scatter plot from GPX waypoints."""

    # get current axes if None given
    ax = ax or plt.gca()

    # initialize coordinate lists
    xlist = []
    ylist = []

    # expand textpos to a list
    if type(textloc) is str:
        textloc = [textloc] * len(names)

    # open GPX file
    with open('../data/locations.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

        # find the right waypoints
        for wpt in gpx.waypoints:
            if wpt.name in names:

                # extract point coordinates
                proj = ax.projection
                xy = proj.transform_point(wpt.longitude, wpt.latitude, ll)
                x, y = xy
                xlist.append(x)
                ylist.append(y)

                # stop here if text is unwanted
                if text == False:
                    continue

                # add annotation
                text = '%s\n%.0f m' % (wpt.name, wpt.elevation)
                loc = textloc[names.index(wpt.name)]
                xshift = ((loc[1] == 'r')-(loc[1] == 'l'))
                xoffset = xshift * offset
                yshift = ((loc[0] == 'u')-(loc[0] == 'l'))
                yoffset = yshift * offset
                relpos = (0.5*(1-xshift), 0.5*(1-yshift))
                ha={'r': 'left', 'l': 'right', 'c': 'center'}[loc[1]]
                va={'u': 'bottom', 'l': 'top', 'c': 'center'}[loc[0]]
                xytext = xoffset, yoffset
                ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va=va,
                            textcoords='offset points',
                            bbox=dict(boxstyle='square,pad=0.5', fc='w'),
                            arrowprops=dict(arrowstyle='->', color='k',
                                            relpos=relpos, alpha=alpha))

    # add scatter plot
    ax.scatter(xlist, ylist, alpha=alpha, **kwargs)


def add_scale(ax=None, length=1000, pad=None, label=None, color='k'):
    """Add map scale."""
    ax = ax or plt.gca()
    pad = pad or 0.25*length
    w, e, s, n = ax.get_extent()
    ax.plot([e-pad-length, e-pad], [s+pad]*2, color=color, marker='|')
    ax.text(e-pad-0.5*length, s+pad, label+'\n', color=color,
            fontweight='bold', ha='center', va='center')
