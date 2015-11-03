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


# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)
filename = 'data/processed/bowdoin-gps-upstream.csv'

# read in a record array
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
rollplot(vh, 4*3)

# zoom on summer 2015
ax.set_xlim('2015-05-22', '2015-07-22')

# save
fig.savefig('plot-gps')
