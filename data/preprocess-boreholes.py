#!/usr/bin/env python

"""Preprocess Bowdoin 2014 to 2017 borehole data."""

import os
import gpxpy
import numpy as np
import pandas as pd
import cartopy.crs as ccrs


# Global data
# -----------

# borehole depths measured immediately after drilling
DRILLING_DATES = None  # FIXME
INITIAL_DEPTHS = dict(bh1=272.0, bh2=262.0, bh3=252.0)

# data logger names
INCLINOMETER_LOGGERS = dict(lower='BOWDOIN-1', upper='BOWDOIN-2')
PIEZOMETER_LOGGERS = dict(lower='drucksens073303', upper='drucksens094419')
THERMISTOR_LOGGERS = dict(lower='Th-Bowdoin-1', upper='Th-Bowdoin-2')

# observations of initial borehole water depths
INITIAL_WATER_DEPTHS = dict(bh1=48.0, bh2=46.0, bh3=0.0)
INITIAL_WATER_TIMING = dict(bh1='2014-07-17 18:07:00',  # assumed
                            bh2='2014-07-17 18:07:00',  # assumed
                            bh3='2014-07-23 00:30:00')  # assumed

# temperature recalibration intervals
RECALIB_INTERVALS = dict(bh1=('2014-07-20 18:00', '2014-07-21 02:00'),
                         bh2=('2014-07-18 00:00', '2014-07-22 00:00'),
                         bh3=('2014-07-23 12:00', '2014-07-23 20:00'))


# Borehole location methods
# -------------------------

def borehole_distances(upper='bh1', lower='bh3'):
    """
    Compute the time evolution of the distance between two boreholes.

    Parameters
    ----------
    upper: string
        The name of the upper borehole.
    lower: string
        The name of the lower borehole.
    """
    # FIXME: Borehole distances will become unnecessary when using RADAR data.

    # projections used to compute distances
    lonlat = ccrs.PlateCarree()
    utm = ccrs.UTM(19)

    # initialize empty data series
    upper_x = pd.Series()
    upper_y = pd.Series()
    lower_x = pd.Series()
    lower_y = pd.Series()

    # read GPX file
    with open('../data/locations.gpx', 'r') as gpx_file:
        for wpt in gpxpy.parse(gpx_file).waypoints:
            if upper.upper() in wpt.name:
                upper_x[wpt.time], upper_y[wpt.time] = \
                    utm.transform_point(wpt.longitude, wpt.latitude, lonlat)
            elif lower.upper() in wpt.name:
                lower_x[wpt.time], lower_y[wpt.time] = \
                    utm.transform_point(wpt.longitude, wpt.latitude, lonlat)

    # sort by date
    for series in upper_x, upper_y, lower_x, lower_y:
        series.sort_index(inplace=True)

    # ensure series have same length
    assert len(upper_x) == len(upper_y) == len(lower_x) == len(lower_y)

    # compute distances
    distances = ((upper_x.values-lower_x.values)**2 +
                 (upper_y.values-lower_y.values)**2)**0.5

    # get average dates
    avg_dates = lower_x.index + (upper_x.index-lower_x.index)/2

    # return as a pandas series
    distances = pd.Series(index=avg_dates, data=distances).sort_index()
    distances.index.name = 'date'
    return distances


def borehole_thinning(uz, lz, distances):
    """Estimate thinning based on distance between boreholes."""
    # FIXME: In practice this area conservation approach is not working.
    # FIXME: Besides one should include ice melt in the computation.
    dz = (uz+lz) / 2 * (distances[0]/distances-1)
    return dz


def borehole_base_evol(upper='bh1', lower='bh3'):
    """
    Compute the time evolution of the depths of two boreholes based on the
    evolution of the distance between the two boreholes and assuming
    conservation of the area of the long-section between them.
    """
    # FIXME: In practice this area conservation approach is not working.
    # FIXME: Instead it should be possible to use ice-penetrating RADAR data.

    # get initial borehole base
    ubase = INITIAL_DEPTHS[upper]
    lbase = INITIAL_DEPTHS[lower]

    # compute time-dependent depths
    distances = borehole_distances(upper=upper, lower=lower)
    thinning = borehole_thinning(ubase, lbase, distances)

    # apply thinning and rename data series
    ubase = (thinning+ubase).rename(upper.upper()+'B')
    lbase = (thinning+lbase).rename(lower.upper()+'B')

    # return depth data series
    return ubase, lbase


# Sensor depth methods
# --------------------

def locate_inclinometers(borehole, wlev):
    """
    Compute inclinometer depths from the initial borehole water level.
    Return initial depth for each sensor as a series.

    Parameters
    ----------
    borehole: string
        Borehole name bh1, bh2 or bh3
    wlev: DataFrame
        Water level above the inclinometers
    """

    # get the initial water depth and time of observation
    water_depth = INITIAL_WATER_DEPTHS[borehole]
    observ_time = INITIAL_WATER_TIMING[borehole]

    # sensor depth is the recorded water level plus the observed water depth
    depth = wlev.loc[observ_time].squeeze() + water_depth

    # return sensor depths
    return depth


def locate_piezometers(borehole, wlev):
    """
    Compute piezometer depth from the initial borehole water level.
    Return output as a series with lenght one.

    Parameters
    ----------
    borehole: string
        Borehole name bh1, bh2 or bh3
    wlev: Series
        Water level above the inclinometers
    """

    # get the initial water depth and time of observation
    water_depth = INITIAL_WATER_DEPTHS[borehole]
    observ_time = INITIAL_WATER_TIMING[borehole]

    # sensor depth is the recorded water level plus the observed water depth
    depth = wlev.loc[observ_time].mean() + water_depth
    depth = pd.Series(data=depth, index=[wlev.name], name=observ_time)

    # return sensor depths
    return depth


def sensor_depths_evol(upper_dept, lower_dept, upper='bh1', lower='bh3'):
    """Return time-dependent sensor depths as data frames."""

    # get initial borebole depths
    ubase = INITIAL_DEPTHS[upper]
    lbase = INITIAL_DEPTHS[lower]

    # compute time-dependent depths
    distances = borehole_distances(upper=upper, lower=lower)
    thinning = borehole_thinning(ubase, lbase, distances)

    # apply thinning
    upper_dept = thinning.apply(lambda d: upper_dept * (1+d/ubase))
    lower_dept = thinning.apply(lambda d: lower_dept * (1+d/lbase))

    # return depth data series
    return upper_dept, lower_dept


def locate_thermistors():
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
    # ubase = INITIAL_DEPTHS['bh2']
    # lbase = INITIAL_DEPTHS['bh3']

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

def read_gps_data(method='backward'):
    """Return lon/lat gps positions in a data frame."""

    # check argument validity
    assert method in ('backward', 'forward', 'central')

    # append dataframes corresponding to each year
    names = ['daydate', 'time', 'lat', 'lon', 'z', 'Q', 'ns',
             'sdn', 'sde', 'sdu', 'sdne', 'sdeu', 'sdun', 'age', 'ratio']
    df = pd.concat([
        pd.read_fwf('original/gps/B14BH1/B14BH1_%d_15min.dat' % year,
                    names=names, index_col=0,
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


def read_tide_data(order=2, cutoff=1/300.0):
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

def read_inclinometer_data(site, gravity=9.80665):
    """Return upper (BH1) or lower (BH3) inclinometer data in a data frame."""

    def floatornan(x):
        """Try to convert to float and return NaN if that fails."""
        try:
            return float(x)
        except (ValueError, TypeError):
            return np.nan

    def splitstrings(site, ts):
        """Split series of data strings into multi-column data frame."""

        # split data strings into new multi-column dataframe and fill with NaN
        df = ts.str.split(',', expand=True).applymap(floatornan)

        # replace null values by nan
        df = df.replace([-99.199996, 2499.0, 4999.0, 7499.0, 9999.0], np.nan)

        # rename columns
        sensors = ['id', 'tilx', 'tily', 'magx', 'magy', 'magz',
                   'wlev', 'tpre', 'temp']
        unitname = site[0].upper() + 'I' + ts.name[-2:-1].zfill(2)
        df.columns = [sensors, [unitname]*len(sensors)]

        # return split dataframe
        return df

    # input file names
    logger = INCLINOMETER_LOGGERS[site]
    ifilename = 'original/inclino/' + logger + '_All.dat'
    cfilename = 'original/inclino/' + logger + '_Coefs.dat'

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
    datadf = pd.concat([splitstrings(site, df[col]) for col in datacols],
                       axis=1)
    df = pd.concat([propdf, datadf], axis=1)

    # read calibration coefficients
    coefs = pd.read_csv(cfilename, index_col=0, comment='#')
    coefs = coefs.loc[df['tilx'].columns]

    # calibrate tilt angles
    df['tilx'] = (df['tilx'] - coefs['bx'])/coefs['ax']
    df['tily'] = (df['tily'] - coefs['by'])/coefs['ay']

    # convert pressure to meters of water and temperature to degrees
    df['wlev'] *= 1e2/gravity
    df['temp'] /= 1e3

    # return filled dataframe
    return df


def read_piezometer_data(site):
    """Return upper (BH2) or lower (BH3) piezometer data in a data frame."""

    # date parser
    def parser(year, day, time):
        datestring = year + day.zfill(3) + time.zfill(4)
        return pd.datetime.strptime(datestring, '%Y%j%H%M')

    # read original file
    logger = PIEZOMETER_LOGGERS[site]
    names = ['id', 'year', 'day', 'time', 'temp', 'pres', 'wlev']
    df = pd.read_csv('original/pressure/%s_final_storage_1.dat' % logger,
                     names=names, index_col='date',
                     na_values=[-99999], date_parser=parser,
                     parse_dates={'date': ['year', 'day', 'time']})

    # the lower sensor recorded crap after Feb. 3, 2017
    if site == 'lower':
        df = df[:'20170203 1500']

    # return dataframe
    return df


def read_thermistor_data(site, suffix='Therm'):
    """
    Return upper (BH2) or lower (BH3) thermistor data in a data frame.

    Parameters
    ----------
    site : string
        borehole site 'lower' or 'upper'.
    suffix : string
        data file suffix 'Manual', 'Masked', or 'Therm'.
    """

    # input file names
    logger = THERMISTOR_LOGGERS[site]
    cfilename = 'original/temperature/%s_Coefs.dat' % logger
    ifilename = 'original/temperature/%s_%s.dat' % (logger, suffix)

    # read rearranged calibration coefficients
    # sensor order lower: BH2A[1-9] + BH2B[1-7],
    #              upper: BH1A[1-9] + BH1B[1-4,7,5-6].
    a1, a2, a3 = np.loadtxt(cfilename, unpack=True)

    # read resistance data
    df = pd.read_csv(ifilename, index_col=0, comment='#', na_values='NAN',
                     skipinitialspace=True,
                     skiprows=([0]+(suffix == 'Therm')*[2, 3]))
    df = df[['Resist({:d})'.format(i+1) for i in range(16)]]

    # compute temperature from resistance
    if suffix != 'Masked':
        df = np.log(df)
        df = 1 / (a1 + a2*df + a3*df**3) - 273.15

    # rename index and columns
    df.index = df.index.rename('date')
    df.columns = [site[0].upper() + 'T%02d' % (i+1) for i in range(16)]

    # return as dataframe
    return df


# Temperature calibration methods
# -------------------------------

def temperature_correction(borehole, temp, depth, clapeyron=CLAPEYRON,
                           density=DENSITY, gravity=GRAVITY):
    """
    Compute temperature recalibration offsets assuming that all temperatures
    were at the melting point for a given time interval following the drilling.
    Sensors depicting unstable temperatures (std > 0.01 K) are interpreted to
    be either exposed to air temperatures or already refreezing and thus
    applied a zero correction. Unfortunately the initial upper (BH1, BH2) data
    were lost such that several sensors are already undergoing freezing when
    the record starts.

    Parameters
    ----------
    beta : scalar
        Clapeyron constant for ice (default: Luethi et al., 2002)
    gravity : scalar
        Standard gravity in m s-2
    rho_i : scalar
        Ice density in kg m-3
    start : datetime-like
        Start of the calibration interval
    end: datetime-like
        End of the calibration interval
    """
    start, end = RECALIB_INTERVALS[borehole]
    melting_point = -beta * rho_i * gravity * depth
    initial_temp = temp[start:end].mean()
    stable_cond = temp[start:end].std() < 0.01
    melt_offset = stable_cond * (melting_point - initial_temp).fillna(0.0)
    return melt_offset.squeeze()


# Main program
# ------------

def main():
    """Preprocess borehole data."""

    # make directory or update modification date
    if os.path.isdir('processed'):
        os.utime('processed', None)
    else:
        os.mkdir('processed')

    # preprocess independent data
    bh1_gps = read_gps_data()
    bh1_gps.to_csv('processed/bowdoin.bh1.gps.csv')
    tts = read_tide_data().rename('Tide')
    tts.to_csv('processed/bowdoin.tide.csv', header=True)

    # read all data except pre-field
    bh1_inc = read_inclinometer_data('upper')['2014-07':]
    bh3_inc = read_inclinometer_data('lower')['2014-07':]
    bh2_pzm = read_piezometer_data('upper')['2014-07':]
    bh3_pzm = read_piezometer_data('lower')['2014-07':]
    bh2_thr_temp = read_thermistor_data('upper')['2014-07':]
    bh3_thr_temp = read_thermistor_data('lower')['2014-07':]
    bh2_thr_manu = read_thermistor_data('upper', suffix='Manual')
    bh3_thr_manu = read_thermistor_data('lower', suffix='Manual')
    bh2_thr_mask = read_thermistor_data('upper', suffix='Masked')
    bh3_thr_mask = read_thermistor_data('lower', suffix='Masked')

    # extract time series
    bh2_pzm_wlev = bh2_pzm['wlev'].rename('UP')
    bh2_pzm_temp = bh2_pzm['temp'].rename('UP')
    bh3_pzm_wlev = bh3_pzm['wlev'].rename('LP')
    bh3_pzm_temp = bh3_pzm['temp'].rename('LP')

    # get initial sensor depths
    bh1_inc_dept = locate_inclinometers('bh1', bh1_inc.wlev)
    bh3_inc_dept = locate_inclinometers('bh3', bh3_inc.wlev)
    bh2_pzm_dept = locate_piezometers('bh2', bh2_pzm_wlev)
    bh3_pzm_dept = locate_piezometers('bh3', bh3_pzm_wlev)
    bh2_thr_dept, bh3_thr_dept = locate_thermistors()

    # recalibrate temperatures using initial depths
    bh1_inc.temp += temperature_correction('bh1', bh1_inc.temp, bh1_inc_dept)
    bh3_inc.temp += temperature_correction('bh3', bh3_inc.temp, bh3_inc_dept)
    bh2_pzm_temp += temperature_correction('bh2', bh2_pzm_temp, bh2_pzm_dept)
    bh3_pzm_temp += temperature_correction('bh3', bh3_pzm_temp, bh3_pzm_dept)
    bh2_thr_corr = temperature_correction('bh2', bh2_thr_temp, bh2_thr_dept)
    bh2_thr_temp += bh2_thr_corr
    bh2_thr_manu += bh2_thr_corr
    bh3_thr_corr = temperature_correction('bh3', bh3_thr_temp, bh3_thr_dept)
    bh3_thr_manu += bh3_thr_corr
    bh3_thr_temp += bh3_thr_corr

    # compute borehole base evolution
    # FIXME: base depths should be independent of instrument type
    bh1_inc_base, bh3_inc_base = borehole_base_evol(upper='bh1', lower='bh3')
    bh2_pzm_base, bh3_pzm_base = borehole_base_evol(upper='bh2', lower='bh3')
    bh2_thr_base, bh3_thr_base = borehole_base_evol(upper='bh2', lower='bh3')

    # compute sensor depths evolution
    bh1_inc_dept, bh3_inc_dept = sensor_depths_evol(
        bh1_inc_dept, bh3_inc_dept, upper='bh1', lower='bh3')
    bh2_pzm_dept, bh3_pzm_dept = sensor_depths_evol(
        bh2_pzm_dept, bh3_pzm_dept, upper='bh2', lower='bh3')
    bh2_thr_dept, bh3_thr_dept = sensor_depths_evol(
        bh2_thr_dept, bh3_thr_dept, upper='bh2', lower='bh3')

    # export to csv, force header on time series
    # FIXME: base depths should be independent of instrument type
    bh1_inc_base.to_csv('processed/bowdoin.bh1.inc.base.csv', header=True)
    bh3_inc_base.to_csv('processed/bowdoin.bh3.inc.base.csv', header=True)
    bh1_inc_dept.to_csv('processed/bowdoin.bh1.inc.dept.csv')
    bh3_inc_dept.to_csv('processed/bowdoin.bh3.inc.dept.csv')
    bh1_inc.temp.to_csv('processed/bowdoin.bh1.inc.temp.csv')
    bh3_inc.temp.to_csv('processed/bowdoin.bh3.inc.temp.csv')
    bh1_inc.tilx.to_csv('processed/bowdoin.bh1.inc.tilx.csv')
    bh1_inc.tily.to_csv('processed/bowdoin.bh1.inc.tily.csv')
    bh3_inc.tilx.to_csv('processed/bowdoin.bh3.inc.tilx.csv')
    bh3_inc.tily.to_csv('processed/bowdoin.bh3.inc.tily.csv')
    bh1_inc.wlev.to_csv('processed/bowdoin.bh1.inc.wlev.csv')
    bh3_inc.wlev.to_csv('processed/bowdoin.bh3.inc.wlev.csv')
    bh2_pzm_base.to_csv('processed/bowdoin.bh2.pzm.base.csv', header=True)
    bh3_pzm_base.to_csv('processed/bowdoin.bh3.pzm.base.csv', header=True)
    bh2_pzm_dept.to_csv('processed/bowdoin.bh2.pzm.dept.csv')
    bh3_pzm_dept.to_csv('processed/bowdoin.bh3.pzm.dept.csv')
    bh2_pzm_temp.to_csv('processed/bowdoin.bh2.pzm.temp.csv', header=True)
    bh3_pzm_temp.to_csv('processed/bowdoin.bh3.pzm.temp.csv', header=True)
    bh2_pzm_wlev.to_csv('processed/bowdoin.bh2.pzm.wlev.csv', header=True)
    bh3_pzm_wlev.to_csv('processed/bowdoin.bh3.pzm.wlev.csv', header=True)
    bh2_thr_base.to_csv('processed/bowdoin.bh2.thr.base.csv', header=True)
    bh3_thr_base.to_csv('processed/bowdoin.bh3.thr.base.csv', header=True)
    bh2_thr_dept.to_csv('processed/bowdoin.bh2.thr.dept.csv')
    bh3_thr_dept.to_csv('processed/bowdoin.bh3.thr.dept.csv')
    bh2_thr_manu.to_csv('processed/bowdoin.bh2.thr.manu.csv')
    bh3_thr_manu.to_csv('processed/bowdoin.bh3.thr.manu.csv')
    bh2_thr_mask.to_csv('processed/bowdoin.bh2.thr.mask.csv')
    bh3_thr_mask.to_csv('processed/bowdoin.bh3.thr.mask.csv')
    bh2_thr_temp.to_csv('processed/bowdoin.bh2.thr.temp.csv')
    bh3_thr_temp.to_csv('processed/bowdoin.bh3.thr.temp.csv')


if __name__ == '__main__':
    main()
