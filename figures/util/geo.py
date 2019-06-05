# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin geographic utils.
"""

import matplotlib.pyplot as plt
import gpxpy


# GPX locations methods
# ---------------------

def read_locations(filename='../data/locations.gpx'):
    """Read waypoints dictionary from GPX file."""
    with open(filename, 'r') as gpx:
        return {wpt.name: wpt for wpt in gpxpy.parse(gpx).waypoints}


# Plotting methods
# ----------------

def add_scale_bar(ax=None, length=1000, pad=None, label=None, color='k'):
    """Add a bar showing map scale."""
    # FIXME: Move this scale bar method to Cartowik?
    ax = ax or plt.gca()
    pad = pad or 0.25*length
    _, east, south, _ = ax.get_extent()
    ax.plot([east-pad-length, east-pad], [south+pad]*2, c=color, marker='|')
    ax.text(east-pad-0.5*length, south+pad, label+'\n',
            color=color, fontweight='bold', ha='center', va='center')
