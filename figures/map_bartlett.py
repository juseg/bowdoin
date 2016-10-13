#!/usr/bin/env python2

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


if __name__ == "__main__":

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    proj = ccrs.UTM(19)
    w, e, s, n = 509e3, 513e3, 8619e3, 8622e3  # just around the samples

    # extend map boundaries
    f = 1.0  # zoom-out factor
    w = (1+f)*w/2 + (1-f)*e/2
    e = (1+f)*e/2 + (1-f)*w/2
    s = (1+f)*s/2 + (1-f)*n/2
    n = (1+f)*n/2 + (1-f)*s/2

    # initialize figure
    figw, figh = 297.0, 210.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_subplot('111', projection=proj)
    fig.subplots_adjust(left=10.0/figw, right=1-10.0/figw,
                        bottom=10.0/figh, top=1-10.0/figh)
    ax.set_extent([w, e, s, n], crs=proj)
    ax.set_rasterization_zorder(2.5)

    # open Yvo's digital elevation model
    data, extent = ut.io.open_gtif('data/bowdoin_20100904_15m_20140929.tif',
                                   (w, e, s, n))

    # plot shadows
    rows, cols = data.shape
    dx = (extent[1]-extent[0])/cols
    dy = (extent[2]-extent[3])/rows
    ax.imshow(ut.pl.shading(data, dx, dy), extent=extent,
              cmap='Greys', vmin=0.0, vmax=1.0)

    # plot contours
    levs = np.arange(0.0, 800.0, 10.0)
    cs = ax.contour(data, levels=levs[(levs % 100 != 0)], extent=extent,
                    colors='k', linewidths=0.25)
    cs = ax.contour(data, levels=levs[(levs % 100 == 0)], extent=extent,
                    colors='k', linewidths=0.5)
    cs.clabel(fmt='%d')

    # plot sample locations
    names = ['BOW15-%02d' % i for i in range(1, 10)]
    textloc = ['ul', 'lr', 'ul', 'lr', 'ul', 'lr', 'lr', 'll', 'ul']
    ut.pl.waypoint_scatter(names, textloc=textloc, c='red')


# save
plt.savefig('map_bartlett')
