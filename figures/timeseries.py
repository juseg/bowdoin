#!/usr/bin/env python2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

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
    filename = 'data/processed/bowdoin-pressure-%s.csv' % bh
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    wlev = df['wlev'].resample('30T')  # resample and fill with nan
    wlev = wlev[2:]  # remove the first hour corresponding to drilling
    wlev.plot(c=colors[i], lw=2.0)
    lines[i] = ax.get_lines()[-1]  # select last line for the legend

    # subset water level series for calibration
    calint = wlev_calib_intervals[i]
    wlev = wlev[calint[0]:calint[1]]

    # open tilt unit water level data
    filename = 'data/processed/bowdoin-inclino-%s.csv' % bh
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    pcols = [col for col in df.columns if col.startswith('p')]

    # infer unit height above the bedrock from pressure sensor data
    # plot only if there is a good match with pressure sensor data
    for col, tiltwlev in (df[pcols]*9.80665).iteritems():
        diff = tiltwlev[wlev.index]-wlev  # difference over calib interval
        tiltwlev -= diff.mean()  # correct for inferred unit height
        if diff.std() < 1.0:  # std of difference below one meter
            tiltwlev.plot(ax=ax, c='k', alpha=0.2, legend=False)

# set axes properties
ax.set_ylim(0, 400)
ax.set_ylabel('water level (m)')
ax.legend(lines, boreholes)

# add new axes
ax = ax.twinx()

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
positions = pd.DataFrame(positions, columns=list('xyz'), index=df.index)

# compute cartesian velocities and norm
velocities = positions.diff()/15*60*24*365.0
vx = velocities['x']
vy = velocities['y']
vz = velocities['z']
v = (velocities**2).sum(axis='columns')**0.5

# compute horizontal component, azimuth and altitude
vh = (vx**2 + vy**2)**0.5
azimuth = np.arctan2(vy, vx)*180/np.pi
altitude = np.arctan2(vz, vh)*180/np.pi

# print statistics
print 'mean h. speed: %.03f' % vh.mean()
print 'mean v. speed: %.03f' % vz.mean()
print 'mean azimuth:  %.03f' % azimuth.mean()
print 'mean altitude: %.03f' % altitude.mean()

# plot
rollplot(vh, 4*3, c='k')

# set axes properties
ax.set_xlim('2014-07-17', '2015-07-20')
ax.set_ylim(0, 2000)
ax.set_ylabel('horizontal velocity (m/a)')

# save
fig.savefig('timeseries')
