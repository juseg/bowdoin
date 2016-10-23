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

    # read velocity data
    filename = 'data/external/greenland_vel_mosaic250_v1.tif'

    # initialize figure
    figw, figh = 85.0, 75.0
    fig = plt.figure(0, (figw/25.4, figh/25.4))
    cax = fig.add_axes([75.0/figw, 50.0/figh, 2.5/figw, 22.5/figh])
    grid = [fig.add_axes(rect, projection=proj) for rect in [
                [02.50/figw, 02.50/figh, 38.75/figw, 70.00/figh],
                [43.75/figw, 43.75/figh, 28.75/figw, 28.75/figh],
                [43.75/figw, 02.50/figh, 38.75/figw, 38.75/figh]]]

    # subregions w, e, s, n
    regions = [
        (-650e3, +900e3, -3400e3, -0600e3),  # Grl. 1550x2800 (38.75*40x70*40)
        (-650e3, -450e3, -1325e3, -1125e3),  # Inglefield 200x200
        (-547e3, -517e3, -1237e3, -1207e3)]  # Bowdoin 30x30

    # mark inset locations
    mark_inset(grid[0], grid[1], loc1=2, loc2=3, fc='none', ec='k', lw=0.5)
    mark_inset(grid[1], grid[2], loc1=1, loc2=2, fc='none', ec='k', lw=0.5)

    # plot
    norm = LogNorm(1e0, 1e4)
    for ax, reg in zip(grid, regions):
        ax.set_rasterization_zorder(2.5)
        ax.set_extent(reg, crs=ax.projection)
        data, extent = ut.ma.open_gtif(filename, extent=reg)
        im = ax.imshow(data, extent=extent, cmap='Blues', norm=norm)

    # add coastlines
    grid[0].coastlines(resolution='50m', lw=0.5)
    grid[1].coastlines(resolution='10m', lw=0.5)
    grid[2].contour(data, extent=extent, levels=[-1e9], colors='k',
                    linestyles='-', linewidths=0.5)

    # add colorbar
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r'surface velocity ($m\,a^{-1}$)', labelpad=-2)

    # plot Qaanaaq location
    c = 'k'
    ax = grid[1]
    kwa = dict(ha='center', fontweight='bold')
    ut.ma.add_waypoint('Qaanaaq', ax=ax, color=c)
    ax.text(-605000, -1250000, 'Qaanaaq', color=c, **kwa)

    # plot borehole locations
    c = ut.colors['upstream']
    ax = grid[2]
    ut.ma.add_waypoint('B14BH3', ax=ax, color=c)
    ut.ma.add_waypoint('B16BH3', ax=ax, color=c)
    ax.text(-535000, -1225500, 'boreholes', color=c, **kwa)

    # plot camp locations
    c = ut.palette['darkgreen']
    ut.ma.add_waypoint('Tent Swiss', ax=ax, color=c, marker='^')
    ax.text(-530000, -1230000, 'camp', color=c, **kwa)

    # add scale
    grid[2].plot([-525e3, -520e3], [-1235e3, -1235e3], 'k-|', mew=1.0)
    grid[2].text(-522.5e3, -1234e3, '5km', ha='center')

    # save third frame
    fig.savefig('map_grl_vel')
