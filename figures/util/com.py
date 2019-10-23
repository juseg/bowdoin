# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin common utils.
"""

import os
import sys
import gpxpy
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import cartopy.crs as ccrs


# Input methods
# -------------

def read_locations(filename='../data/locations.gpx', crs=None):
    """Read waypoints dataframe from GPX file."""

    # read locations in geographic coordinates
    with open(filename, 'r') as gpx:
        attributes = [{attr: getattr(wpt, attr) for attr in wpt.__slots__}
                      for wpt in gpxpy.parse(gpx).waypoints]
    data = pd.DataFrame(attributes).dropna(axis=1, how='all').set_index('name')

    # if crs is given, append coordinates in given crs
    if crs is not None:
        xyz = data[['longitude', 'latitude', 'elevation']].values
        xyz = crs.transform_points(ccrs.PlateCarree(), *xyz.T).T
        data['x'], data['y'], data['z'] = xyz

    # remove timezone information (see gpxpy issue #182)
    data.time = data.time.dt.tz_localize(None)

    # return locations dataframe
    return data


# Plotting methods
# ----------------

def add_subfig_label(text, ax=None, loc='ul', xpad=6, ypad=6, **kwargs):
    """
    Add a subfigure label in bold. The default position is near the upper left
    corner of the axes frame.

    Parameters
    ----------
    text: string
        The subfigure label text.
    ax: Axes
        Axes to draw on, defaults to the current axes.
    loc: string
        Label location ll, lc, lr, cl, cc, cr, ul, uc or ur.
    xpad: scalar
        Horizontal pad between the axes margin and the label in points.
    ypad: scalar
        Vertical pad between the axes margin and the label in points.
    **kwargs:
        Additional keyword arguments are passed to annotate.
    """

    # process arguments
    ax = ax or plt.gca()
    yloc, xloc = loc

    # add annotation
    ax.annotate(text, fontweight='bold', textcoords='offset points',
                ha={'l': 'left', 'c': 'center', 'r': 'right'}[xloc],
                va={'l': 'bottom', 'c': 'center', 'u': 'top'}[yloc],
                xy=({'l': 0, 'c': 0.5, 'r': 1}[xloc],
                    {'l': 0, 'c': 0.5, 'u': 1}[yloc]),
                xytext=({'l': 1, 'c': 0, 'r': -1}[xloc]*xpad,
                        {'l': 1, 'c': 0, 'u': -1}[yloc]*ypad),
                xycoords='axes fraction', **kwargs)


def plot_field_campaigns(ax=None, color='C1', ytext=0.05):
    """Mark 2014--2017 summer field campaigns."""

    # get axes if None provided
    ax = ax or plt.gca()

    # prepare blended transform
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)

    # for dates when people were on Bowdoin
    for start, end in [('2014-07-15', '2014-07-29'),
                       ('2015-07-06', '2015-07-20'),
                       ('2016-07-04', '2016-07-21'),
                       ('2017-07-04', '2017-07-17')]:

        # add rectangular spans
        ax.axvspan(start, end, ec='none', fc=color, alpha=0.25)

        # add text annotations
        duration = pd.to_datetime(end) - pd.to_datetime(start)
        midpoint = pd.to_datetime(start) + duration / 2
        ax.text(midpoint, ytext, midpoint.year, color=color, fontweight='bold',
                ha='center', transform=trans)


def savefig(fig=None, suffix=''):
    """Save figure to script filename."""
    fig = fig or plt.gcf()
    res = fig.savefig(os.path.splitext(sys.argv[0])[0]+suffix)
    return res
