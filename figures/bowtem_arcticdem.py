#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature Arctic DEM map and profile."""

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import absplots as apl
import cartowik.decorations as cde
import util


def init_figure():
    """Initialize figure with map and profile subplots."""

    # initialize figure
    fig = apl.figure_mm(figsize=(150, 75))
    ax0 = fig.add_axes_mm([2.5, 2.5, 60, 70], projection=ccrs.Stereographic(
        central_latitude=90, central_longitude=-45, true_scale_latitude=70))
    ax1 = fig.add_axes_mm([75, 10, 72.5, 62.5])

    # add subfigure labels
    util.com.add_subfig_label(ax=ax0, text='(a)')
    util.com.add_subfig_label(ax=ax1, text='(b)')

    # prepare axes
    ax0.set_rasterization_zorder(2.5)

    # return figure and axes
    return fig, (ax0, ax1)


def project_borehole_locations(date, crs):
    """
    Estimate borehole locations for a given date based their initial positions
    measured by hand-held GPS and the continuous D-GPS record at BH1.
    """

    # read initial positions from GPX file
    locs = util.com.read_locations(crs=crs)
    locs = locs[locs.index.str.startswith('B14')]
    locs.index = locs.index.str[3:].str.lower()
    initial = locs[['x', 'y']]

    # interpolate DEM date BH1 location from continuous GPS
    lonlat = ccrs.PlateCarree()
    gps = util.tem.load('../data/processed/bowdoin.bh1.gps.csv')
    gps = gps.interpolate().loc[date]
    gps['x'], gps['y'] = crs.transform_point(gps.lon, gps.lat, lonlat)
    gps = gps[['x', 'y']]

    # compute DEM date positions from BH1 displacement with time mutliplier
    displacement = gps - initial.loc['bh1']
    date = pd.to_datetime(date)
    multiplier = (date-locs.time.bh1) / (date-locs.time)
    displacement = displacement.apply(lambda x: x*multiplier).T
    projected = initial + displacement

    # return initial and projected locations
    return initial, projected


def build_profile_coords(points, interval=None, method='linear'):
    """Interpolate coordinates along profile through given points."""

    # compute distance along profile
    x, y = np.asarray(points).T
    dist = ((np.diff(x)**2+np.diff(y)**2)**0.5).cumsum()
    dist = np.insert(dist, 0, 0)

    # build coordinate xarrays
    x = xr.DataArray(x, coords=[dist], dims='d')
    y = xr.DataArray(y, coords=[dist], dims='d')

    # if interval was given, interpolate coordinates
    if interval is not None:
        dist = np.arange(0, dist[-1], interval)
        x = x.interp(d=dist, method=method)
        y = y.interp(d=dist, method=method)

    # return coordinates
    return x, y


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax0, ax1) = init_figure()

    # Arctic DEM strip and sensing date
    demstrip = 'SETSM_WV01_20140906_10200100318E9F00_1020010033454500_seg4_2m'
    filename = '../data/external/' + demstrip + '_v3.0.tif'
    sensdate = '2014-09-06 17:30:00'

    # plot elevation map (UTM 19 extent 510400, 510700, 8623700, 8624050)
    data = xr.open_rasterio(filename).squeeze(drop=True)
    data = data.loc[-1226500:-1227200, -535200:-534600]  # 700x600 m
    data = data.loc[-1226700:-1227050, -535075:-534775]  # 350x300 m
    data.plot.imshow(ax=ax0, add_colorbar=False, cmap='Blues_r')

    # contour code too slow for full dem
    data.plot.contour(ax=ax0, colors='0.25', levels=range(70, 100),
                      linewidths=0.1)
    data.plot.contour(ax=ax0, colors='0.25', levels=range(70, 100, 5),
                      linewidths=0.25).clabel(fmt='%d')

    # plot borehole locations on the map
    initial, projected = project_borehole_locations(sensdate, ax0.projection)
    for bh in ('bh1', 'bh2', 'bh3'):
        color = util.tem.COLOURS[bh]
        ax0.plot(*initial.loc[bh], color='0.25', marker='+')
        ax0.plot(*initial.loc[bh], color='0.25', marker='+')
        ax0.plot(*projected.loc[bh], color=color, marker='+')
        ax0.text(*projected.loc[bh]+np.array([10, 0]), s=bh.upper(),
                 color=color, ha='left', va='center', fontweight='bold')

        # add arrows and uncertainty circles
        if bh != 'bh1':
            ax0.annotate('', xy=projected.loc[bh], xytext=initial.loc[bh],
                         arrowprops=dict(arrowstyle='->', color=color))
            ax0.add_patch(plt.Circle(projected.loc[bh], radius=10.0, fc='w',
                                     ec=color, alpha=0.5))

    # add scale
    cde.add_scale_bar(ax=ax0, color='k', label='100 m', length=100)

    # plot Arctic DEM topographic profile
    points = [2*projected.loc['bh3']-projected.loc['bh1'],
              2*projected.loc['bh1']-projected.loc['bh3']]
    x, y = build_profile_coords(points, interval=1)
    data.interp(x=x, y=y, method='linear').plot(ax=ax1, color='0.25')

    # mark borehole locations along profile
    for bh in ('bh1', 'bh3'):
        color = util.tem.COLOURS[bh]
        dist = ((projected.loc[bh]-points[0])**2).sum()**0.5
        ax1.axvline(dist, color=color)
        ax1.text(dist, 76, ' '+bh.upper()+' ', color=color, fontweight='bold')

    # set axes properties
    ax1.set_xlabel('distance along profile (m)')
    ax1.set_ylabel('surface elevation (m)')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
