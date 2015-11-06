#!/usr/bin/env python2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def get_pressure_wlev(bh):
    """Get water level from pressure sensor in a dataframe."""
    filename = 'data/processed/bowdoin-pressure-%s.csv' % bh
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    df = df['wlev'].resample('30T')  # resample and fill with nan
    return df[2:]  # remove the first hour corresponding to drilling


def get_tiltunit_wlev(bh):
    """Get water level from tilt sensor units in a dataframe."""

    # calibration interval
    calint = {'upstream':   ['2014-07-18', '2014-07-22'],
              'downstream': ['2014-07-29', '2014-08-02']}[bh]

    # open tilt unit water level data
    filename = 'data/processed/bowdoin-inclino-%s.csv' % bh
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    df = df[[col for col in df.columns if col.startswith('p')]]*9.80665

    # compute difference with pressure sensor data over calib interval
    wlev = get_pressure_wlev(bh)
    wlev = wlev[calint[0]:calint[1]]
    diff = df.loc[wlev.index].sub(wlev, axis=0)

    # subtract mean difference as inferred unit height
    df -= diff.mean()

    # return columns with std of difference below one meter
    return df[df.columns[(diff.std() < 1.0)]]


def get_gps_positions():
    """Get UTM 19 GPS positions in a dataframe."""

    # open GPS data
    filename = 'data/processed/bowdoin-gps-upstream.csv'
    df = pd.read_csv(filename, parse_dates=True, index_col='date')

    # find samples not taken at multiples of 15 min (900 sec) and remove them
    # it seems that these (18) values were recorded directly after each data gap
    inpace = (60*df.index.minute + df.index.second) % 900 == 0
    assert (not inpace.sum() < 20)  # make sure we remove less than 20 values
    df = df[inpace]

    # resample with 15 minute frequency and fill with NaN
    df = df.resample('15T')

    # convert lon/lat to UTM 19 meters
    ll = ccrs.PlateCarree()
    proj = ccrs.UTM(19)
    positions = df[['longitude', 'latitude', 'height']]
    positions = proj.transform_points(ll, *positions.values.T)
    return pd.DataFrame(positions, columns=list('xyz'), index=df.index)


def get_gps_velocity(method='backward'):
    """Get UTM 19 GPS velocity components in a dataframe."""
    df = get_gps_positions()
    if method == 'backward':
        df = df.diff()
    elif method == 'forward':
        df = -df.diff(-1)
    elif method == 'central':
        df = (positions.diff()-positions.diff(-1))/2.0
    else:
        raise ValueError, 'method should be one backward, forward, central.'
    return df/15*60*24*365.0


def rollplot(arg, window, c='b'):
    mean = pd.rolling_mean(arg, window)
    std = pd.rolling_std(arg, window)
    arg.plot(c=c, ls='', marker='.', markersize=0.5)
    mean.plot(c=c, ls='-')
    plt.fill_between(arg.index, mean-2*std, mean+2*std, color=c, alpha=0.1)


# parameters
boreholes = ['upstream', 'downstream']
colors = ['b', 'r']
lines = [None, None]

# interval to match tilt unit pressure against water level from bottom
wlev_calib_intervals = [['2014-07-18', '2014-07-22'],
                        ['2014-07-29', '2014-08-02']]

# initialize figure
fig, ax = plt.subplots(1, 1)

# for each borehole
for i, bh in enumerate(boreholes):

    # plot pressure sensor water level
    df = get_pressure_wlev(bh)
    df.plot(c=colors[i], lw=2.0)
    lines[i] = ax.get_lines()[-1]  # select last line for the legend

    # plot tilt unit water level
    df = get_tiltunit_wlev(bh)
    df.plot(ax=ax, c='k', alpha=0.2, legend=False)

# set axes properties
ax.set_ylim(100, 400)
ax.set_ylabel('water level (m)')
ax.legend(lines, boreholes)

# set spine properties
ax.spines['left'].set_smart_bounds(True)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')

# add new axes
ax = ax.twinx()

# get GPS velocity
df = get_gps_velocity()

# compute horizontal component, azimuth and altitude
vh = (df['x']**2 + df['y']**2)**0.5
azimuth = np.arctan2(df['y'], df['x']**2)*180/np.pi
altitude = np.arctan2(df['z'], vh)*180/np.pi

# plot
rollplot(vh, 4*3, c='k')

# set axes properties
ax.set_xlim('2014-07-17', '2015-07-20')
ax.set_ylim(-1000, 1000)
ax.set_ylabel('horizontal velocity (m/a)')

# set spine properties
ax.spines['right'].set_smart_bounds(True)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('right')
ax.xaxis.set_ticks_position('bottom')

# save
fig.savefig('timeseries')
