#!/usr/bin/env python2

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import gpxpy

if __name__ == '__main__':

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    utm = ccrs.UTM(19)
    ste = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                             true_scale_latitude=70.0)
    extent = 505e3, 513.5e3, 8619.5e3, 8625.5e3

    # initialize figure
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], projection=utm)
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(extent, crs=utm)

    # read velocity data
    filename = ('../data/external/gimpdem0_4.tif')
    filename = '../data/external/bowdoin_20100904_15m_20140929.tif'
    z, extent = ut.io.open_gtif(filename, extent)

    # plot shadows
    s = ut.pl.shading(z, extent=extent)
    ax.imshow(s, extent=extent, cmap='Greys', vmin=0.0, vmax=1.0)

    # plot contours
    levs = np.arange(0.0, 800.0, 20.0)
    cs = ax.contour(z, levels=levs[(levs % 100 != 0)], extent=extent,
                    colors='k', linewidths=0.1)
    cs = ax.contour(z, levels=levs[(levs % 100 == 0)], extent=extent,
                    colors='k', linewidths=0.25)
    cs.clabel(fmt='%d')

    # plot slope map
    #s = ut.pl.slope(z, extent=extent, smoothing=10)
    #im = ax.imshow(s, extent=extent, vmin=0.0, vmax=0.05, cmap='magma_r')
    #fig.colorbar(im)

    # plot borehole and camera locations
    kwa = dict(color=ut.colors['upstream'], marker='o')
    ut.pl.add_waypoint('B14BH1', **kwa)
    ut.pl.add_waypoint('B16BH1', **kwa)
    kwa = dict(color=ut.colors['downstream'], marker='o')
    ut.pl.add_waypoint('B14BH3', text='2014', **kwa)
    ut.pl.add_waypoint('B16BH3', text='2016', **kwa)
    kwa = dict(color=ut.palette['darkorange'], marker='^')
    ut.pl.add_waypoint('Camera Upper', **kwa)
    ut.pl.add_waypoint('Camera Lower', **kwa)

    # save third frame
    ut.pl.savefig(fig)

