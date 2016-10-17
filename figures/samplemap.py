#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import util as ut
import gpxpy

from mpl_toolkits.axes_grid1.inset_locator import mark_inset

if __name__ == '__main__':

    # geographic projections
    ll = ccrs.PlateCarree()
    utm = ccrs.UTM(19)
    limits = [[505.5e3, 513.5e3, 8619.5e3, 8625.5e3]] * 5

    # regions w, e, s, n
    regions = [
        (503750, 516250, 8619000, 8629000),  # Bowdoin 12.5x10.0 km
        (505000, 506500, 8621350, 8622350),  # Sentinel nunatak 1.5x1.0
        (509000, 513000, 8620000, 8622000),  # Bartlett hill 4.0x2.0
        (511350, 512350, 8623000, 8624300),  # Upper cam hill 1.0x1.3
        (514250, 515250, 8625100, 8625800)]  # East arm moraine 1.0x0.7

    # initialize figure
    figw, figh = 175.0, 150.0
    fig = plt.figure(0, (figw/25.4, figh/25.4))
    frames = [[0.0/figw, 50.0/figh, 125.0/figw, 100.0/figh],
              [0.0/figw, 0.0/figh, 75.0/figw, 50.0/figh],
              [75.0/figw, 0.0/figh, 100.0/figw, 50.0/figh],
              [125.0/figw, 50.0/figh, 50.0/figw, 65.0/figh],
              [125.0/figw, 115.0/figh, 50.0/figw, 35.0/figh]]
    grid = [fig.add_axes(rect, projection=utm) for rect in frames]
    for ax, reg in zip(grid, regions):
        ax.set_extent(reg, crs=utm)
        ax.outline_patch.set_linewidth(2.0)
        ax.outline_patch.set_edgecolor('w')

    # mark inset locations
    kwa = dict(fc='none', ec='w', lw=1.0)
    mark_inset(grid[0], grid[1], loc1=1, loc2=2, **kwa)
    mark_inset(grid[0], grid[2], loc1=1, loc2=2, **kwa)
    mark_inset(grid[0], grid[3], loc1=2, loc2=3, **kwa)
    mark_inset(grid[0], grid[4], loc1=2, loc2=3, **kwa)

#    # plot S2A image
#    filename = 'data/S2A_20160808_175915_456_RGB.jpg'
#    data, extent = ut.io.open_gtif(filename, regions[0])
#    data = np.moveaxis(data, 0, 2)
#    for ax in grid:
#        ax.imshow(data, extent=extent, transform=utm)

    # open Yvo's digital elevation model
    filename = 'data/bowdoin_20100904_15m_20140929.tif'
    data, extent = ut.io.open_gtif(filename, regions[0])
    levs = np.arange(0.0, 800.0, 10.0)

    # compute shaded relief
    rows, cols = data.shape
    dx = (extent[1]-extent[0])/cols
    dy = (extent[2]-extent[3])/rows
    shades = ut.pl.shading(data, dx, dy)

    # plot shades and contours
    for ax in grid:
        ax.imshow(shades, extent=extent, cmap='Greys', vmin=0.0, vmax=1.0)
        cs = ax.contour(data, levels=levs[(levs % 100 != 0)], extent=extent,
                        colors='k', linewidths=0.25)
        cs = ax.contour(data, levels=levs[(levs % 100 == 0)], extent=extent,
                        colors='k', linewidths=0.5)
        cs.clabel(fmt='%d')

    # plot Sentinel hill sample locations
    names = ['BOW16-MF-BED%d' % i for i in range(1, 4)]
    names += ['BOW16-MF-BOU%d' % i for i in range(1, 4)]
    textloc = ['ul', 'lr', 'll', 'll', 'cr', 'ur']
    ut.pl.waypoint_scatter(names, ax=grid[1], textloc=textloc,
                           c=ut.palette['darkred'])

    # plot Bartlett hill sample locations
    names = ['BOW15-%02d' % i for i in range(1, 10)]
    names += ['BOW16-JS-%02d' % i for i in (12, 13)]
    textloc = ['ur', 'cr', 'cl', 'ur', 'ul', 'cr', 'lr', 'll', 'cl',
               'cl', 'ul']
    ut.pl.waypoint_scatter(names, ax=grid[2], textloc=textloc,
                           c=ut.palette['darkred'])

    # plot Camp carbon sample locations
    names = ['BOW16-CA-%02d' % i for i in range(2, 5)]
    textloc = ['lr', 'cr', 'ur']
    ut.pl.waypoint_scatter(names, ax=grid[3], textloc=textloc, c='w')

    # plot Upper cam hill sample locations
    names = ['BOW16-JS-%02d' % i for i in range(1, 7)]
    textloc = ['cr', 'cl', 'll', 'ul', 'ur', 'lr']
    ut.pl.waypoint_scatter(names, ax=grid[3], textloc=textloc,
                           c=ut.palette['darkred'])

    # plot Eastarm moraine sample locations
    names = ['BOW16-JS-%02d' % i for i in range(7, 12)]
    textloc = ['cl', 'lr', 'll', 'ul', 'ur']
    ut.pl.waypoint_scatter(names, ax=grid[4], textloc=textloc,
                           c=ut.palette['darkred'])

    # save
    fig.savefig('samplemap')
