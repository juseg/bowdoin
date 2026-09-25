#!/usr/bin/env python
# Copyright (c) 2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin strain animation from satellite feature-tracking."""


import absplots as apl
import matplotlib as mpl
import matplotlib.animation
import pandas as pd
import xarray as xr

import bowdef_utils
import bowtem_utils
import bowdef_speed  # FIXME move errorbar plot to utils


def func(date, fig, ds, gnss):
    now = ds.isel(time=abs(ds.time-date.to_datetime64()).argmin('time').item())
    quiver = next(
        c for c in fig.axes[0].collections if isinstance(c, mpl.quiver.Quiver))
    quiver.set_UVC(now.u.T, now.v.T)
    fig.axes[0].images[1].set_data(now.eeh)
    fig.axes[0].texts[1].set_text(date.strftime('%d %b %Y'))
    star = fig.axes[0].lines[-1]
    star.set_data([gnss.x[date]], [gnss.y[date]])
    star.set_alpha(1 if gnss.measured[str(date.date())].any() else 0.5)
    fig.axes[1].lines[0].set_ydata(gnss.vh.where(gnss.index <= date))
    hbars = fig.axes[1].collections[0]
    hbars.set_alpha(ds.time.values <= date)
    vbars = fig.axes[1].collections[1]
    vbars.set_alpha(ds.time.values <= date)


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(192, 108))
    fig.add_axes_mm([3, 3, 72, 102])
    fig.add_axes_mm([93, 9, 96, 96])
    fig.add_axes_mm([96, 66, 6, 30])

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=fig.axes[0], color='w')
    bowtem_utils.add_subfig_label('...', ax=fig.axes[0], color='w', loc='sw')
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

    # plot background map
    bowtem_utils.plot_bowdoin_map(fig.axes[0], boreholes=[], season='summer')

    # interpolate gnss positions across data gaps and to image dates
    gnss = bowdef_utils.load_gnss_velocities(method='savgol', window='12h')
    xy = gnss[['x', 'y']].interpolate(method='time', limit_area='inside')
    gnss = gnss.assign(x=xy.x, y=xy.y, measured=gnss.x.notna())
    xy = xy.reindex(ds.time.values, method='nearest')
    ds = ds.assign(gnssx=('time', xy.x.values), gnssy=('time', xy.y.values))

    # compute effective strain rate
    du_dx = ds.u.differentiate("x")
    du_dy = ds.u.differentiate("y")
    dv_dx = ds.v.differentiate("x")
    dv_dy = ds.v.differentiate("y")
    ds = ds.assign(eeh=(2*(du_dx**2+dv_dy**2)+(du_dy+dv_dx)**2)**0.5)

    # plot first frame
    ds.eeh[0].plot.imshow(
        ax=fig.axes[0], add_labels=False, alpha=0.75, cbar_ax=fig.axes[2],
        cmap='Reds', vmin=0, vmax=1)
    quiver = ds.isel(time=0).plot.quiver(
        x='x', y='y', u='u', v='v', ax=fig.axes[0], add_guide=False, alpha=0.75)
    fig.axes[0].plot(
        ds.gnssx[0], ds.gnssy[0], marker='*', markersize=8, color='tab:orange')

    # plot gnss velocity first (higher-frequency pandas plots clear the axes)
    gnss.vh.plot(ax=fig.axes[1], color='tab:orange')

    # plot time series FIXME a bit similar to errorbar plot from dataframe
    # FIXME get a better error estimate from new images
    dsi = ds.interp(x=ds.gnssx, y=ds.gnssy)
    dsi = dsi.assign(speed=(dsi.u**2+dsi.v**2)**0.5)
    # estimate error as 0.2 pixel (3 m) over the pair interval, assuming
    # feature-tracking on 15 m Landsat 8 panchromatic images
    dsi = dsi.assign(error=3 * 365 / dsi.days.dt.days)
    dsi = dsi.squeeze()
    df = dsi.to_dataframe()
    bowdef_speed.plot_satellite(fig.axes[1], df, color='tab:blue')

    # set axes properties
    fig.axes[0].set_aspect('equal')
    fig.axes[0].set_title('')
    fig.axes[0].set_xlabel('')
    fig.axes[0].set_ylabel('')
    fig.axes[1].set_xlabel('')
    fig.axes[1].set_xlim('20150301', '20150930')
    fig.axes[1].set_ylabel(r'velocity magnitude ($m\,a^{-1}$)')
    fig.axes[2].set_ylabel(r'horizontal effective strain rate ($a^{-1}$)')

    # save
    fig.savefig(__file__[:-3])

    # animate at daily intervals, showing the nearest image
    dates = pd.date_range(
        ds.time[0].values, ds.time[-1].values, freq='1D', normalize=True)
    ani = matplotlib.animation.FuncAnimation(
        fig, func, fargs=(fig, ds, gnss), frames=dates)
    ani.save(__file__[:-3]+'.mp4', fps=10)


if __name__ == '__main__':
    main()
