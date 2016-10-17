#!/usr/bin/env python2
# coding: utf-8

"""Plotting tools."""

import util as ut

import cartopy.crs as ccrs
import numpy as np
import matplotlib.pyplot as plt
import gpxpy

# cartographic projections

ll = ccrs.PlateCarree()


# subplot helper functions

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


# map drawing functions

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
    with open('data/locations.gpx', 'r') as gpx_file:
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
    with open('data/locations.gpx', 'r') as gpx_file:
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
                            bbox=dict(boxstyle='square,pad=0.5', fc='w',
                                      alpha=alpha),
                            arrowprops=dict(arrowstyle='->', color='k',
                                            relpos=relpos, alpha=alpha))

    # add scatter plot
    ax.scatter(xlist, ylist, alpha=alpha, **kwargs)
