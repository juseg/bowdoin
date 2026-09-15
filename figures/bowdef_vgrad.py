#!/usr/bin/env python
# Copyright (c) 2016-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin velocity gradient from Landsat images."""


import numpy as np
import matplotlib.pyplot as plt
# import cartopy.crs as ccrs
import bowdef_utils
# import gpxpy
import xarray as xr

from bowtem_utils import COLOURS, annotate_location


# from bowtem_utils
def plot_bowdoin_map(ax, boreholes=None, colors=None, season='spring'):
    """Draw boreholes location map with Sentinel image background."""

    # default boreholes and colors
    boreholes = boreholes or list(COLOURS.keys())[:-1]
    colors = colors or list(COLOURS.values())[:-1]

    # select default color and seasonal image
    color, image = {
        'summer': ('w', '20160808_175915_456_S2A_RGB'),
        'spring': ('k', '20170310_174129_456_S2A_RGB')}[season]

    # plot Sentinel image data
    img = xr.open_dataarray(f'../data/native/{image}.jpg').astype(int)
    img.plot.imshow(add_labels=False, ax=ax, interpolation='bilinear')

    # add camp and boreholes locations
    crs = '+proj=utm +zone=19'
    annotate_location(
        'Tent Swiss', ax=ax, color=color, crs=crs,
        point='s', marker='^',
        text='Camp')
    for bh, c in zip(boreholes, colors):
        for year in (14, 16, 17):
            annotate_location(
                f'B{year}{bh.upper()}', ax=ax, color=c, crs=crs,
                text=f'20{year}', point='se' if bh == 'bh1' else 'nw')

    # set axes properties
    ax.set_xlim(508e3, 512e3)
    ax.set_ylim(8621e3, 8626e3+2e3/3)
    ax.set_xticks([])
    ax.set_yticks([])

    # add scale bar
    img.to_dataset().hyoga.plot.scale_bar(ax=ax, color=color)


def main():
    """Main program called during execution."""

    # projections and map boundaries
    # ll = ccrs.PlateCarree()
    # utm = ccrs.UTM(19)
    # extent = 465e3, 525e3, 8655e3, 8595e3
    # extent = 500e3, 520e3, 8640e3, 8620e3

    # initialize figure
    # figw, figh = 60.0, 60.0
    fig = plt.figure(figsize=(60/25.4, 60/25.4))
    ax = fig.add_axes([0, 0, 1, 1])  #, projection=utm)
    # cax = fig.add_axes([5.0/figw, 35.0/figh, 2.5/figw, 20.0/figh])
    # frame = plt.Rectangle((2.5/figw, 32.5/figh), 15.0/figw, 25.0/figh,
    #                       ec='k', fc='w', transform=ax.transAxes)
    # ax.set_rasterization_zorder(2.5)
    # ax.set_extent(extent, crs=utm)

    plot_bowdoin_map(
        fig.axes[0], boreholes=['bh1', 'bh3'],
        colors=['tab:blue', 'tab:pink'], season='summer')

    # plot image data
    # filename = '../data/native/S2A_20160808_175915_456_RGB.jpg'
    # data, extent = bowdef_utils.open_gtif(filename)
    # data = np.moveaxis(data, 0, 2)
    # ax.imshow(data, extent=extent, transform=utm, cmap='Blues')

    # plot velocity gradient
    filename = '../data/satellite/bowdoin-landsat/16072015_17082015.tif'
    # data, extent = bowdef_utils.open_gtif(filename)
    # data = np.ma.masked_equal(data, 65535).astype(np.float)
    # grad = bowdef_utils.slope(data, extent=extent)
    # cs = ax.imshow(grad, extent=extent, cmap='Reds', vmin=0.0, vmax=0.5, alpha=0.75)
    img = xr.open_dataarray(filename).squeeze()
    img = img.where(img!=65535)
    # img = (img.differentiate('x')**2 + img.differentiate('y')**2)**0.5

    # img.plot.imshow(ax=ax, add_labels=False, alpha=0.75, cmap='Reds')  #, interpolation='bilinear')
    img.plot.contour(ax=ax, add_labels=False, alpha=0.75, cmap='Reds')

    # add colorbar
    # ax.add_patch(frame)
    # cb = fig.colorbar(cs, cax)
    # cb.set_label('velocity gradient (a$^{-1}$)', labelpad=2)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
