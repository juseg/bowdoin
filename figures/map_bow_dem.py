#!/usr/bin/env python2

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import gpxpy

if __name__ == '__main__':

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    proj = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                              true_scale_latitude=70.0)

    # subregion w, e, s, n
    extent = (-580e3, -500e3, -1250e3, -1200e3)  # Qaanaaq peninsula
    extent = (-545e3, -525e3, -1235e3, -1220e3)  # lower Bowdoin Glacier
    extent = (-540e3, -531e3, -1231e3, -1225e3)  # boreholes

    # initialize figure
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], projection=proj)
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(extent, crs=proj)

    # read velocity data
    filename = ('data/external/gimpdem0_4.tif')
    z, extent = ut.ma.open_gtif(filename, extent)

    # plot shadows
    (w, e, s, n) = extent
    rows, cols = z.shape
    dx = (e-w) / cols
    dy = (s-n) / rows
    s = ut.ma.shading(z, dx=dx, dy=dy)
    ax.imshow(s, extent=extent, cmap='Greys', vmin=0.0, vmax=1.0)

    # plot contours
    levs = np.arange(0.0, 1500.0, 20.0)
    cs = ax.contour(z, levels=levs[(levs % 100 != 0)], extent=extent,
                    colors='k', linewidths=0.1)
    cs = ax.contour(z, levels=levs[(levs % 100 == 0)], extent=extent,
                    colors='k', linewidths=0.25)
    cs.clabel(fmt='%d')

    # plot slope map
    #s = ut.ma.slope(z, dx=dx, dy=dy, smoothing=10)
    #im = ax.imshow(s, extent=extent, vmin=0.0, vmax=0.05, cmap='magma_r')
    #fig.colorbar(im)

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

    # save third frame
    fig.savefig('map_bow_dem')

