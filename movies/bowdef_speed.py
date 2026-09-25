#!/usr/bin/env python
# Copyright (c) 2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin velocity animation from satellite feature-tracking."""


import absplots as apl
import matplotlib.animation
import pandas as pd
import xarray as xr

import bowdef_utils
import bowtem_utils


def update(date, artists, frames, gnss, ds):
    """Update artists for the corresponding date."""

    # update map image and quiver (it stores arrows in xy order)
    now = frames.sel(date=date)
    artists['quiver'].set_UVC(now.u.T, now.v.T)
    artists['image'].set_data(now.speed)

    # update map date label and station marker
    artists['label'].set_text(date.strftime('%d %b %Y'))
    artists['star'].set_data([gnss.x[date]], [gnss.y[date]])
    artists['star'].set_alpha(0.5+0.5*gnss.measured[str(date.date())].any())

    # update timeseries and errorbar transparency
    artists['curve'].set_ydata(gnss.vh.where(gnss.index <= date))
    artists['bars'][0].set_alpha(ds.time.values <= date)
    artists['bars'][1].set_alpha(ds.time.values <= date)


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(192, 108))
    fig.add_axes_mm([3, 3, 72, 102])
    fig.add_axes_mm([90, 9, 99, 96])
    fig.add_axes_mm([96, 66, 6, 30])

    # add subfigure labels
    artists = {}
    bowtem_utils.add_subfig_label('(a)', ax=fig.axes[0], color='w')
    artists['label'] = bowtem_utils.add_subfig_label(
        '...', ax=fig.axes[0], color='w', loc='sw')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[1], color='k')

    # open 2015 images in multi-file dataset
    ds = xr.open_mfdataset(
        '../data/satellite/bowdoin-landsat-uv/*2015_*2015_*.nc',
        combine='nested', combine_attrs='drop_conflicts', concat_dim='time',
        preprocess=lambda ds: ds.assign(title=ds.title.split('/')[-1]))

    # extract intervals and velocity components
    ds = ds.assign(start=xr.DataArray(
        data=pd.to_datetime(ds.title.str[0:8], format='%d%m%Y').values,
        dims='time'))
    ds = ds.assign(end=xr.DataArray(
        data=pd.to_datetime(ds.title.str[9:17], format='%d%m%Y').values,
        dims='time'))
    ds = ds.assign(days=ds.end-ds.start)
    ds = ds.assign(time=ds.start+ds.days/2)
    u = ds.sel(time=ds.title.str.contains('u')).drop_vars('title')
    v = ds.sel(time=ds.title.str.contains('v')).drop_vars('title')
    ds = xr.merge([u.rename(z='u'), v.rename(z='v')], compat='no_conflicts')

    # crop to Bowdoin tongue, select 2015 images, and sort by date
    ds = ds.sel(x=slice(505e3, 515e3), y=slice(8630e3, 8620e3))
    ds = ds.where(ds.time.dt.year == 2015, drop=True).sortby('time').load()

    # estimate error as 0.2 pixel (3 m) over the pair interval, assuming
    # feature-tracking on 15 m Landsat 8 panchromatic images
    # FIXME get a better error estimate from new images
    ds = ds.assign(error=3 * 365 / ds.days.dt.days)

    # compute velocity magnitude
    ds = ds.assign(speed=(ds.u**2+ds.v**2)**0.5)

    # average pairs covering each daily frame, weighted by inverse variance
    dates = pd.date_range(
        ds.time[0].values, ds.time[-1].values, freq='1D', normalize=True)
    date = xr.DataArray(dates, dims='date', coords={'date': dates})
    weights = ((ds.start <= date) & (date <= ds.end)) / ds.error**2
    frames = ds[['u', 'v']].weighted(weights).mean('time')
    frames = frames.transpose('date', 'y', 'x')
    frames = frames.assign(speed=(frames.u**2+frames.v**2)**0.5)

    # plot background map
    bowtem_utils.plot_bowdoin_map(fig.axes[0], boreholes=[], season='summer')

    # interpolate gnss positions across data gaps and to image dates
    gnss = bowdef_utils.load_gnss_velocities(method='savgol', window='12h')
    xy = gnss[['x', 'y']].interpolate(method='time', limit_area='inside')
    gnss = gnss.assign(x=xy.x, y=xy.y, measured=gnss.x.notna())
    xy = xy.reindex(ds.time.values, method='nearest')
    ds = ds.assign(gnssx=('time', xy.x.values), gnssy=('time', xy.y.values))

    # plot first frame
    artists['image'] = frames.speed[0].plot.imshow(
        ax=fig.axes[0], add_labels=False, alpha=0.75, cbar_ax=fig.axes[2],
        cmap='Blues', extend='max', vmin=0, vmax=600)
    artists['quiver'] = frames.isel(date=0).plot.quiver(
        x='x', y='y', u='u', v='v', ax=fig.axes[0], add_guide=False,
        color='0.25', scale=2, scale_units='x')
    fig.axes[0].quiverkey(
        artists['quiver'], 0.85, 0.125, 500, r'500$\,m\,a^{-1}$', color='w',
        labelcolor='w', labelpos='S')
    artists['star'], = fig.axes[0].plot(
        gnss.x[dates[0]], gnss.y[dates[0]], marker='*', markersize=8,
        color='tab:orange')

    # plot gnss velocity first (higher-frequency pandas plots clear the axes)
    artists['curve'] = gnss.vh.plot(
        ax=fig.axes[1], color='tab:orange', label='GNSS').lines[-1]

    # plot satellite velocity at gnss location
    df = ds.interp(x=ds.gnssx, y=ds.gnssy).to_dataframe()
    errorbar = bowdef_utils.plot_errorbar(
        fig.axes[1], df, color='tab:blue', label='Landsat 8')
    artists['bars'] = errorbar.lines[2]

    # set axes properties
    fig.axes[1].legend(loc='upper right')
    fig.axes[0].set_aspect('equal')
    fig.axes[0].set_title('')
    fig.axes[0].set_xlabel('')
    fig.axes[0].set_ylabel('')
    fig.axes[1].set_xlabel('')
    fig.axes[1].set_xlim(
        dates[0].to_period('M').start_time, dates[-1].to_period('M').end_time)
    fig.axes[1].set_ylabel(r'surface velocity ($m\,a^{-1}$)')
    fig.axes[2].set_ylabel(r'interpolated velocity ($m\,a^{-1}$)')

    # save last frame as still image
    fargs = (artists, frames, gnss, ds)
    update(dates[-1], *fargs)
    fig.savefig(__file__[:-3])

    # animate at daily intervals
    ani = matplotlib.animation.FuncAnimation(
        fig, update, fargs=fargs, frames=dates)
    ani.save(__file__[:-3]+'.mp4', fps=10)


if __name__ == '__main__':
    main()
