#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import gpxpy

import util as ut


if __name__ == '__main__':

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    utm = ccrs.UTM(19)
    proj = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                              true_scale_latitude=70.0)

    # subregions w, e, s, n
    grld = (-650e3, +900e3, -0600e3, -3400e3)  # 1550x2800 (38.75*40x70*40)
    qaaq = (-650e3, -450e3, -1325e3, -1125e3)  # 200x200
    bowd = (-547e3, -517e3, -1237e3, -1207e3)  # 30x30
    jako = (-300e3, +000e3, -2350e3, -2050e3)  # 300x300

    # read velocity data
    data, extent = ut.ma.open_gtif('data/external/greenland_vel_mosaic250_v1.tif')

    # initialize figure
    figw, figh = 85.0, 75.0
    fig = plt.figure(0, (figw/25.4, figh/25.4))
    rect1 = [2.5/figw, 2.5/figh, 38.75/figw, 70.0/figh]
    rect2 = [43.75/figw, 43.75/figh, 28.75/figw, 28.75/figh]
    rect3 = [43.75/figw, 2.5/figh, 38.75/figw, 38.75/figh]
    ax1 = fig.add_axes(rect1, projection=proj)
    ax2 = fig.add_axes(rect2, projection=proj)
    ax3 = fig.add_axes(rect3, projection=proj)
    cax = plt.axes([75.0/figw, 43.75/figh, 2.5/figw, 28.75/figh])

    # set rasterization levels
    ax1.set_rasterization_zorder(2.5)
    ax2.set_rasterization_zorder(2.5)
    ax3.set_rasterization_zorder(2.5)

    # set map extents
    ax1.set_extent(grld, crs=proj)
    ax2.set_extent(qaaq, crs=proj)
    ax3.set_extent(bowd, crs=proj)

    # mark inset locations
    mark_inset(ax1, ax2, loc1=2, loc2=3, fc='none', ec='k', lw=0.5)
    mark_inset(ax2, ax3, loc1=1, loc2=2, fc='none', ec='k', lw=0.5)

    # plot ax1 velocity map
    norm = LogNorm(1e0, 1e4)
    im = ax1.imshow(data, extent=extent, cmap='Blues', norm=norm)
    cl = ax1.coastlines(resolution='50m', lw=0.5)

    # plot ax2 velocity map
    im = ax2.imshow(data, extent=extent, cmap='Blues', norm=norm)
    cl = ax2.coastlines(resolution='10m', lw=0.5)

    # plot ax3 velocity map
    im = ax3.imshow(data, extent=extent, cmap='Blues', norm=norm)
    cl = ax3.coastlines(resolution='10m', lw=0.5)

    # add colorbar
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r'surface velocity ($m\,a^{-1}$)', labelpad=0.0)

    # plot ax3 satellite image
    # FIXME: this works only with an internet connection. Replace by
    # a locally-stored satellite image.
    #background = cimgt.MapQuestOpenAerial()
    #ax3.add_image(background, 10)

    # plot Qaanaaq, borehole and camera locations
    ut.ma.annotate('Qaanaaq', ax=ax2, color='k', marker='o')
    kwa = dict(ax=ax3, color=ut.colors['upstream'], marker='o')
    ut.ma.annotate('B14BH1', **kwa)
    ut.ma.annotate('B16BH1', **kwa)
    kwa = dict(ax=ax3, color=ut.colors['downstream'], marker='o')
    ut.ma.annotate('B14BH3', **kwa)
    ut.ma.annotate('B16BH3', **kwa)
    kwa = dict(ax=ax3, color=ut.palette['darkorange'], marker='^')
    ut.ma.annotate('Camera Upper', **kwa)
    ut.ma.annotate('Camera Lower', **kwa)

    # annotate
    ax2.text(-590000, -1250000, 'Qaanaaq', color='k',
             ha='center', fontweight='bold')
    ax3.text(-532500, -1225500, 'boreholes', color=ut.palette['darkblue'],
             ha='center', fontweight='bold')
    ax3.text(-540000, -1229000, 'seismometers', color=ut.palette['darkred'],
             ha='center', fontweight='bold')
    ax3.text(-532000, -1229500, 'cameras', color=ut.palette['darkorange'],
             ha='center', fontweight='bold')

    # add scale
    ax3.plot([-525e3, -520e3], [-1235e3, -1235e3], 'k-|', mew=1.0)
    ax3.text(-522.5e3, -1234e3, '5km', ha='center')

    # save third frame
    fig.savefig('map_grl_vel')
