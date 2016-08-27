#!/usr/bin/env python2

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

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
    ax = fig.add_subplot(111, projection=proj)
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

    # plot locations of camera and boreholes
    llz = {'qaanaaq':   (-69.230556, 77.466667,   0.000000),
           'cam_lower': (-68.527481, 77.659782, 490.219243),
           'cam_upper': (-68.504852, 77.691702, 289.044237),
           'gcp_m1':    (-68.504733, 77.688107, 139.879200),
           'gcp_m2':    (-68.628121, 77.721004, 172.288962),
           'gcp_m3':    (-68.643724, 77.703824, 172.562631),
           'bh1':       (-68.555749, 77.691244,  88.694913),  # upstream
           'bh2':       (-68.555685, 77.691307,  87.746263),  # upstream
           'bh3':       (-68.558857, 77.689995,  83.446628),  # downstream
           'camp':      (-68.509920, 77.685890,  70.000000)}
    ax.plot(*llz['bh1'][:2], c=ut.colors['upstream'], marker='o', ms=6, transform=ll)
    ax.plot(*llz['bh3'][:2], c=ut.colors['downstream'], marker='o', ms=6, transform=ll)
    ax.plot(*llz['cam_upper'][:2], c=ut.palette['darkorange'], marker='^', ms=6,
            transform=ll)
    ax.plot(*llz['cam_lower'][:2], c=ut.palette['darkorange'], marker='^', ms=6,
            transform=ll)

    # save third frame
    fig.savefig('map_bow')

