#!/usr/bin/env python

import os
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
basal_depths = dict(BH1=272.0, BH2=262.0, BH3=252.0)

# data logger properties
dgps_columns = ['daydate', 'time', 'lat', 'lon', 'z', 'Q', 'ns',
                'sdn', 'sde', 'sdu', 'sdne', 'sdeu', 'sdun', 'age', 'ratio']
pressure_loggers = dict(lower='drucksens073303', upper='drucksens094419')
pressure_columns = ['id', 'year', 'day', 'time', 'temp', 'pres', 'wlev']
tiltunit_loggers = dict(lower='BOWDOIN-1', upper='BOWDOIN-2')
tiltunit_sensors = ['id', 'ixr', 'iyr', 'mx', 'my', 'mz', 'p', 'tp', 't']
tiltunit_outinst = ['ixr', 'iyr', 'p', 'tp', 't']
thstring_loggers = dict(lower='Th-Bowdoin-1', upper='Th-Bowdoin-2')

# physical constants
g = 9.80665  # gravitational acceleration in m s-2
rhoi = 910.0  # ice density in kg m-3
beta = 7.9e-8  # ice Clapeyron constant (Luethi et al., 2002)


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
    meandates = lx.index + (ux.index-lx.index)/2

    # return as a pandas series
    ts = pd.Series(index=meandates, data=distances)
    ts = ts.sort_index()
    ts.index.name = 'date'
    return ts


def borehole_thinning(uz, lz, distances):
    """Estimate thinning based on distance between boreholes."""
    # FIXME account for ice melt
    dz = (uz+lz) / 2 * (distances[0]/distances-1)  # < 0)
    return dz


# Sensor depth methods
# --------------------

def borehole_base_evol(sensor):
    """Return time-dependent borehole base for sensor as data series."""

    # exact borehole location depends on sensor
    upper = sensor_holes[sensor]['upper']
    lower = sensor_holes[sensor]['lower']

    # get initial borehole base
    ubase = basal_depths[upper]
    lbase = basal_depths[lower]

    # compute time-dependent depths
    distances = borehole_distances(upper=upper, lower=lower)
    dz = borehole_thinning(ubase, lbase, distances)

    # apply thinning
    ubase = dz + ubase
    lbase = dz + lbase

    # rename data series
    stype = dict(pressure='P', thstring='T', tiltunit='I')[sensor]
    ubase = ubase.rename(stype+'UB')
    lbase = lbase.rename(stype+'LB')

    # return depth data series
    return ubase, lbase


def sensor_depths_init(sensor, ulev, llev):
    """Return initial sensor depths as data series."""

    # exact borehole location depends on sensor
    upper = sensor_holes[sensor]['upper']
    lower = sensor_holes[sensor]['lower']

    # compute sensor depths (groupy averages duplicate)
    ut = observ_dates[upper]
    lt = observ_dates[lower]
    uz = ulev.loc[ut:ut].groupby(level=0).mean() + water_depths[upper]
    lz = llev.loc[lt:lt].groupby(level=0).mean() + water_depths[lower]

    # convert series to horizontal dataframes
    if len(uz.shape) == 1:
        uz = uz.to_frame()
        lz = lz.to_frame()

    # squeeze using columns as new index
    uz = uz.squeeze(axis=0)
    lz = lz.squeeze(axis=0)

    # return sensor depths
    return uz, lz


def sensor_depths_evol(sensor, uz, lz):
    """Return time-dependent sensor depths as data frames."""

    # exact borehole location depends on sensor
    upper = sensor_holes[sensor]['upper']
    lower = sensor_holes[sensor]['lower']

    # get initial borebole depths
    ubase = basal_depths[upper]
    lbase = basal_depths[lower]

    # compute time-dependent depths
    distances = borehole_distances(upper=upper, lower=lower)
    dz = borehole_thinning(ubase, lbase, distances)

    # apply thinning
    uz = dz.apply(lambda d: uz * (1+d/ubase))
    lz = dz.apply(lambda d: lz * (1+d/lbase))

    # return depth data series
    return uz, lz


def thstring_depth_init():
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

    Additional information from Martin, incompatible with the above: at the
    upper borehole, the gap between the deepest sensor of the surface string
    and the shallowest sensor on the deeper string is 10 m.

    Results:
    * Upper borehole:
     - Using surfacing cable lenghts (resulting in 11.3 m string overlap):
       up to 2 K away from tilt unit measurements, deep thermistors ~15 m too
       high, realistic profile.
     - Assuming 10 m between strings: within 1 K of tilt unit measurements,
       deep thermistors ~5 m too low, realistic profile.
    * Lower borehole:
     - Using surfacing cable lenghts (resulting in 6.05 m string overlap):
       incomatible with tilt unit measurements, deep thermistors ~60 m too
       high, even incompatible with shallow thermistors.
     - Assuming 20 m between strings: incompatible with tilt unit measurements,
       deep thermistors ~35 m too high, funny peak in temperature profile.
    """

    # ``SMB was measured [...] on Bowdoin Glacier at [...] BH1 (71 m a.s.l.)
    # from 19 July 2014 to 16 July 2015 [...] SMB on Bowdoin Glacier for
    # 2014/15 was [...] -1.96 m a-1 at [...] BH1'' (Tsutaki et al., 2016).
    melt = 1.96

    # borehole bases
    # ubase = basal_depths[sensor_holes['thstring']['upper']]
    # lbase = basal_depths[sensor_holes['thstring']['lower']]

    # upper borehole
    surf_string = [0.0 - 13.40 - 20.0*i for i in [-6, -5, -4, -3, 0, -2, -1]]
    deep_string = [275.0 - 19.70 - 20.0*i for i in range(9)]  # surface cable
    deep_string = [surf_string[0] + 10 - 20*i for i in range(-8, 1)]  # Martin
    # deep_string = [ubase - melt] + [np.nan] * 8  # nans except for the base
    uz = pd.Series(index=['UT%02d' % (i+1) for i in range(16)],
                   data=list(deep_string)+list(surf_string))

    # lower borehole
    surf_string = [-20.0 - 11.25 - 20.0*i for i in range(-6, 1)]
    deep_string = [250.0 - 7.30 - 20.0*i for i in range(9)]  # surface cable
    deep_string = [surf_string[0] - 20.0*i for i in range(-9, 0)]  # Conny
    # deep_string = [lbase - melt] + [np.nan] * 8  # nans except for the base
    lz = pd.Series(index=['LT%02d' % (i+1) for i in range(16)],
                   data=list(deep_string)+list(surf_string))

    # add melted ice to reconstruct 2014 positions. Although cable lengths
    # were measured in 2015, the spacing between sensors is relative to 2014
    # before longitudinal stretching took place.
    uz += melt
    lz += melt

    # return as a pandas data series
    return uz, lz


# Independent data reading methods
# --------------------------------

def get_dgps_data(method='backward'):
    """Return lon/lat gps positions in a data frame."""

    # check argument validity
    assert method in ('backward', 'forward', 'central')

    # append dataframes corresponding to each year
    df = pd.concat([
        pd.read_fwf('original/gps/B14BH1/B14BH1_%d_15min.dat' % year,
                    names=dgps_columns, index_col=0,
                    usecols=['daydate', 'time', 'lon', 'lat', 'z'],
                    parse_dates={'date': ['daydate', 'time']})
        for year in [2014, 2015, 2016, 2017]])

    # find samples not taken at multiples of 15 min (900 sec) and remove them
    # it seems these (18) values were recorded directly after each data gap
    inpace = (60*df.index.minute + df.index.second) % 900 == 0
    assert (not inpace.sum() < 20)  # make sure we remove less than 20 values
    df = df[inpace]

    # convert lon/lat to UTM 19 meters
    ll = ccrs.PlateCarree()
    proj = ccrs.UTM(19)
    points = proj.transform_points(ll, df['lon'].values, df['lat'].values)
    df['x'] = points[:, 0]
    df['y'] = points[:, 1]

    # resample with 15 minute frequency and fill with NaN
    df = df.resample('15T').mean()

    # compute cartesian velocity in meters per year
    v = df[['x', 'y', 'z']]
    if method == 'backward':
        v = v.diff()
    elif method == 'forward':
        v = -v.diff(-1)
    elif method == 'central':
        v = (v.diff()-v.diff(-1))/2.0
    v *= 60*24*365/15.0
    v.columns = ['vx', 'vy', 'vz']
    df = df.join(v)

    # compute velocity polar coordinates
    df['vh'] = (df['vx']**2 + df['vy']**2)**0.5
    df['azimuth'] = np.arctan2(df['vy'], df['vx']**2)*180/np.pi
    df['altitude'] = np.arctan2(df['vz'], df['vh'])*180/np.pi

    # return complete dataframe
    return df


def get_tide_data(order=2, cutoff=1/300.0):
    """Return Masahiro unfiltered tidal pressure in a data series."""

    # load data from two pressure sensors
    def parser(s): return pd.datetime.strptime(s, '%y/%m/%d %H:%M:%S')
    files = os.listdir('original/tide')
    props = dict(index_col=0, parse_dates=True, date_parser=parser)
    ls1 = ['original/tide/'+f for f in files if f.endswith('_4m.csv')]
    ls2 = ['original/tide/'+f for f in files if f.endswith('_76m.csv')]
    ts1 = pd.concat([pd.read_csv(f, **props, squeeze=True) for f in ls1])
    ts2 = pd.concat([pd.read_csv(f, **props, squeeze=True) for f in ls2])

    # correct shifts of ts2 on a daily basis
    # FIXME it looks like ts1 has internal shifts
    ts2 += (ts1-ts2).resample('1D').mean().reindex_like(ts2, method='pad')

    # merge series with priority on values from ts1 and substract mean
    ts = pd.concat([ts1, ts2]).groupby(level=0).first()
    ts -= ts.mean()

    # rename index
    ts.index = ts.index.rename('date')

    # return pressure data series
    return ts


# Borehole data reading methods
# -----------------------------

def get_pressure_data(bh, log):
    """Return pressure sensor data in a data frame."""

    # date parser
    def parser(year, day, time):
        datestring = year + day.zfill(3) + time.zfill(4)
        return pd.datetime.strptime(datestring, '%Y%j%H%M')

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
    cfilename = 'original/inclino/%s_Coefs.dat' % log

    # open input file
    df = pd.read_csv(ifilename, skiprows=[0, 2, 3], index_col=0,
                     dtype=str, parse_dates=True, na_values='NAN')

    # rename index
    df.index = df.index.rename('date')

    # find columns with logger properties and those data
    propcols = [col for col in df.columns if not col.startswith('res')]
    datacols = [col for col in df.columns if col.startswith('res')]
    datacols = [col for col in datacols if df[col].notnull().any()]

    # split data strings and re-merge into one dataframe
    propdf = df[propcols]
    propdf.columns = pd.MultiIndex.from_tuples([(c, '') for c in propcols])
    datadf = pd.concat([splitstrings(bh, df[col]) for col in datacols], axis=1)
    df = pd.concat([propdf, datadf], axis=1)

    # read calibration coefficients
    coefs = pd.read_csv(cfilename, index_col=0, comment='#')
    coefs = coefs.loc[df['ixr'].columns]

    # calibrate tilt angles
    df['ixr'] = (df['ixr'] - coefs['bx'])/coefs['ax']
    df['iyr'] = (df['iyr'] - coefs['by'])/coefs['ay']

    # convert temperatures to degrees and pressures to meters of water
    df['p'] *= 1e2/g
    df['t'] /= 1e3

    # return filled dataframe
    return df


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
    except (ValueError, TypeError):
        return np.nan


def splitstrings(bh, ts):
    """Split series of data strings into multi-column data frame."""

    # split data strings into new multi-column dataframe and fill with NaN
    df = ts.str.split(',', expand=True).applymap(floatornan)

    # replace null values by nan
    df = df.replace([-99.199996, 2499.0, 4999.0, 7499.0, 9999.0], np.nan)

    # rename columns
    unitname = bh[0].upper() + 'I%02d' % int(ts.name[-2:-1])
    df.columns = [tiltunit_sensors, [unitname]*len(tiltunit_sensors)]

    # return splitted dataframe
    return df


# Temperature calibration methods
# -------------------------------

def cal_temperature(temp, depth, t0='2014-07-23 11:20', t1='2014-07-23 15:00'):
    """
    Recalibrate lower borehole temperature to melting point.
    Unfortunately initial upper borehole data were lost.
    """
    # FIXME: add upper sensors when possible, remove sensors above surface
    melting_point = -beta * rhoi * g * depth
    initial_temp = temp[t0:t1].mean()
    melt_offset = (melting_point - initial_temp).fillna(0.0)
    return temp + melt_offset


# Main program
# ------------

if __name__ == '__main__':
    """Preprocess borehole data."""

    # make directory or update modification date
    if os.path.isdir('processed'):
        os.utime('processed', None)
    else:
        os.mkdir('processed')

    # preprocess independent data
    vdf = get_dgps_data()
    vdf.to_csv('processed/bowdoin-dgps-velocity-upper.csv')
    tts = get_tide_data().rename('Tide')
    tts.to_csv('processed/bowdoin-tide.csv', header=True)

    # read all data
    pudf = get_pressure_data('upper', pressure_loggers['upper'])
    pldf = get_pressure_data('lower', pressure_loggers['lower'])
    uudf = get_tiltunit_data('upper', tiltunit_loggers['upper'])
    uldf = get_tiltunit_data('lower', tiltunit_loggers['lower'])
    tudf = get_thstring_data('upper', thstring_loggers['upper'])
    tldf = get_thstring_data('lower', thstring_loggers['lower'])
    mudf = get_thstring_data('upper', thstring_loggers['upper'], manual=True)
    mldf = get_thstring_data('lower', thstring_loggers['lower'], manual=True)

    # extract time series
    puw = pudf['wlev'].rename('UP')
    plw = pldf['wlev'].rename('LP')
    put = pudf['temp'].rename('UP')
    plt = pldf['temp'].rename('LP')

    # get initial sensor depths
    puz, plz = sensor_depths_init('pressure', puw, plw)
    uuz, ulz = sensor_depths_init('tiltunit', uudf['p'], uldf['p'])
    tuz, tlz = thstring_depth_init()

    # calibrate temperatures using initial depths
    uldf['t'] = cal_temperature(uldf['t'], ulz)
    tldf = cal_temperature(tldf, tlz)

    # compute borehole base evolution
    pub, plb = borehole_base_evol('pressure')
    tub, tlb = borehole_base_evol('thstring')
    uub, ulb = borehole_base_evol('tiltunit')

    # compute sensor depths evolution
    puz, plz = sensor_depths_evol('pressure', puz, plz)
    tuz, tlz = sensor_depths_evol('thstring', tuz, tlz)
    uuz, ulz = sensor_depths_evol('tiltunit', uuz, ulz)

    # export to csv, force header on time series
    pub.to_csv('processed/bowdoin-pressure-base-upper.csv', header=True)
    plb.to_csv('processed/bowdoin-pressure-base-lower.csv', header=True)
    puz.to_csv('processed/bowdoin-pressure-depth-upper.csv')
    plz.to_csv('processed/bowdoin-pressure-depth-lower.csv')
    put.to_csv('processed/bowdoin-pressure-temp-upper.csv', header=True)
    plt.to_csv('processed/bowdoin-pressure-temp-lower.csv', header=True)
    puw.to_csv('processed/bowdoin-pressure-wlev-upper.csv', header=True)
    plw.to_csv('processed/bowdoin-pressure-wlev-lower.csv', header=True)
    tub.to_csv('processed/bowdoin-thstring-base-upper.csv', header=True)
    tlb.to_csv('processed/bowdoin-thstring-base-lower.csv', header=True)
    tuz.to_csv('processed/bowdoin-thstring-depth-upper.csv')
    tlz.to_csv('processed/bowdoin-thstring-depth-lower.csv')
    mudf.to_csv('processed/bowdoin-thstring-mantemp-upper.csv')
    mldf.to_csv('processed/bowdoin-thstring-mantemp-lower.csv')
    tudf.to_csv('processed/bowdoin-thstring-temp-upper.csv')
    tldf.to_csv('processed/bowdoin-thstring-temp-lower.csv')
    uub.to_csv('processed/bowdoin-tiltunit-base-upper.csv', header=True)
    ulb.to_csv('processed/bowdoin-tiltunit-base-lower.csv', header=True)
    uuz.to_csv('processed/bowdoin-tiltunit-depth-upper.csv')
    ulz.to_csv('processed/bowdoin-tiltunit-depth-lower.csv')
    uudf['t'].to_csv('processed/bowdoin-tiltunit-temp-upper.csv')
    uldf['t'].to_csv('processed/bowdoin-tiltunit-temp-lower.csv')
    uudf['ixr'].to_csv('processed/bowdoin-tiltunit-tiltx-upper.csv')
    uudf['iyr'].to_csv('processed/bowdoin-tiltunit-tilty-upper.csv')
    uldf['ixr'].to_csv('processed/bowdoin-tiltunit-tiltx-lower.csv')
    uldf['iyr'].to_csv('processed/bowdoin-tiltunit-tilty-lower.csv')
    uudf['p'].to_csv('processed/bowdoin-tiltunit-wlev-upper.csv')
    uldf['p'].to_csv('processed/bowdoin-tiltunit-wlev-lower.csv')
