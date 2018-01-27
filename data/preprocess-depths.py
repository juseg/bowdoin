#!/usr/bin/env python2

import gpxpy
import pandas as pd
import cartopy.crs as ccrs


sensor_holes = dict(pressure=dict(upper='BH2', lower='BH3'),
                    tiltunit=dict(upper='BH1', lower='BH3'))
observ_dates = dict(BH1='2014-07-17 18:07:00',  # assumed
                    BH2='2014-07-17 18:07:00',  # assumed
                    BH3='2014-07-23 00:30:00')  # assumed
water_depths = dict(BH1=48.0, BH2=46.0, BH3=0.0)


def borehole_distances(upper='BH2', lower='BH3'):
    """
    Compute distances between boreholes
    """

    # years with data
    # FIXME: there must be a better way to do that
    years = [2014, 2016, 2017]

    # projections used to compute distances
    ll = ccrs.PlateCarree()
    utm = ccrs.UTM(19)

    # read GPX file
    locations = dict()
    dates = dict()
    with open('../data/locations.gpx', 'r') as gpx_file:
        for wpt in gpxpy.parse(gpx_file).waypoints:
            if upper in wpt.name or lower in wpt.name:
                xy = utm.transform_point(wpt.longitude, wpt.latitude, ll)
                locations[wpt.name] = xy
                dates[wpt.name] = wpt.time

    # compute distances
    distances = dict()
    for y in years:
        ux, uy = locations['B%2d%s' % (y-2000, upper)]
        lx, ly = locations['B%2d%s' % (y-2000, lower)]
        distances[y] = ((ux-lx)**2 + (uy-ly)**2)**0.5

    # get average dates
    meandates = dict()
    for y in years:
        ud = dates['B%2d%s' % (y-2000, upper)]
        ld = dates['B%2d%s' % (y-2000, lower)]
        meandates[y] = ld+(ud-ld)/2

    # return as a pandas series
    ts = pd.Series(index=meandates.values(), data=distances.values())
    ts = ts.sort_index()
    ts.index.name = 'date'
    return ts


def borehole_thinning(uz, lz, distances):
    """Estimate thinning based on distance between boreholes."""
    dz = (uz+lz) / 2 * (distances[0]/distances-1)  # < 0)
    return dz


def sensor_depths(sensor='pressure'):
    """Compute time-dependent sensor depths."""

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
    ubase = uz.max()  # FIXME: this should consider other sensors too
    lbase = lz.max()  # FIXME: this should consider other sensors too

    # compute time-dependent depths
    distances = borehole_distances(upper=upper, lower=lower)
    dz = borehole_thinning(ubase, lbase, distances)

    # apply thinning
    uz = dz.apply(lambda d: uz * (1+d/ubase))
    lz = dz.apply(lambda d: lz * (1+d/lbase))

    # return depth data series
    return uz, lz


if __name__ == '__main__':
    """Preprocess borehole sensor depths."""
    # FIXME: include preprocessing of thermistor string depths.

    # extract pressure and tiltunit sensor depths
    for sensor in ('pressure', 'tiltunit'):
        uz, lz = sensor_depths(sensor=sensor)
        uz.to_csv('processed/bowdoin-%s-depth-upper.csv' % sensor, header=True)
        lz.to_csv('processed/bowdoin-%s-depth-lower.csv' % sensor, header=True)
