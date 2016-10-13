#!/usr/bin/env python2

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


if __name__ == "__main__":

    # projections and map boundaries
    proj = ccrs.UTM(19)
    extent = 505e3, 507e3, 8620.8e3, 8622.3e3

    # initialize figure
    fig = plt.figure(figsize=(160.0/25.4, 120.0/25.4))
    ax = fig.add_axes([0, 0, 1, 1], projection=proj)
    ax.set_extent(extent, crs=proj)
    ax.set_rasterization_zorder(2.5)

    # open Yvo's digital elevation model
    filename = 'data/bowdoin_20100904_15m_20140929.tif'
    data, extent = ut.io.open_gtif(filename, extent)

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
    names = ['BOW16-MF-BED%d' % i for i in range(1, 4)]
    names += ['BOW16-MF-BOU%d' % i for i in range(1, 4)]
    textloc = ['ul', 'lr', 'll', 'll', 'lr', 'ur']
    ut.pl.waypoint_scatter(names, textloc=textloc, c='red')

# save
plt.savefig('map_sentinel')
