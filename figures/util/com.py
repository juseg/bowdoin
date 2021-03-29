# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin common utils.
"""

import gpxpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import cartopy.crs as ccrs
import cartowik.decorations as cde

# local aliases
add_scale_bar = cde.add_scale_bar
add_subfig_label = cde.add_subfig_label


# Input methods
# -------------

def load_file(filename):
    """Load preprocessed data file and return data with duplicates removed."""
    data = pd.read_csv(filename, parse_dates=True, index_col='date')
    data = data.groupby(level=0).mean()
    return data


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

def add_subfig_labels(axes=None, colors=None, **kwargs):
    """Add automatic subfigure labels (a), (b), (c), etc."""
    # NOTE: this could become part of absplots

    # get the figure axes by default, else convert to flat array
    if axes is None:
        axes = plt.gcf().axes
    else:
        axes = np.array(axes).flatten()

    # convert colors to list if it is a non-string sequence
    if isinstance(colors, str) or not hasattr(colors, '__iter__'):
        colors = [colors] * len(axes)

    # add subfigure labels
    for ax, color, label in zip( axes, colors, 'abcdefghijklmnopqrstuvwxyz'):
        add_subfig_label('('+label+')', ax=ax, color=color, **kwargs)


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
                ha='center', transform=trans, clip_on=True)
