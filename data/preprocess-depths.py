#!/usr/bin/env python2

import gpxpy
import numpy as np
import pandas as pd
import cartopy.crs as ccrs


sensor_holes = dict(pressure=dict(upper='BH2', lower='BH3'),
                    thstring=dict(upper='BH2', lower='BH3'),
                    tiltunit=dict(upper='BH1', lower='BH3'))
observ_dates = dict(BH1='2014-07-17 18:07:00',  # assumed
                    BH2='2014-07-17 18:07:00',  # assumed
                    BH3='2014-07-23 00:30:00')  # assumed
water_depths = dict(BH1=48.0, BH2=46.0, BH3=0.0)


def borehole_distances(upper='BH2', lower='BH3'):
    """
    Compute distances between boreholes
    """

    # projections used to compute distances
    ll = ccrs.PlateCarree()
    utm = ccrs.UTM(19)

    # initialize empty data series
    ux = pd.Series()
    uy = pd.Series()
    lx = pd.Series()
    ly = pd.Series()

    # read GPX file
    with open('../data/locations.gpx', 'r') as gpx_file:
        for wpt in gpxpy.parse(gpx_file).waypoints:
            if upper in wpt.name:
                xy = utm.transform_point(wpt.longitude, wpt.latitude, ll)
                ux[wpt.time], uy[wpt.time] = xy
            elif lower in wpt.name:
                xy = utm.transform_point(wpt.longitude, wpt.latitude, ll)
                lx[wpt.time], ly[wpt.time] = xy

    # sort by date
    for ts in ux, uy, lx, ly:
        ts.sort_index(inplace=True)

    # ensure series have same length
    assert len(ux) == len(uy) == len(lx) == len(ly)

    # compute distances
    distances = ((ux.values-lx.values)**2 + (uy.values-ly.values)**2)**0.5

    # get average dates
    meandates = lx.index +(ux.index-lx.index)/2

    # return as a pandas series
    ts = pd.Series(index=meandates, data=distances)
    ts = ts.sort_index()
    ts.index.name = 'date'
    return ts


def borehole_thinning(uz, lz, distances):
    """Estimate thinning based on distance between boreholes."""
    dz = (uz+lz) / 2 * (distances[0]/distances-1)  # < 0)
    return dz


def sensor_depths_init(sensor):
    """Return initial sensor depths as data series."""

    # exact borehole location depends on sensor
    upper = sensor_holes[sensor]['upper']
    lower = sensor_holes[sensor]['lower']

    # load water level data
    ulev = pd.read_csv('processed/bowdoin-%s-wlev-upper.csv' % sensor,
                        parse_dates=True, index_col='date')
    llev = pd.read_csv('processed/bowdoin-%s-wlev-lower.csv' % sensor,
                        parse_dates=True, index_col='date')

    # compute sensor depths
    ut = observ_dates[upper]
    lt = observ_dates[lower]
    uz = ulev.loc[ut:ut].mean() + water_depths[upper]
    lz = llev.loc[lt:lt].mean() + water_depths[lower]

    # retunr sensor depths
    return uz, lz


def sensor_depths_evol(sensor, uz, lz, ubase, lbase):
    """Return time-dependent sensor depths as data frames."""

    # exact borehole location depends on sensor
    upper = sensor_holes[sensor]['upper']
    lower = sensor_holes[sensor]['lower']

    # compute time-dependent depths
    distances = borehole_distances(upper=upper, lower=lower)
    dz = borehole_thinning(ubase, lbase, distances)

    # apply thinning
    uz = dz.apply(lambda d: uz * (1+d/ubase))
    lz = dz.apply(lambda d: lz * (1+d/lbase))

    # return depth data series
    return uz, lz


def thstring_depth_init(ubase, lbase):
    """
    Return initial temperature sensor depths as data series.

    This is the most confusing part of the data processing. After looking at it
    many times I could not recover thermistor depths from the deeper strings.

    Measured surfacing cable lenghts
    * Th-Bowdoin-2: BH1A 2015-07-18 12:30, 19.70 m to 275 m mark
      (upper)            2016-07-19 11:45, 21.60 m to 275 m mark (+1.90)
                    BH1B 2015-07-18 12:30, 13.40 m to sensor 7
                         2016-07-19 11:45, 15.30 m to sensor 7 (+1.90)
    * Th-Bowdoin-1: BH2A 2015-07-18 14:30, 7.30 m to 250 m mark
      (lower)            2016-07-19 13:20, 9.70 m to 250 m mark (+2.40)
                    BH2B 2015-07-18 14:30, 11.25 m to sensor 6
                         2016-07-19 13:20, 13.65 m to sensor 6 (+2.40)

    Additional information from Conny, incompatible with the above: at the
    lower borehole, the gap between the deepest sensor of the surface string
    and the shallowest sensor on the deeper string is 20 m.
    """

    # ``SMB was measured [...] on Bowdoin Glacier at [...] BH1 (71 m a.s.l.)
    # from 19 July 2014 to 16 July 2015 [...] SMB on Bowdoin Glacier for
    # 2014/15 was [...] -1.96 m a-1 at [...] BH1'' (Tsutaki et al., 2016).
    melt = 1.96

    # upper borehole
    surf_string = [0.0 - 13.40 - 20.0*i for i in [-6, -5, -4, -3, 0, -2, -1]]
    deep_string = [275.0 - 19.70 - 20.0*i for i in range(9)]  # surface cable
    deep_string = [ubase - melt] + [np.nan] * 8  # nans except for the base
    uz = pd.Series(index=['UT%02d' % (i+1) for i in range(16)],
                   data=list(deep_string)+list(surf_string))

    # lower borehole
    surf_string = [-20.0 - 11.25 - 20.0*i for i in range(-6, 1)]
    deep_string = [250.0 - 7.30 - 20.0*i for i in range(9)]  # surface cable
    deep_string = [surf_string[0] - 20.0*i for i in range(-8, 1)]  # Conny
    deep_string = [lbase - melt] + [np.nan] * 8  # nans except for the base
    lz = pd.Series(index=['LT%02d' % (i+1) for i in range(16)],
                   data=list(deep_string)+list(surf_string))

    # add melted ice to reconstruct 2014 positions. Although cable lengths
    # were measured in 2015, the spacing between sensors is relative to 2014
    # before longitudinal stretching took place.
    uz += melt
    lz += melt

    # return as a pandas data series
    return uz, lz


if __name__ == '__main__':
    """Preprocess borehole sensor depths."""

    # first get initial sensor depths
    puz, plz = sensor_depths_init('pressure')
    uuz, ulz = sensor_depths_init('tiltunit')

    # assume borehole base at the deepest sensor
    ubase = max(puz.max(), uuz.max())
    lbase = max(plz.max(), ulz.max())

    # get initial thermistor depths
    tuz, tlz = thstring_depth_init(ubase, lbase)

    # compute borehole thinning
    puz, plz = sensor_depths_evol('pressure', puz, plz, ubase, lbase)
    tuz, tlz = sensor_depths_evol('thstring', tuz, tlz, ubase, lbase)
    uuz, ulz = sensor_depths_evol('tiltunit', uuz, ulz, ubase, lbase)

    # export to csv
    puz.to_csv('processed/bowdoin-pressure-depth-upper.csv', header=True)
    plz.to_csv('processed/bowdoin-pressure-depth-lower.csv', header=True)
    tuz.to_csv('processed/bowdoin-thstring-depth-upper.csv', header=True)
    tlz.to_csv('processed/bowdoin-thstring-depth-lower.csv', header=True)
    uuz.to_csv('processed/bowdoin-tiltunit-depth-upper.csv', header=True)
    ulz.to_csv('processed/bowdoin-tiltunit-depth-lower.csv', header=True)
