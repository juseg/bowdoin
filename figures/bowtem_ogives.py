#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature Arctic DEM map and profile."""

from scipy import stats
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import absplots as apl
import cartowik.decorations as cde
import cartowik.shadedrelief as csr
import util


def init_figure():
    """Initialize figure with map and profile subplots."""

    # initialize figure
    crs = ccrs.Stereographic(
        central_latitude=90, central_longitude=-45, true_scale_latitude=70)
    fig, grid = apl.subplots_mm(
        figsize=(180, 120), ncols=3, projection=crs, gridspec_kw=dict(
            left=2.5, right=22.5, bottom=65, top=5, wspace=2.5))

    # add colorbar and profile axes
    cax = fig.add_axes_mm([160, 65, 5, 50])
    pfax = fig.add_axes_mm([2.5, 12.5, 162.5, 50])
    pfax.yaxis.set_label_position("right")
    pfax.yaxis.tick_right()

    # add subfigure labels
    for ax, label in zip(list(grid) + [pfax], 'abcd'):
        util.com.add_subfig_label(ax=ax, text='('+label+')')

    # return figure and axes
    return fig, grid, cax, pfax


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
    gps = gps.interpolate().loc[date].mean()
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
    fig, grid, cax, pfax = init_figure()

    # selected Arctic DEM data strips
    st0 = 'SETSM_W1W2_20140905_10200100318E9F00_1030010037BBC200_seg3_2m_v3.0'
    st1 = 'SETSM_WV01_20170318_10200100602AB700_102001005FDC9000_seg1_2m_v3.0'
    st1 = 'SETSM_WV02_20160424_10300100566BCD00_103001005682C900_seg6_2m_v3.0'

    # load reference elevation data
    elev = xr.open_rasterio('../data/external/%s.tif' % st0)
    elev = elev.squeeze(drop=True)
    elev = elev.loc[-1224000:-1229000, -537500:-532500].where(elev > -9999)
    zoom = elev.loc[-1226725:-1227025, -535075:-534775]  # 300x300 m

    # load elevation difference data
    diff = xr.open_rasterio('../data/external/%s.tif' % st1)
    diff = diff.squeeze(drop=True)
    diff = diff.loc[-1224000:-1229000, -537500:-532500].where(diff > -9999)
    diff = diff - elev
    diff = diff - stats.mode(diff, axis=None)[0]

    # plot zoomed-in elevation map
    ax = grid[0]
    zoom.plot.imshow(ax=ax, add_colorbar=False, cmap='Blues_r')
    zoom.plot.contour(ax=ax, colors='0.25', levels=range(70, 100),
                      linewidths=0.1)
    zoom.plot.contour(ax=ax, colors='0.25', levels=range(70, 100, 5),
                      linewidths=0.25).clabel(fmt='%d')

    # plot reference elevation map
    # FIXME add xarray-centric cartowik methods
    csr._compute_multishade(elev, altitudes=[30]*4).plot.imshow(
        ax=grid[1], add_colorbar=False, cmap='Greys', vmin=-1, vmax=1)

    # plot elevation difference map
    diff.plot.imshow(ax=grid[2], cbar_ax=cax, cmap='RdBu', vmin=-20, vmax=20,
                     cbar_kwargs=dict(label='elevation change (m)'))

    # plot borehole locations on the map
    ax = grid[0]
    initial, projected = project_borehole_locations(st0[11:19], ax.projection)
    for bh in ('bh1', 'bh2', 'bh3'):
        color = util.tem.COLOURS[bh]
        ax.plot(*initial.loc[bh], color='0.25', marker='+')
        ax.plot(*initial.loc[bh], color='0.25', marker='+')
        ax.plot(*projected.loc[bh], color=color, marker='+')
        ax.text(*projected.loc[bh]+np.array([10, 0]), s=bh.upper(),
                color=color, ha='left', va='center', fontweight='bold')

        # add arrows and uncertainty circles
        if bh != 'bh1':
            ax.annotate('', xy=projected.loc[bh], xytext=initial.loc[bh],
                        arrowprops=dict(arrowstyle='->', color=color))
            ax.add_patch(plt.Circle(projected.loc[bh], radius=10.0, fc='w',
                                    ec=color, alpha=0.5))

    # add scales
    cde.add_scale_bar(ax=grid[0], color='k', label='50 m', length=50)
    cde.add_scale_bar(ax=grid[1], color='k', label='1 km', length=1000)

    # plot Arctic DEM topographic profile
    points = [1.5*projected.loc['bh3']-0.5*projected.loc['bh1'],
              1.5*projected.loc['bh1']-0.5*projected.loc['bh3']]
    x, y = build_profile_coords(points, interval=1)
    ax.plot(x, y, color='0.25', linestyle='--')
    elev.interp(x=x, y=y, method='linear').plot(ax=pfax, color='0.25')

    # mark borehole locations along profile
    for bh in ('bh1', 'bh3'):
        color = util.tem.COLOURS[bh]
        dist = ((projected.loc[bh]-points[0])**2).sum()**0.5
        pfax.axvline(dist, color=color)
        pfax.text(dist, 76, ' '+bh.upper()+' ', color=color, fontweight='bold')

    # set axes properties
    grid[0].set_title(st0[11:19])
    grid[1].set_title(st0[11:19])
    grid[2].set_title(st1[11:19] + ' - ' + st0[11:19])
    pfax.set_xlabel('distance along profile (m)')
    pfax.set_ylabel('surface elevation (m)')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
