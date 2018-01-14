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
    bowd = 505.0e3, 513.5e3, 8619.5e3, 8625.5e3

    # initialize figure
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], projection=utm)
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(bowd, crs=utm)

    # plot image data
    filename = '../data/external/S2A_20160808_175915_456_RGB.jpg'
    data, extent = ut.io.open_gtif(filename)
    data = np.moveaxis(data, 0, 2)
    ax.imshow(data, extent=extent, transform=utm, cmap='Blues')

    # plot borehole and camera locations
    kwa = dict(color=ut.colors['upper'], marker='o')
    ut.pl.add_waypoint('B14BH1', **kwa)
    ut.pl.add_waypoint('B16BH1', **kwa)
    ut.pl.add_waypoint('B17BH1', **kwa)
    kwa = dict(color=ut.colors['lower'], marker='o')
    ut.pl.add_waypoint('B14BH3', text='2014', **kwa)
    ut.pl.add_waypoint('B16BH3', text='2016', **kwa)
    ut.pl.add_waypoint('B17BH3', text='2017', **kwa)
    kwa = dict(color=ut.palette['darkorange'], marker='^')
    ut.pl.add_waypoint('Camera Upper', **kwa)
    ut.pl.add_waypoint('Camera Lower', text='Camera', **kwa)
    kwa = dict(color=ut.palette['darkgreen'], marker='^')
    ut.pl.add_waypoint('Tent Swiss', text='Camp', textpos='ur', **kwa)
    ut.pl.add_waypoint('Camp Hill', **kwa)

    # save
    ut.pl.savefig(fig)
