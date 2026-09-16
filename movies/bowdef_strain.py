#!/usr/bin/env python
# Copyright (c) 2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin strain animation from satellite feature-tracking."""


import absplots as apl
import matplotlib.animation
import pandas as pd
import xarray as xr


def func(frame, fig, ds):
    ds = ds.isel(time=frame)
    print(frame, ds.time.dt.strftime('%d %b %Y').values)
    fig.axes[0].images[0].set_data((ds.u**2+ds.v**2)**0.5)
    fig.texts[0].set_text(ds.time.dt.strftime('%d %b %Y').values)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(192, 108), ncols=2, sharex=True, sharey=True, gridspec_kw={
            'left': 2.5, 'bottom': 2.5, 'right': 2.5, 'top': 2.5, 'wspace': 2.5})

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

    # select 2015 images and sort by date
    ds = ds.where(ds.time.dt.year==2015, drop=True).sortby('time')

    # plot first frame
    ((ds.u[0]**2+ds.v[0]**2)**0.5).plot.imshow(
        ax=axes[0], add_colorbar=False, add_labels=False, alpha=0.75)
    fig.text(0.25, 0.1, 'text')

    # save
    fig.savefig(__file__[:-3])

    # animate
    ani = matplotlib.animation.FuncAnimation(
        fig, func, fargs=(fig, ds), frames=len(ds.time))
    ani.save(__file__[:-3]+'.mp4', fps=10)


if __name__ == '__main__':
    main()
