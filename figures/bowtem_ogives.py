#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature Arctic DEM map and profile."""

from scipy import stats
import hyoga  # noqa pylint: disable=unused-import
import geopandas as gpd
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import absplots as apl
import pyproj
import bowtem_utils


def init_figure():
    """Initialize figure with map and profile subplots."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(180, 120), ncols=3, gridspec_kw={
            'left': 2.5, 'right': 22.5, 'bottom': 65, 'top': 5, 'wspace': 2.5})

    # add colorbar and profile axes
    cax = fig.add_axes_mm([160, 65, 5, 50])
    pfax = fig.add_axes_mm([2.5, 12.5, 162.5, 50])
    pfax.yaxis.set_label_position("right")
    pfax.yaxis.tick_right()

    # add subfigure labels
    for ax, label in zip(list(grid) + [pfax], 'abcd'):
        bowtem_utils.add_subfig_label(ax=ax, text='('+label+')')

    # return figure and axes
    return fig, grid, cax, pfax


def project_borehole_locations(date, crs):
    """
    Estimate borehole locations for a given date based their initial positions
    measured by hand-held GPS and the continuous D-GPS record at BH1.
    """

    # read initial positions from GPX file
    gdf = gpd.read_file('../data/locations.gpx').set_index('name').to_crs(crs)
    gdf = gdf[gdf.index.str.startswith('B14')]
    gdf = gdf.set_index(gdf.index.str[3:].str.lower())
    initial = gdf.geometry.get_coordinates()

    # interpolate DEM date BH1 location from continuous GPS
    trans = pyproj.Transformer.from_crs('+proj=lonlat', crs)
    gps = bowtem_utils.load('../data/processed/bowdoin.bh1.gps.csv')
    gps = gps.interpolate().loc[date].mean()
    gps['x'], gps['y'] = trans.transform(gps.lon, gps.lat)
    gps = gps[['x', 'y']]

    # compute DEM date positions from BH1 displacement with time mutliplier
    displacement = gps - initial.loc['bh1']
    date = pd.to_datetime(date, utc=True)
    date_init = pd.to_datetime(gdf.time)
    multiplier = (date - date_init.bh1) / (date - date_init)
    displacement = displacement.apply(lambda x: x*multiplier).T
    projected = initial + displacement

    # return initial and projected locations
    return initial, projected


def project_location(x, y, loc):
    """
    Find the distance along a profile corresponding to the nearest point of
    the profile to a given location.
    """
    dist = ((x-loc.x)**2+(y-loc.y)**2)**0.5
    dist = dist.where(dist == dist.min(), drop=True).d
    return dist


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid, cax, pfax = init_figure()

    # selected Arctic DEM data strips
    st0 = 'WV01_20140906_10200100318E9F00_1020010033454500_2m_lsf_seg2'  # 0.71
    st1 = 'WV01_20170318_10200100602AB700_102001005FDC9000_2m_lsf_seg1'  # 1.00
    st1 = 'WV02_20160424_10300100566BCD00_103001005682C900_2m_lsf_seg1'  # 0.95

    # load reference elevation data
    elev = xr.open_dataarray(f'../data/external/SETSM_s2s041_{st0}.tif')
    elev = elev.squeeze()
    elev = elev.loc[-1224000:-1229000, -537500:-532500].where(elev > -9999)
    zoom = elev.loc[-1226725:-1227025, -535075:-534775]  # 300x300 m

    # load elevation difference data
    diff = xr.open_dataarray(f'../data/external/SETSM_s2s041_{st1}.tif')
    diff = diff.squeeze()
    diff = diff.loc[-1224000:-1229000, -537500:-532500].where(diff > -9999)
    diff = diff - elev
    diff = diff - stats.mode(diff, axis=None, nan_policy='omit')[0]

    # plot zoomed-in elevation map
    ax = grid[0]
    zoom.plot.imshow(
        ax=ax, add_colorbar=False, add_labels=False, cmap='Blues_r')
    zoom.plot.contour(
        ax=ax, add_labels=False, colors='0.25', levels=range(70, 100),
        linewidths=0.1)
    zoom.plot.contour(
        ax=ax, add_labels=False, colors='0.25', levels=range(70, 100, 5),
        linewidths=0.25).clabel(fmt='%d')

    # plot reference elevation map
    ds = elev.assign_attrs(standard_name='bedrock_altitude').to_dataset()
    ds.hyoga.plot.bedrock_hillshade(
        ax=grid[1], add_colorbar=False, altitude=[15]*3, cmap='Greys')

    # plot elevation difference map
    diff.plot.imshow(
        ax=grid[2], add_labels=False, cbar_ax=cax, cmap='RdBu',
        vmin=-20, vmax=20, cbar_kwargs={'label': 'elevation change (m)'})

    # plot borehole locations on the map
    ax = grid[0]
    crs = '+proj=stere +lat_0=90 +lon_0=-45 +lat_ts=70'
    initial, projected = project_borehole_locations(st0[5:13], crs=crs)
    for bh in ('bh1', 'bh2', 'bh3'):
        color = bowtem_utils.COLOURS[bh]
        ax.plot(*initial.loc[bh], color='0.25', marker='+')
        ax.plot(*initial.loc[bh], color='0.25', marker='+')
        ax.plot(*projected.loc[bh], color=color, marker='+')
        loc = projected.loc[bh].values
        bowtem_utils.annotate_by_compass(
            bh.upper(), ax=ax, bbox={
                'alpha': 0.75, 'ec': color, 'fc': 'w', 'pad': 2},
            color=color, fontweight='bold', xy=loc, offset=12,
            point=('se' if bh == 'bh1' else 'nw'), zorder=10)

        # add arrows and uncertainty circles
        if bh != 'bh1':
            ax.annotate('', xy=loc, xytext=initial.loc[bh],
                        arrowprops={'arrowstyle': '->', 'color': color})
            ax.add_patch(plt.Circle(
                projected.loc[bh].values, radius=10.0, fc='w', ec=color,
                alpha=0.75))

        # on other maps too
        grid[1].plot(*loc, color=color, marker='o')
        grid[2].plot(*loc, color=color, marker='o')

    # add scales
    zoom.to_dataset().hyoga.plot.scale_bar(ax=grid[0], label=r'50$\,$m')
    elev.to_dataset().hyoga.plot.scale_bar(ax=grid[1])

    # interpolate along profile
    flowline = gpd.read_file('../data/native/flowline.shp').to_crs(crs)
    elev = elev.isel(y=slice(None, None, -1))  # work around hyoga issue #117
    elev = elev.to_dataset().hyoga.profile(flowline, interval=10).band_data
    elev = elev[elev.d < 5000]

    # plot map-view and topographic profiles
    grid[1].plot(elev.x, elev.y, color='w', linestyle='--')
    elev.plot(ax=pfax, color='0.25')

    # mark borehole locations along profile
    for bh in ['bh2', 'bh3']:
        color = bowtem_utils.COLOURS[bh]
        dist = project_location(elev.x, elev.y, projected.loc[bh])
        pfax.axvline(dist, color=color)
        pfax.text(dist, 40, ' '+bh.upper()+' ', color=color, fontweight='bold',
                  ha=('left' if bh == 'bh2' else 'right'))

    # set axes properties
    for ax in grid:
        ax.set_xticks([])
        ax.set_yticks([])
    grid[0].set_title(st0[5:9]+'-'+st0[9:11]+'-'+st0[11:13])
    grid[1].set_title(st0[5:9]+'-'+st0[9:11]+'-'+st0[11:13])
    grid[2].set_title(st1[5:9]+'-'+st1[9:11]+'-'+st1[11:13]+' - ' +
                      st0[5:9]+'-'+st0[9:11]+'-'+st0[11:13])
    pfax.set_title('')
    pfax.set_xlabel('distance from the calving front (m)')
    pfax.set_ylabel('surface elevation (m)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
