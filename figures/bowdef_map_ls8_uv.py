#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import netCDF4 as nc4
import util as ut
import gpxpy

if __name__ == '__main__':

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    utm = ccrs.UTM(19)
    extent = 465e3, 525e3, 8655e3, 8595e3
    extent = 500e3, 520e3, 8640e3, 8620e3


    # initialize figure
    figw, figh = 60.0, 60.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_axes([0, 0, 1, 1], projection=utm)
    cax = fig.add_axes([5.0/figw, 35.0/figh, 2.5/figw, 20.0/figh])
    frame = plt.Rectangle((2.5/figw, 32.5/figh), 15.0/figw, 25.0/figh,
                          ec='k', fc='w', transform=ax.transAxes)
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(extent, crs=utm)

    # plot image data
    filename = '../data/native/S2A_20160808_175915_456_RGB.jpg'
    data, extent = ut.io.open_gtif(filename)
    data = np.moveaxis(data, 0, 2)
    ax.imshow(data, extent=extent, transform=utm, cmap='Blues')

    # plot image data
    basename = '16072015_17082015_161111_1117_f'
    upath = '../data/satellite/bowdoin-landsat-uv/%s_u.nc' % basename
    vpath = '../data/satellite/bowdoin-landsat-uv/%s_v.nc' % basename
    unc = nc4.Dataset(upath)
    vnc = nc4.Dataset(vpath)
    x = unc['x'][:]
    y = unc['y'][:]
    u = unc['z'][:]
    v = vnc['z'][:]
    unc.close()
    vnc.close()
    c = (u**2+v**2)**0.5
    levs = range(0, 451, 50)
    cs = ax.contourf(x, y, c, levels=levs, extent=extent, transform=utm,
                     vmin=0.0, vmax=450.0, cmap='Reds', alpha=0.75)

    # add colorbar
    ax.add_patch(frame)
    cb = fig.colorbar(cs, cax)
    cb.set_label('ice velocity (m a$^{-1}$)', labelpad=2)

    # save
    ut.pl.savefig(fig)
