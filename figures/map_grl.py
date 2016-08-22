#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from netCDF4 import Dataset
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import gdal


import util as ut


def open_gtif(filename):
    """Open GeoTIFF and return data and extent."""

    # read image data
    ds = gdal.Open(filename)
    data = ds.ReadAsArray()
    rows, cols = data.shape

    # read geotransform
    gt = ds.GetGeoTransform()
    x0, dx, dxdy, y0, dydx, dy = ds.GetGeoTransform()
    assert dxdy == dydx == 0.0  # rotation parameters should be zero
    x1 = x0 + dx * cols
    y1 = y0 + dy * rows

    # return image data and extent
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


if __name__ == '__main__':

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    proj = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                              true_scale_latitude=70.0)

    # subregions w, e, s, n
    grld = (-725e3, +900e3, -0550e3, -3425e3)  # 1625x2875 (65*25x115*25)
    qaaq = (-650e3, -450e3, -1325e3, -1125e3)  # 200x200
    bowd = (-547e3, -517e3, -1237e3, -1207e3)  # 30x30
    jako = (-300e3, +000e3, -2350e3, -2050e3)  # 300x300

    # read velocity data
    data, extent = open_cci_velocity()

    # initialize figure
    figw, figh = 135.0, 120.0
    fig = plt.figure(0, (figw/25.4, figh/25.4))
    rect1 = [2.5/figw, 2.5/figh, 65.0/figw, 115.0/figh]
    rect2 = [70.0/figw, 67.5/figh, 50.0/figw, 50.0/figh]
    rect3 = [70.0/figw, 2.5/figh, 62.5/figw, 62.5/figh]
    ax1 = fig.add_axes(rect1, projection=proj)
    ax2 = fig.add_axes(rect2, projection=proj)
    ax3 = fig.add_axes(rect3, projection=proj)
    cax = plt.axes([122.5/figw, 77.5/figh, 2.5/figw, 40.0/figh])

    # set rasterization levels
    ax1.set_rasterization_zorder(2.5)
    ax2.set_rasterization_zorder(2.5)
    ax3.set_rasterization_zorder(2.5)

    # set map extents
    ax1.set_extent(grld, crs=proj)
    ax2.set_extent(qaaq, crs=proj)
    ax3.set_extent(bowd, crs=proj)

    # mark inset locations
    mark_inset(ax1, ax2, loc1=2, loc2=3, fc='none', ec='k', lw=0.5)
    mark_inset(ax2, ax3, loc1=1, loc2=2, fc='none', ec='k', lw=0.5)

    # plot ax1 velocity map
    norm = LogNorm(1e0, 1e4)
    im = ax1.imshow(data, extent=extent, cmap='Blues', norm=norm)
    cl = ax1.coastlines(resolution='50m', lw=0.5)

    # plot ax2 velocity map
    im = ax2.imshow(data, extent=extent, cmap='Blues', norm=norm)
    cl = ax2.coastlines(resolution='10m', lw=0.5)

    # add colorbar
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r'surface velocity ($m\,a^{-1}$)', labelpad=0.0)

    # plot ax3 satellite image
    # FIXME: this works only with an internet connection. Replace by
    # a locally-stored satellite image.
    #background = cimgt.MapQuestOpenAerial()
    #ax3.add_image(background, 10)

    # plot locations of camera and boreholes
    llz = {'qaanaaq':   (-69.230556, 77.466667,   0.000000),
           'cam_lower': (-68.527481, 77.659782, 490.219243),
           'cam_upper': (-68.504852, 77.691702, 289.044237),
           'gcp_m1':    (-68.504733, 77.688107, 139.879200),
           'gcp_m2':    (-68.628121, 77.721004, 172.288962),
           'gcp_m3':    (-68.643724, 77.703824, 172.562631),
           'bh1':       (-68.555749, 77.691244,  88.694913),  # upstream
           'bh2':       (-68.555685, 77.691307,  87.746263),  # upstream
           'bh3':       (-68.558857, 77.689995,  83.446628),  # downstream
           'b1501':     (-68.607773, 77.679805,  59.2910),  # 150719 17:30
           'b1502':     (-68.564605, 77.693997,  96.2647),  # 150719 14:30
           'b1503':     (-68.554406, 77.706070, 133.6503),  # 150719 13:00
           'camp':      (-68.509920, 77.685890,  70.000000)}
    ax2.plot(*llz['qaanaaq'][:2], c='k', marker='o',  transform=ll)
    ax3.plot(*llz['bh3'][:2], c=ut.palette['darkblue'], marker='o', transform=ll)
    ax3.plot(*llz['b1501'][:2], c=ut.palette['darkred'], marker='s', transform=ll)
    ax3.plot(*llz['cam_lower'][:2], c=ut.palette['darkorange'], marker='^',
             transform=ll)
    ax3.plot(*llz['cam_upper'][:2], c=ut.palette['darkorange'], marker='^',
             transform=ll)

    # annotate
    ax2.text(-590000, -1250000, 'Qaanaaq', color='k',
             ha='center', fontweight='bold')
    ax3.text(-532500, -1225500, 'boreholes', color=ut.palette['darkblue'],
             ha='center', fontweight='bold')
    ax3.text(-540000, -1229000, 'seismometers', color=ut.palette['darkred'],
             ha='center', fontweight='bold')
    ax3.text(-532000, -1229500, 'cameras', color=ut.palette['darkorange'],
             ha='center', fontweight='bold')

    # add scale
    ax3.plot([-525e3, -520e3], [-1235e3, -1235e3], 'k-|', mew=1.0)
    ax3.text(-522.5e3, -1234e3, '5km', ha='center')

    # save third frame
    fig.savefig('map_grl')
