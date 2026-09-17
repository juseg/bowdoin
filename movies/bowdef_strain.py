#!/usr/bin/env python
# Copyright (c) 2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin strain animation from satellite feature-tracking."""


import absplots as apl
import geopandas as gpd
import matplotlib as mpl
import matplotlib.animation
import numpy as np
import pandas as pd
import xarray as xr

import bowtem_utils
import bowdef_speed  # FIXME move errorbar plot to utils


def func(frame, fig, ds):
    now = ds.isel(time=frame)
    quiver = next(
        c for c in fig.axes[0].collections if isinstance(c, mpl.quiver.Quiver))
    quiver.set_UVC(now.u.T, now.v.T)
    fig.axes[0].images[1].set_data(now.speed)
    fig.axes[0].set_title(now.time.dt.strftime('%d %b %Y').values)
    hbars = fig.axes[1].collections[0]
    hbars.set_alpha(np.arange(len(ds.time)) <= frame)
    vbars = fig.axes[1].collections[1]
    vbars.set_alpha(np.arange(len(ds.time)) <= frame)


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    fig.add_axes_mm([2.5, 2.5, 60, 85])
    fig.add_axes_mm([77.5, 12.5, 100, 75])
    axes = fig.axes

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=fig.axes[0], color='w')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[1], color='k')

    # open images in multi-file dataset
    # note: choose between using datetime and pd.to_datetime
    ds = xr.open_mfdataset(
        '../data/satellite/bowdoin-landsat-uv/*.nc',
        combine='nested', combine_attrs='drop_conflicts', concat_dim='time',
        preprocess=lambda ds: ds.assign(
            title=ds.title.split('/')[-1],
            # start=datetime.datetime.strptime(
            #     ds.title.split('/')[-1].split('_')[0], '%d%m%Y'),
            # end=datetime.datetime.strptime(
            #     ds.title.split('/')[-1].split('_')[1], '%d%m%Y'),
            ))

    # extract intervals and velocity components
    ds = ds.assign(start=xr.DataArray(
        pd.to_datetime(ds.title.str[0:8], format='%d%m%Y').values, dims='time'))
    ds = ds.assign(end=xr.DataArray(
        pd.to_datetime(ds.title.str[9:17], format='%d%m%Y').values, dims='time'))
    ds = ds.assign(days=ds.end-ds.start)
    ds = ds.assign(time=ds.start+ds.days/2)
    u = ds.sel(time=ds.title.str.contains('u')).drop_vars('title')  # .z.rename('u')
    v = ds.sel(time=ds.title.str.contains('v')).drop_vars('title')  # .z.rename('v')
    ds = xr.merge([u.rename(z='u'), v.rename(z='v')], compat='no_conflicts')

    # crop to Bowdoin tongue, select 2015 images, and sort by date
    ds = ds.sel(x=slice(505e3, 515e3), y=slice(8630e3, 8620e3))
    ds = ds.where(ds.time.dt.year==2015, drop=True).sortby('time')

    # plot background map FIXME allow plotting no boreholes
    bowtem_utils.plot_bowdoin_map(fig.axes[0], boreholes=['bh1'], season='summer')

    # interpolate to borehole location FIXME get precise location from GNSS
    gdf = gpd.read_file('../data/locations.gpx', layer='waypoints')
    gdf = gdf.set_index('name').loc[['B14BH1']]
    gdf = gdf.to_crs('+proj=utm +zone=19')
    gdf.plot(ax=axes[0], marker='*', markersize=60)

    # plot first frame
    ds = ds.assign(speed=(ds.u**2+ds.v**2)**0.5)
    ds.speed[0].plot.imshow(ax=axes[0], add_colorbar=False, add_labels=False, alpha=0.75)
    ds.isel(time=0).plot.quiver(x='x', y='y', u='u', v='v', ax=axes[0], alpha=0.75)

    # plot time series FIXME a bit similar to errorbar plot from dataframe
    dsi = ds.interp(x=gdf.geometry.x, y=gdf.geometry.y)
    dsi = dsi.assign(error=1)
    dsi = dsi.squeeze()
    df = dsi.to_dataframe()
    df.speed.resample('1D').mean().interpolate(method='linear').plot(ax=axes[1], alpha=0.25)
    bowdef_speed.plot_satellite(axes[1], df, color='tab:blue')

    # set axes properties
    axes[0].set_aspect('equal')

    # save
    fig.savefig(__file__[:-3])

    # animate
    ani = matplotlib.animation.FuncAnimation(
        fig, func, fargs=(fig, ds), frames=len(ds.time))
    ani.save(__file__[:-3]+'.mp4', fps=10)


if __name__ == '__main__':
    main()
