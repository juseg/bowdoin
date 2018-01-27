#!/usr/bin/env python2

import gpxpy
import numpy as np
import pandas as pd
import cartopy.crs as ccrs


# Global data
# -----------

# borehole properties
sensor_holes = dict(pressure=dict(upper='BH2', lower='BH3'),
                    thstring=dict(upper='BH2', lower='BH3'),
                    tiltunit=dict(upper='BH1', lower='BH3'))
observ_dates = dict(BH1='2014-07-17 18:07:00',  # assumed
                    BH2='2014-07-17 18:07:00',  # assumed
                    BH3='2014-07-23 00:30:00')  # assumed
water_depths = dict(BH1=48.0, BH2=46.0, BH3=0.0)

# data logger properties
pressure_loggers = dict(lower='drucksens073303', upper='drucksens094419')
pressure_columns = ['label', 'year', 'day', 'time', 'temp', 'pres', 'wlev']
tiltunit_loggers = dict(lower='BOWDOIN-1', upper='BOWDOIN-2')
tiltunit_allinst = ['id', 'ixr', 'iyr', 'mx', 'my', 'mz', 'p', 'tp', 't']
tiltunit_outinst = ['ixr', 'iyr', 'p', 'tp', 't']
thstring_loggers = dict(lower='Th-Bowdoin-1', upper='Th-Bowdoin-2')


# Borehole location methods
# -------------------------

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


# Sensor depth methods
# --------------------

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


# Data reading methods
# --------------------

def get_pressure_data(bh, log):
    """Return pressure sensor data in a data frame."""

    # date parser
    parser = lambda year, day, time: pd.datetime.strptime(
        '%04d.%03d.%04d' % tuple(map(int, [year, day, time])), '%Y.%j.%H%M')

    # read original file
    df = pd.read_csv('original/pressure/%s_final_storage_1.dat' % log,
                     names=pressure_columns, index_col='date',
                     na_values=[-99999], date_parser=parser,
                     parse_dates={'date': ['year', 'day', 'time']})

    # return dataframe
    return df


def get_tiltunit_data(bh, log):
    """Return tilt unit data in a data frame."""

    # input file names
    ifilename = 'original/inclino/%s_All.dat' % log

    # open input file
    idf = pd.read_csv(ifilename, skiprows=[0, 2, 3], index_col=0,
                      dtype=str, parse_dates=True, na_values='NAN')

    # rename index
    idf.index = idf.index.rename('date')

    # these columns will need to be splitted
    rescols = [col for col in idf.columns if col.startswith('res')]

    # ignore columns containing no data
    rescols = [col for col in rescols if not idf[col].isnull().all()]

    # split remaining columns into new dataframe
    odf = pd.concat([splitstrings(bh, idf[col]) for col in rescols], axis=1)

    # return filled dataframe
    return odf


def get_thstring_data(bh, log, manual=False):
    """Return thermistor string data in a data frame."""

    # input file names
    postfix = 'Manual' if manual else 'Therm'
    cfilename = 'original/temperature/%s_Coefs.dat' % log
    ifilename = 'original/temperature/%s_%s.dat' % (log, postfix)

    # read rearranged calibration coefficients
    # sensor order lower: BH2A[1-9] + BH2B[1-7],
    #              upper: BH1A[1-9] + BH1B[1-4,7,5-6].
    a1, a2, a3 = np.loadtxt(cfilename, unpack=True)

    # read resistance data
    skiprows = [0] if manual else [0, 2, 3]
    df = pd.read_csv(ifilename, skiprows=skiprows, comment='#',
                     na_values='NAN', index_col=0)
    df = df[['Resist({:d})'.format(i+1) for i in range(16)]]

    # compute temperature from resistance
    df = np.log(df)
    df = 1 / (a1 + a2*df + a3*df**3) - 273.15

    # rename index and columns
    df.index = df.index.rename('date')
    df.columns = [bh[0].upper() + 'T%02d' % (i+1) for i in range(16)]

    # return as dataframe
    return df


# Tiltunit data extraction methods
# --------------------------------

def floatornan(x):
    """Try to convert to float and return NaN if that fails."""
    try:
        return float(x)
    except ValueError:
        return np.nan


def splitstrings(bh, ts):
    """Split series of data strings into multi-column data frame."""

    # split data strings into new multi-column dataframe and fill with NaN
    df = ts.str.split(',', expand=True)
    df.fillna(value=np.nan, inplace=True)

    # rename columns
    unitname = bh[0].upper() + 'I%02d' % int(ts.name[-2:-1])
    df.columns = [tiltunit_allinst, [unitname]*len(tiltunit_allinst)]

    # replace nan values by nan
    df.replace('-99.199996', np.nan, inplace=True)

    # convert to numeric
    # splitted.convert_objects(convert_numeric=True)  # deprectiated
    # splitted = pd.to_numeric(splitted, errors='coerce')  # does not work
    df = df.applymap(floatornan)

    # return splitted dataframe
    return df


def extract_tilt(df, log):
    """Return tilt angles in a dataframe."""

    # read calibration coefficients
    coefs = pd.read_csv('original/inclino/%s_Coefs.dat' % log,
                         index_col=0, comment='#')

    # keep only units present in data
    coefs = coefs.loc[df['ixr'].columns]

    # process angles and compute tilt
    tiltx = (df['ixr'] - coefs['bx'])/coefs['ax']
    tilty = (df['iyr'] - coefs['by'])/coefs['ay']
    # tilt = np.arcsin(np.sqrt(np.sin(tiltx)**2+np.sin(tilty)**2))*180/np.pi

    # return tilt
    return tiltx, tilty


def extract_temp(df):
    """Return temperature values in a dataframe."""
    temp = df['t']*1e-3
    return temp


def extract_wlev(df):
    """Return water level and unit depths."""
    wlev = df['p']*1e2/9.80665
    return wlev


# Temperature calibration methods
# -------------------------------

def cal_temperature(temp, depth, borehole):
    """
    Recalibrate lower temperature to zero degrees.
    """
    return temp + melt_offset(temp, depth, borehole)


def melt_offset(temp, depth, borehole):
    """
    Return offset between measured temp and melting point.
    Unfortunately initial upper data were lost.
    """

    # check argument validity
    assert borehole in ('lower', 'upper')

    # compute offset to melting point
    if borehole == 'lower':
        if 'temp01' in depth:
            depth['temp01'] = 243.849292443  # FIXME: move this to preproc
        melt = melting_point(depth.iloc[0])  # FIXME: find nearest date
        calt = temp['2014-07-23 11:20':'2014-07-23 15:00'].mean()
        offset = (melt - calt).fillna(0.0)
    else:
        offset = 0.0

    # return offset
    return offset


def melting_point(depth, g=9.80665, rhoi=910.0, beta=7.9e-8):
    """Compute pressure melting point from depth (Luethi et al., 2002)"""
    return -beta * rhoi * g * depth


# Main program
# ------------

if __name__ == '__main__':
    """Preprocess borehole data."""

    # preprocess pressure sensor data
    for bh, log in pressure_loggers.iteritems():

        # get all data
        df = get_pressure_data(bh, log)

        # extract water level
        wlev = df['wlev'].rename(bh[0].upper() + 'P')
        wlev.to_csv('processed/bowdoin-pressure-wlev-%s.csv' % bh, header=True)

        # extract temperature
        temp = df['temp'].rename(bh[0].upper() + 'P')
        temp.to_csv('processed/bowdoin-pressure-temp-%s.csv' % bh, header=True)

    # preprocess tiltunit water level
    for bh, log in tiltunit_loggers.iteritems():

        # get all data
        df = get_tiltunit_data(bh, log)

        # extract water level and sensor depth
        wlev = extract_wlev(df)
        wlev.to_csv('processed/bowdoin-tiltunit-wlev-%s.csv' % bh)

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

    # preprocess tiltunit temperatures and tilt
    for bh, log in tiltunit_loggers.iteritems():

        # get sensor depth
        z = {'upper': uuz, 'lower': ulz}[bh]

        # get all data # FIXME: reading data again
        df = get_tiltunit_data(bh, log)

        # extract temperatures
        temp = extract_temp(df)
        temp = cal_temperature(temp, z, bh)
        temp.to_csv('processed/bowdoin-tiltunit-temp-%s.csv' % bh)

        # extract tilt angles
        tiltx, tilty = extract_tilt(df, log)
        tiltx.to_csv('processed/bowdoin-tiltunit-tiltx-%s.csv' % bh)
        tilty.to_csv('processed/bowdoin-tiltunit-tilty-%s.csv' % bh)

    # preprocess thermistor string data
    for bh, log in thstring_loggers.iteritems():

        # get sensor depth
        z = {'upper': tuz, 'lower': tlz}[bh]

        # preprocess data logger temperatures
        df = get_thstring_data(bh, log)
        df += melt_offset(df, z, bh)
        df.to_csv('processed/bowdoin-thstring-temp-%s.csv' % bh)

        # preprocess manual temperatures
        df = get_thstring_data(bh, log, manual=True)
        df.to_csv('processed/bowdoin-thstring-mantemp-%s.csv' % bh)
