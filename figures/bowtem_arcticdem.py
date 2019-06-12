#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature Arctic DEM map and profile."""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import gpxpy
import absplots as apl
import cartowik.decorations as cde
import util


def project_borehole_locations(date, crs):
    """
    Estimate borehole locations for a given date based their initial positions
    measured by hand-held GPS and the continuous D-GPS record at BH1.
    """
    # FIXME: account for different dates in bh1 and bh3 waypoints

    # read initial positions from GPX file
    lonlat = ccrs.PlateCarree()
    with open('../data/locations.gpx', 'r') as gpx_file:
        initial = {wpt.name[3:].lower():
                   crs.transform_point(wpt.longitude, wpt.latitude, lonlat)
                   for wpt in gpxpy.parse(gpx_file).waypoints
                   if wpt.name.startswith('B14')}

    # interpolate DEM date BH1 location from continuous GPS
    gps = util.tem.load('../data/processed/bowdoin.bh1.gps.csv')
    gps = gps.interpolate().loc[date]
    gps = crs.transform_point(gps['lon'], gps['lat'], lonlat)

    # compute DEM date positions from BH1 displacement
    displacement = np.array(gps) - initial['bh1']
    projected = {bh: pos + displacement for bh, pos in initial.items()}

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
    fig = apl.figure_mm(figsize=(150, 75))
    ax0 = fig.add_axes_mm([2.5, 2.5, 60, 70], projection=ccrs.Stereographic(
        central_latitude=90, central_longitude=-45, true_scale_latitude=70))
    ax1 = fig.add_axes_mm([75, 10, 72.5, 62.5])

    # add subfigure labels
    util.com.add_subfig_label(ax=ax0, text='(a)')
    util.com.add_subfig_label(ax=ax1, text='(b)')

    # prepare axes
    ax0.set_rasterization_zorder(2.5)

    # Arctic DEM strip and sensing date
    demstrip = 'SETSM_WV01_20140906_10200100318E9F00_1020010033454500_seg4_2m'
    filename = '../data/external/' + demstrip + '_v3.0.tif'
    sensdate = '2014-09-06 17:30:00'

    # plot elevation map (UTM 19 extent 510400, 510700, 8623700, 8624050)
    data = xr.open_rasterio(filename).squeeze(drop=True)
    data = data.loc[-1226500:-1227200, -535200:-534600]  # 700x600 m
    data = data.loc[-1226700:-1227050, -535075:-534775]  # 350x300 m
    data.plot.imshow(ax=ax0, add_colorbar=False, cmap='Blues_r')

    # FIXME: Implement windowed plotting in Cartowik.
    # FIXME: Implement contour plots in Cartowik.
    # csr.add_topography(filename, ax=ax0, cmap='Blues_r')
    # csr.add_multishade(filename, ax=ax0)

    # contour code too slow for full dem
    data.plot.contour(ax=ax0, colors='0.25', levels=range(70, 100),
                      linewidths=0.1)
    data.plot.contour(ax=ax0, colors='0.25', levels=range(70, 100, 5),
                      linewidths=0.25).clabel(fmt='%d')

    # plot borehole locations on the map
    initial, projected = project_borehole_locations(sensdate, ax0.projection)
    for bh in ('bh1', 'bh2', 'bh3'):
        color = util.tem.COLOURS[bh]
        ax0.plot(*initial[bh], color='0.25', marker='+')
        ax0.plot(*projected[bh], color=color, marker='+')
        ax0.text(*projected[bh]+np.array([10, 0]), s=bh.upper(), color=color,
                 ha='left', va='center', fontweight='bold')

        # add arrows and uncertainty circles
        if bh != 'bh1':
            ax0.annotate('', xy=projected[bh], xytext=initial[bh],
                         arrowprops=dict(arrowstyle='->', color=color))
            ax0.add_patch(plt.Circle(projected[bh], radius=10.0, fc='w',
                                     ec=color, alpha=0.5))

    # add scale
    cde.add_scale_bar(ax=ax0, color='k', label='100 m', length=100)

    # plot Arctic DEM topographic profile
    points = [2*projected['bh3']-projected['bh1'],
              2*projected['bh1']-projected['bh3']]
    x, y = build_profile_coords(points, interval=1)
    data.interp(x=x, y=y, method='linear').plot(ax=ax1, color='0.25')

    # mark borehole locations along profile
    for bh in ('bh1', 'bh3'):
        color = util.tem.COLOURS[bh]
        dist = ((projected[bh]-points[0])**2).sum()**0.5
        ax1.axvline(dist, color=color)
        ax1.text(dist, 76, ' '+bh.upper()+' ', color=color, fontweight='bold')

    # set axes properties
    ax1.set_xlabel('distance along profile (m)')
    ax1.set_ylabel('surface elevation (m)')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
