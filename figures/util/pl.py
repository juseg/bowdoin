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
import al

from matplotlib.transforms import ScaledTranslation


# Geographic data
# ---------------

ll = ccrs.PlateCarree()


# Figure creation
# ---------------

def subplots_inches(nrows=1, ncols=1, figsize=None,
                    left=None, bottom=None, right=None, top=None,
                    wspace=None, hspace=None, projection=None, **kwargs):
    from matplotlib.pyplot import rcParams, subplots

    # get figure dimensions from rc params if missing
    figw, figh = figsize or rcParams['figure.figsize']

    # normalize inner spacing to axes dimensions
    if wspace is not None:
        wspace = (((figw-left-right)/wspace+1)/ncols-1)**(-1)
    if hspace is not None:
        hspace = (((figh-bottom-top)/hspace+1)/nrows-1)**(-1)

    # normalize outer margins to figure dimensions
    if left is not None:
        left = left/figw
    if right is not None:
        right = 1-right/figw
    if bottom is not None:
        bottom = bottom/figh
    if top is not None:
        top = 1-top/figh

    # pass projection argument to subplot keywords
    subplot_kw = kwargs.pop('subplot_kw', {})
    if projection is not None:
        subplot_kw['projection'] = projection

    # return figure and subplot grid
    return subplots(nrows=nrows, ncols=ncols, figsize=figsize,
                    gridspec_kw={'left': left, 'right': right,
                                 'bottom': bottom, 'top': top,
                                 'wspace': wspace, 'hspace': hspace},
                    subplot_kw=subplot_kw, **kwargs)


def subplots_mm(nrows=1, ncols=1, figsize=None,
                left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=None, projection=None, **kwargs):

    # convert all non null arguments in inches
    mm = 1/25.4
    if figsize is not None:
        figw, figh = figsize
        figsize = (figw*mm, figh*mm)
    if left is not None:
        left *= mm
    if right is not None:
        right *= mm
    if bottom is not None:
        bottom = bottom*mm
    if top is not None:
        top = top*mm
    if wspace is not None:
        wspace = wspace*mm
    if hspace is not None:
        hspace = hspace*mm

    # use inches helper to align subplots
    return subplots_inches(nrows=nrows, ncols=ncols, figsize=figsize,
                           left=left, right=right, bottom=bottom, top=top,
                           wspace=wspace, hspace=hspace,
                           projection=projection, **kwargs)


# Axes properties
# ---------------

def add_subfig_label(s, ax=None, ha='left', va='top', offset=2.5/25.4):
    ax = ax or plt.gca()
    x = (ha == 'right')  # 0 for left edge, 1 for right edge
    y = (va == 'top')  # 0 for bottom edge, 1 for top edge
    xoffset = (1 - 2*x)*offset
    yoffset = (1 - 2*y)*offset
    offset = ScaledTranslation(xoffset, yoffset, ax.figure.dpi_scale_trans)
    return ax.text(x, y, s, ha=ha, va=va, fontweight='bold',
                   transform=ax.transAxes + offset)


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

def plot_campaigns(ax, y=0.95, va='baseline'):
    """Plot 2014--2016 summer field campaigns."""

    # add rectangular spans
    c = ut.palette['darkorange']
    ax.axvspan('2014-07-15', '2014-07-29', ec='none', fc=c, alpha=0.25)
    ax.axvspan('2015-07-06', '2015-07-20', ec='none', fc=c, alpha=0.25)
    ax.axvspan('2016-07-04', '2016-07-21', ec='none', fc=c, alpha=0.25)
    ax.axvspan('2017-07-04', '2017-07-17', ec='none', fc=c, alpha=0.25)

    # prepare blended transform
    trans = plt.matplotlib.transforms.blended_transform_factory(
        ax.transData, ax.transAxes)

    # add text annotations
    kwa = dict(color=c, transform=trans, va=va)
    ax.text('2014-07-10', y, 'field campaign 2014', ha='left', **kwa)
    ax.text('2015-07-13', y, 'field campaign 2015', ha='center', **kwa)
    ax.text('2016-07-13', y, 'field campaign 2016', ha='center', **kwa)
    ax.text('2017-07-22', y, 'field campaign 2017', ha='right', **kwa)


# Map elements
# ------------

def shading(z, dx=None, dy=None, extent=None, azimuth=315.0, altitude=30.0):
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
    # zlight = 0.0  # remove shades from horizontal surfaces

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


def add_waypoint(name, ax=None, color=None, marker='o',
                 text=None, textpos='ul', offset=10):
    """Plot and annotate waypoint from GPX file"""

    # get current axes if None given
    ax = ax or plt.gca()

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
                    isright = (textpos[1] == 'r')
                    isup = (textpos[0] == 'u')
                    xytext = ((2*isright-1)*offset, (2*isup-1)*offset)
                    ax.annotate(text, xy=xy, xytext=xytext, color=color,
                                ha=('left' if isright else 'right'),
                                va=('bottom' if isup else 'top'),
                                fontweight='bold', textcoords='offset points',
                                bbox=dict(pad=0, ec='none', fc='none'),
                                arrowprops=dict(arrowstyle='->', color=color,
                                                relpos=(1-isright, 1-isup)))

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


# Saving figures
def savefig(fig=None):
    """Save figure to script filename."""
    fig = fig or plt.gcf()
    res = fig.savefig(os.path.splitext(sys.argv[0])[0])
    return res
