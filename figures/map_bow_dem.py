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

    # calculate extent in data projection
    w, e, s, n = extent
    x_utm = np.array((w, w, e, e))
    y_utm = np.array((s, n, s, n))
    x_ste, y_ste = ste.transform_points(utm, x_utm, y_utm).T[:2]
    extent_ste = [x_ste.min(), x_ste.max(), y_ste.min(), y_ste.max()]

    # read velocity data
    filename = ('data/external/gimpdem0_4.tif')
    z, extent = ut.ma.open_gtif(filename, extent_ste)

    # plot shadows
    (w, e, s, n) = extent
    rows, cols = z.shape
    dx = (e-w) / cols
    dy = (s-n) / rows
    s = ut.ma.shading(z, dx=dx, dy=dy)
    ax.imshow(s, extent=extent, cmap='Greys', vmin=0.0, vmax=1.0, transform=ste)

    # plot contours
    levs = np.arange(0.0, 1500.0, 20.0)
    cs = ax.contour(z, levels=levs[(levs % 100 != 0)], extent=extent,
                    colors='k', linewidths=0.1, transform=ste)
    cs = ax.contour(z, levels=levs[(levs % 100 == 0)], extent=extent,
                    colors='k', linewidths=0.25, transform=ste)
    cs.clabel(fmt='%d')

    # plot slope map
    #s = ut.ma.slope(z, dx=dx, dy=dy, smoothing=10)
    #im = ax.imshow(s, extent=extent, vmin=0.0, vmax=0.05, cmap='magma_r')
    #fig.colorbar(im)

    # plot borehole and camera locations
    kwa = dict(color=ut.colors['upstream'], marker='o')
    ut.ma.add_waypoint('B14BH1', **kwa)
    ut.ma.add_waypoint('B16BH1', **kwa)
    kwa = dict(color=ut.colors['downstream'], marker='o')
    ut.ma.add_waypoint('B14BH3', text='2014', **kwa)
    ut.ma.add_waypoint('B16BH3', text='2016', **kwa)
    kwa = dict(color=ut.palette['darkorange'], marker='^')
    ut.ma.add_waypoint('Camera Upper', **kwa)
    ut.ma.add_waypoint('Camera Lower', **kwa)

    # save third frame
    fig.savefig('map_bow_dem')

