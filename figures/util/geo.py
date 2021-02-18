# Copyright (c) 2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin geographic utils.
"""

import gpxpy


# GPX locations methods
# ---------------------

def read_locations(filename='../data/locations.gpx'):
    """Read waypoints dictionary from GPX file."""
    with open(filename, 'r') as gpx:
        return {wpt.name: wpt for wpt in gpxpy.parse(gpx).waypoints}
