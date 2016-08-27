#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import util as ut

if __name__ == '__main__':

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    utm = ccrs.UTM(19)
    bowd = 504e3, 515.5e3, 8626.5e3, 8619e3

    # initialize figure
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=utm))
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(bowd, crs=utm)

    # plot image data
    filename = 'data/external/S2A_20160808_175915_456_RGB.jpg'
    data, extent = ut.ma.open_gtif(filename)
    data = np.moveaxis(data, 0, 2)
    ax.imshow(data, extent=extent, transform=utm, cmap='Blues')

    # plot locations of cameras
    llz = {'cam_lower': (-68.527481, 77.659782, 490.219243),
           'cam_upper': (-68.504852, 77.691702, 289.044237)}
    ax.plot(*llz['cam_lower'][:2], c=ut.palette['darkorange'], marker='^',
             transform=ll)
    ax.plot(*llz['cam_upper'][:2], c=ut.palette['darkorange'], marker='^',
             transform=ll)

    # save third frame
    fig.savefig('map_s2a')
