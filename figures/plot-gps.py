#!/usr/bin/env python2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)
filename = 'data/processed/bowdoin-gps-upstream.csv'

# read in a record array
df = pd.read_csv(filename, parse_dates=True, index_col='GPST')

# find samples not taken at multiples of 15 min (900 sec) and remove them
# it seems that these (18) values were recorded directly after each data gap
inpace = (60*df.index.minute + df.index.second) % 900 == 0
assert (not inpace.sum() < 20)  # make sure we remove less than 20 values
df = df[inpace]

# resample with 15 minute frequency and fill with NaN
df = df.resample('15T')

# extract dates and displacement
date = df.index.values
lon = df['longitude'].values
lat = df['latitude'].values
z = df['height'].values

# convert lon/lat to UTM 19 meters
ll = ccrs.PlateCarree() 
proj = ccrs.UTM(19)
points = proj.transform_points(ll, lon, lat, z)
x, y, z = tuple(points.T)

# compute time gradient
seconds = (df.index - df.index[0]).astype('timedelta64[s]')
years = seconds/(24*3600*365.0)
dt = np.gradient(years)

# compute cartesian velocities and norm
vx = np.gradient(x)/dt
vy = np.gradient(y)/dt
vz = np.gradient(z)/dt
v = (vx**2 + vy**2 + vz**2)**0.5

# very high velocities correspond to antenna displacements
mask = (v > 1e4)
vx = np.ma.array(vx, mask=mask)
vy = np.ma.array(vy, mask=mask)
vz = np.ma.array(vz, mask=mask)
v = np.ma.array(v, mask=mask)

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
ax.plot_date(date, vh, 'b.')
ax.plot_date(date, vz, 'r.')

# zoom on summer 2015
ax.set_xlim('2015-05-22', '2015-07-22')

# save
fig.savefig('plot-gps')
