#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature Arctic DEM map and profile."""

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartowik.shadedrelief as csr
import absplots as apl
import gpxpy
import util


def coords_from_extent(extent, cols, rows):
    """Compute coordinate vectors from image extent."""

    # compute dx and dy
    (w, e, s, n) = extent
    dx = (e-w) / cols
    dy = (n-s) / rows

    # prepare coordinate vectors
    xwcol = w + 0.5*dx  # x-coord of W row cell centers
    ysrow = s + 0.5*dy  # y-coord of N row cell centers
    x = xwcol + np.arange(cols)*dx  # from W to E
    y = ysrow + np.arange(rows)*dy  # from S to N

    # return coordinate vectors
    return x, y


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


def main():
    """Main program called during execution."""

    # initialize figure
    # FIXME: Implement add_axes_mm / add_subplot_mm for unique subplots.
    fig = apl.figure_mm(figsize=(150, 75))
    gridspec_kw = dict(left=2.5, right=87.5, bottom=2.5, top=2.5)
    projection = ccrs.Stereographic(central_latitude=90, central_longitude=-45,
                                    true_scale_latitude=70)
    ax0 = fig.subplots_mm(gridspec_kw=gridspec_kw,
                          subplot_kw=dict(projection=projection))
    gridspec_kw = dict(left=75, right=2.5, bottom=10, top=2.5)
    ax1 = fig.subplots_mm(gridspec_kw=gridspec_kw)

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
    bounds = -535075, -1227050, -534775, -1226700  # 300x350m
    data, extent = csr._open_raster_data(filename, bounds=bounds)
    ax0.imshow(data, cmap='Blues_r', extent=extent, origin='upper')

    # FIXME: Implement windowed plotting in Cartowik.
    # FIXME: Implement contour plots in Cartowik.
    # csr.add_topography(filename, ax=ax0, cmap='Blues_r')
    # csr.add_multishade(filename, ax=ax0)

    # contour code too slow for full dem
    levs = np.arange(70.0, 100.0, 1.0)
    cs = ax0.contour(data, colors='0.25', levels=levs[(levs % 5 != 0)],
                     extent=extent, linewidths=0.1, origin='upper')
    cs = ax0.contour(data, colors='0.25', levels=levs[(levs % 5 == 0)],
                     extent=extent, linewidths=0.1, origin='upper')
    cs.clabel(fmt='%d')

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
    util.geo.add_scale_bar(ax=ax0, length=100, label='100 m', color='k')

    # prepare profile coords and compute distance from bh3
    coords = np.linspace(2*projected['bh3']-1*projected['bh1'],
                         2*projected['bh1']-1*projected['bh3'], 301)
    dist = ((coords-coords[0])**2).sum(axis=1)**0.5
    dist -= ((projected['bh3']-coords[0])**2).sum()**0.5

    # plot Arctic DEM topographic profile
    # FIXME: Implement profile interpolation in Cartowik (xarray?).
    demx, demy = coords_from_extent(extent, *data.shape[::-1])
    demz = sp.interpolate.interpn((demx, demy), data[::-1].T, coords,
                                  method='linear', bounds_error=False)
    ax1.plot(dist, demz, color='0.25')

    # mark borehole locations along profile
    for bh in ('bh1', 'bh2', 'bh3'):
        color = util.tem.COLOURS[bh]
        dist = ((projected[bh]-projected['bh3'])**2).sum()**0.5
        ax1.axvline(dist, color=color)
        ax1.text(dist, 76, ' '+bh.upper()+' ', color=color, fontweight='bold',
                 ha=('right' if bh == 'bh1' else 'left'))

    # set axes properties
    ax1.set_xlabel('distance along flow (m)')
    ax1.set_ylabel('surface elevation (m)')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
