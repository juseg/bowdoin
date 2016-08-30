#!/usr/bin/env python2
# coding: utf-8

"""Mapping tools."""

import numpy as np
from netCDF4 import Dataset
from osgeo import gdal
import gpxpy
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


# geographic projections
ll = ccrs.PlateCarree()


def open_gtif(filename, extent=None):
    """Open GeoTIFF and return data and extent."""

    # open dataset
    ds = gdal.Open(filename)

    # read geotransform
    x0, dx, dxdy, y0, dydx, dy = ds.GetGeoTransform()
    assert dxdy == dydx == 0.0  # rotation parameters should be zero

    # if extent argument was not given
    if extent is None:

        # set image indexes to cover whole image
        col0 = 0  # index of first (W) column
        row0 = 0  # index of first (N) row
        cols = ds.RasterXSize  # number of cols to read
        rows = ds.RasterYSize  # number of rows to read

    # if extent argument was given
    else:

        # compute image indexes corresponding to map extent
        w, e, s, n = extent
        col0 = int((w-x0)/dx)  # index of first (W) column
        row0 = int((n-y0)/dy)  # index of first (N) row
        col1 = int((e-x0)/dx) + 1  # index of last (E) column
        row1 = int((s-y0)/dy) + 1  # index of last (S) row

        # make sure indexes are within data extent
        col0 = max(0, col0)
        row0 = max(0, row0)
        col1 = min(ds.RasterXSize, col1)
        row1 = min(ds.RasterYSize, row1)

        # compute number of cols and rows needed
        cols = col1 - col0  # number of cols needed
        rows = row1 - row0  # number of rows needed

        # compute coordinates of new origin
        x0 = x0 + col0*dx
        y0 = y0 + row0*dy

    # compute new image extent
    x1 = x0 + dx*cols
    y1 = y0 + dy*rows

    # read image data
    print col0, row0, cols, rows
    data = ds.ReadAsArray(col0, row0, cols, rows)

    # close dataset and return image data and extent
    ds = None
    return data, (x0, x1, y0, y1)


def open_measures_composite():
    """Average MEASURES Greenland velocities over five winters of data."""

    # data file names
    filenames = ['data/external/greenland_vel_mosaic500_2000_2001.tif',
                 'data/external/greenland_vel_mosaic500_2005_2006.tif',
                 'data/external/greenland_vel_mosaic500_2006_2007.tif',
                 'data/external/greenland_vel_mosaic500_2007_2008.tif',
                 'data/external/greenland_vel_mosaic500_2008_2009.tif']

    # read geotiffs
    data, extents = zip(*[open_gtif(f) for f in filenames])

    # check that all extents are the same
    assert extents.count(extents[0]) == len(extents)

    # mask null values
    data = np.ma.masked_equal(data, 0.1)

    # return average and extent
    return data.mean(axis=0), extents[0]


def open_cci_velocity():
    """Average CCI Greenland velocities over two winters of data."""

    # data file names
    filename = 'data/external/greenland_iv_500m_s1_20141101_20151201_v1_0.nc'
    data = []
    extents = []
    intervals = []

    # open dataset
    nc = Dataset(filename)
    x = nc['x'][:]
    y = nc['y'][:]
    c = nc['land_ice_surface_velocity_magnitude'][:]*365.25

    # compute image extent from coordinate vectors
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2

    # compute time interval
    #start = pd.to_datetime(nc.time_coverage_start)  # ! wrong value
    #end = pd.to_datetime(nc.time_coverage_end)      # ! wrong value
    #start = pd.to_datetime(filename.split('_')[4])
    #end = pd.to_datetime(filename.split('_')[5])

    # close dataset
    nc.close()

    # return data and extent
    return c, (w, e, s, n)


def shading(z, dx=None, dy=None, azimuth=315.0, altitude=30.0):
    """Compute shaded relief map."""

    # convert to anti-clockwise rad
    azimuth = -azimuth*np.pi / 180.
    altitude = altitude*np.pi / 180.

    # compute cartesian coords of the illumination direction
    xlight = np.cos(azimuth) * np.cos(altitude)
    ylight = np.sin(azimuth) * np.cos(altitude)
    zlight = np.sin(altitude)
    #zlight = 0.0  # remove shades from horizontal surfaces

    # compute hillshade (dot product of normal and light direction vectors)
    u, v = np.gradient(z, dx, dy)
    return (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)


def slope(z, dx=None, dy=None, smoothing=None):
    """Compute slope map with optional smoothing."""

    # optionally smooth data
    if smoothing:
        import scipy.ndimage as ndimage
        z = ndimage.filters.gaussian_filter(z, smoothing)

    # compute gradient along each coordinate
    u, v = np.gradient(z, dx, dy)

    # compute slope
    slope = (u**2 + v**2)**0.5
    return slope


def extent_from_coords(x, y):
    """Compute image extent from coordinate vectors."""
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2
    return w, e, s, n

def coords_from_extent(extent, cols, rows):
    """Compute coordinate vectors from image extent."""

    # compute dx and dy
    (w, e, s, n) = extent
    dx = (e-w) / cols
    dy = (n-s) / rows

    # prepare coordinate vectors
    xwcol = w + 0.5*dx  # x-coord of W row cell centers
    ysrow = s + 0.5*dy  # y-coord of N row cell centers
    x = xwcol + np.arange(cols)*dx  # from W to E
    y = ysrow + np.arange(rows)*dy  # from S to N

    # return coordinate vectors
    return x, y


def annotate(name, ax=None, text=None, color=None, marker=None):
    """Plot and annotate waypoint from GPX file"""

    # get current axes if None given
    ax = ax or plt.gca()

    # open GPX file
    with open('data/locations.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for wpt in gpx.waypoints:
            if wpt.name == name:
                #c = ut.colors['downstream']
                xy = ax.projection.transform_point(wpt.longitude, wpt.latitude, ll)
                ax.plot(*xy, color=color, marker=marker)
                if text:
                    ax.annotate(text, xy=xy, xytext=(-10, 10), color=color,
                        ha='right', va='bottom', fontweight='bold',
                        textcoords='offset points',
                        bbox=dict(pad=0, ec='none', fc='none'),
                        arrowprops=dict(arrowstyle='->', color=color,
                                        relpos=(1, 0)))

