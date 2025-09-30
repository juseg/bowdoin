#!/usr/bin/env python
# Copyright (c) 2016-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Extract velocity time series at the boreholes location."""

import os
import zipfile
import numpy as np
import pandas as pd
import netCDF4 as nc4
import cartopy.crs as ccrs

# extract archive
with zipfile.ZipFile('satellite/bowdoin-landsat-uv.zip') as archive:
    namelist = archive.namelist()
    archive.extractall('satellite')

# GPS coordinates on 2015/07/01 00:00
ll = ccrs.PlateCarree()
utm = ccrs.UTM(19)
# FIXME: it looks like the point is slightly misplaced
xb, yb = utm.transform_point(-68.560813961, 77.688492104, ll)

# initialize data dictionary
dd = []

# open data directory
datadir = 'satellite/bowdoin-landsat-uv'
namelist = sorted(os.listdir(datadir))
ulist = [name for name in namelist if name.endswith('u.nc')]
vlist = [name for name in namelist if name.endswith('v.nc')]
for ufile, vfile in zip(ulist, vlist):

    # make sure file names match
    assert ufile.rstrip('u.nc') == vfile.rstrip('v.nc')

    # read velocity data
    upath = os.path.join(datadir, ufile)
    vpath = os.path.join(datadir, vfile)
    unc = nc4.Dataset(upath)
    vnc = nc4.Dataset(vpath)
    x = unc['x'][:]
    y = unc['y'][:]
    u = unc['z'][:]
    v = vnc['z'][:]
    unc.close()
    vnc.close()
    c = (u**2+v**2)**0.5

    # count
    print((c>0).count(), ufile)

    # find index of borehole location
    i = np.argmin(np.abs(x-xb))
    j = np.argmin(np.abs(y-yb))

    # append to dict if non masked
    if not c.mask[j, i]:
        start = ufile[4:8] + ufile[2:4] + ufile[0:2]
        end = ufile[13:17] + ufile[11:13] + ufile[9:11]
        vel = c[j, i]
        err = c[j-1:j+2, i-1:i+2].std()
        dd.append(dict(start=start, end=end, vel=vel, err=err))

# write to csv file
df = pd.DataFrame(dd, columns=['start', 'end', 'vel', 'err'])
df.to_csv('satellite/bowdoin-landsat-uv.csv', index=False, header=True)
