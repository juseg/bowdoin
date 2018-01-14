#!/usr/bin/env python2

import numpy as np
import pandas as pd
import cartopy.crs as ccrs

columns = ['daydate', 'time', 'lat', 'lon', 'z', 'Q', 'ns',
           'sdn', 'sde', 'sdu', 'sdne', 'sdeu', 'sdun', 'age', 'ratio']


def get_velocity(method='backward'):
    """Return lon/lat gps positions in a data frame."""

    # check argument validity
    assert method in ('backward', 'forward', 'central')

    # append dataframes corresponding to each year
    dflist = []
    df = pd.concat([pd.read_fwf('original/gps/B14BH1/B14BH1_%d_15min.dat' % year,
                                names=columns, index_col=0,
                                usecols=['daydate', 'time', 'lon', 'lat', 'z'],
                                parse_dates={'date': ['daydate', 'time']})
                    for year in [2014, 2015, 2016, 2017]])

    # find samples not taken at multiples of 15 min (900 sec) and remove them
    # it seems that these (18) values were recorded directly after each data gap
    inpace = (60*df.index.minute + df.index.second) % 900 == 0
    assert (not inpace.sum() < 20)  # make sure we remove less than 20 values
    df = df[inpace]

    # convert lon/lat to UTM 19 meters
    ll = ccrs.PlateCarree()
    proj = ccrs.UTM(19)
    points = proj.transform_points(ll, df['lon'].values, df['lat'].values)
    df['x'] = points[:,0]
    df['y'] = points[:,1]

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


# preprocess gps data
df = get_velocity()
df.to_csv('processed/bowdoin-dgps-velocity-upper.csv')
