#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import util as ut
import gpxpy

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

    # plot borehole and camera locations
    kwa = dict(color=ut.colors['upstream'], marker='o')
    ut.ma.annotate('B14BH1', **kwa)
    ut.ma.annotate('B16BH1', **kwa)
    kwa = dict(color=ut.colors['downstream'], marker='o')
    ut.ma.annotate('B14BH3', text='2014', **kwa)
    ut.ma.annotate('B16BH3', text='2016', **kwa)
    kwa = dict(color=ut.palette['darkorange'], marker='^')
    ut.ma.annotate('Camera Upper', **kwa)
    ut.ma.annotate('Camera Lower', **kwa)

    # save
    fig.savefig('map_s2a')
