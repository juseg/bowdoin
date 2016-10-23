#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import util as ut
import gpxpy

#from mpl_toolkits.axes_grid1.inset_locator import mark_inset

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
        ax.outline_patch.set_edgecolor('k')

#    # mark inset locations
#    kwa = dict(fc='none', ec='k', lw=1.0, alpha=0.75)
#    mark_inset(grid[0], grid[1], loc1='none', loc2='none', **kwa)
#    mark_inset(grid[0], grid[2], loc1=1, loc2=3, **kwa)
#    mark_inset(grid[0], grid[3], loc1=2, loc2=3, **kwa)
#    mark_inset(grid[0], grid[4], loc1=2, loc2=4, **kwa)

    # add subfigure labels
    for reg, label in zip(regions[1:], list('bcde')):
        w, e, s, n = reg
        rect = plt.Rectangle((w, n), (e-w), (s-n), fc='none')
        grid[0].add_patch(rect)
        grid[0].text(w, n+100, '(%s)' % label, fontweight='bold')
    ut.pl.add_subfig_label('(a) Bowdoin Glacier', ax=grid[0])
    ut.pl.add_subfig_label('(b) Sentinel hill', ax=grid[1])
    ut.pl.add_subfig_label('(c) Bartlett hill', ax=grid[2])
    ut.pl.add_subfig_label('(d) Upper cam. hill', ax=grid[3])
    ut.pl.add_subfig_label('(e) East Branch moraine', ax=grid[4])

    # plot S2A image
    filename = 'data/S2A_20160410_180125_659_RGB.jpg'
    data, extent = ut.io.open_gtif(filename, regions[0])
    data = np.moveaxis(data, 0, 2)
    for ax in grid:
        ax.imshow(data, extent=extent, transform=utm)

    # open Yvo's digital elevation model
    filename = 'data/bowdoin_20100904_15m_20140929.tif'
    data, extent = ut.io.open_gtif(filename, regions[0])
    levs = np.arange(0.0, 800.0, 20.0)

    # plot contours
    for ax in grid:
        cs = ax.contour(data, levels=levs[(levs % 100 != 0)], extent=extent,
                        colors='k', linewidths=0.1, alpha=0.75)
        cs = ax.contour(data, levels=levs[(levs % 100 == 0)], extent=extent,
                        colors='k', linewidths=0.25, alpha=0.75)
        cs.clabel(fmt='%d')

    # plot all sample locations on main panel
    comkwa = dict(s=40, alpha=0.5)
    bedkwa = dict(marker='s', c=ut.palette['darkblue'], **comkwa)
    boukwa = dict(marker='o', c=ut.palette['darkred'], **comkwa)
    carkwa = dict(marker='^', c='w', **comkwa)
    ut.pl.waypoint_scatter(['BOW16-JS-%02d' % i for i in range(1, 4)] +
                           ['BOW16-MF-BED%d' % i for i in range(1, 4)],
                           ax=grid[0], text=False, **bedkwa)
    ut.pl.waypoint_scatter(['BOW15-%02d' % i for i in range(1, 10)] +
                           ['BOW16-JS-%02d' % i for i in range(4, 14)] +
                           ['BOW16-MF-BOU%d' % i for i in range(1, 4)],
                           ax=grid[0], text=False, **boukwa)
    ut.pl.waypoint_scatter(['BOW16-CA-%02d' % i for i in range(2, 5)],
                           ax=grid[0], text=False, **carkwa)

    # plot Sentinel hill sample locations
    ut.pl.waypoint_scatter(['BOW16-MF-BED%d' % i for i in range(1, 4)],
                           textloc=['ul', 'lr', 'll'],
                           ax=grid[1], **bedkwa)
    ut.pl.waypoint_scatter(['BOW16-MF-BOU%d' % i for i in range(1, 4)],
                           textloc=['ll', 'cr', 'ur'],
                           ax=grid[1], **boukwa)

    # plot Bartlett hill sample locations
    ut.pl.waypoint_scatter(['BOW15-%02d' % i for i in range(1, 10)] +
                           ['BOW16-JS-%02d' % i for i in (12, 13)],
                           textloc=['ur', 'cr', 'cl', 'ur', 'ul', 'cr', 'lr',
                                    'll', 'cl', 'cl', 'ul'],
                           ax=grid[2], **boukwa)

    # plot Camp carbon sample locations
    ut.pl.waypoint_scatter(['BOW16-CA-%02d' % i for i in range(2, 5)],
                           textloc=['lr', 'cr', 'ur'],
                           ax=grid[3], **carkwa)

    # plot Upper cam hill sample locations
    ut.pl.waypoint_scatter(['BOW16-JS-%02d' % i for i in range(1, 4)],
                           textloc=['cr', 'cl', 'll'],
                           ax=grid[3], **bedkwa)
    ut.pl.waypoint_scatter(['BOW16-JS-%02d' % i for i in range(4, 7)],
                           textloc=['ul', 'ur', 'lr'],
                           ax=grid[3], **boukwa)

    # plot East Branch moraine sample locations
    ut.pl.waypoint_scatter(['BOW16-JS-%02d' % i for i in range(7, 12)],
                           textloc=['cr', 'lr', 'll', 'ul', 'ur'],
                           ax=grid[4], **boukwa)

    # save
    fig.savefig('samplemap')
