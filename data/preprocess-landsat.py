#!/usr/bin/env python

"""Extract velocity time series at the boreholes location."""

import os
import zipfile
import numpy as np
import pandas as pd
from osgeo import gdal
import cartopy.crs as ccrs

# extract archive
with zipfile.ZipFile('satellite/bowdoin-landsat.zip') as archive:
    namelist = archive.namelist()
    archive.extractall('satellite')

# GPS coordinates on 2015/07/01 00:00
ll = ccrs.PlateCarree()
utm = ccrs.UTM(19)
xb, yb = utm.transform_point(-68.560813961, 77.688492104, ll)

# initialize data dictionary
dd = []

# open data directory
datadir = 'satellite/bowdoin-landsat'
namelist = sorted(os.listdir(datadir))
for row, basename in enumerate(namelist):

    # read image data
    filename = os.path.join(datadir, basename)
    ds = gdal.Open(filename)
    data = ds.ReadAsArray()
    data = np.ma.masked_where(data==65535, data)

    # read geotransform
    gt = ds.GetGeoTransform()
    x0, dx, dxdy, y0, dydx, dy = ds.GetGeoTransform()
    assert dxdy == dydx == 0.0  # rotation parameters should be zero
    ds = None

    # find index of borehole location
    i = int((xb-x0)/dx)
    j = int((yb-y0)/dy)

    # append to dict if non masked
    if not data.mask[j, i]:
        start = basename[4:8] + basename[2:4] + basename[0:2]
        end = basename[13:17] + basename[11:13] + basename[9:11]
        vel = data[j, i]
        err = data[j-1:j+2, i-1:i+2].std()
        dd.append(dict(start=start, end=end, vel=vel, err=err))

# write to csv file
df = pd.DataFrame(dd, columns=['start', 'end', 'vel', 'err'])
df.to_csv('satellite/bowdoin-landsat.csv', index=False, header=True)
