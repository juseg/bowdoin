#!/usr/bin/env python2

import util as ut
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot(targets, ofile='map_grl_gmb'):
    """Plot mass change rates pairwise between three target dates."""

    # open dataset
    ds = xr.open_dataset('../data/external/GIS_GMB_grid.nc')
    dm = ds['dm']

    # print available dates
    #print dm.time.to_index().strftime('%Y-%m-%d')

    # select dates nearest to targets
    targets = pd.to_datetime(targets)
    dm = dm.sel(time=targets, method='nearest')

    # format matching dates for later
    matches = dm.time.to_index().strftime('%Y-%m')

    # compute rate of mass change
    oneyear = pd.to_timedelta('365.25D')
    ddm = dm.diff(dim='time')
    dt = dm.time.diff(dim='time')/oneyear
    rate =  ddm / dt

    # geographic projection
    proj = ccrs.Stereographic(central_latitude=90.0,
                              central_longitude=-45.0,
                              true_scale_latitude=70.0)

    # initialize figure
    figw, figh = 85.0, 90.0
    fig, grid = plt.subplots(1, 2, figsize=(figw/25.4, figh/25.4),
                             gridspec_kw=dict(left=2.5/figw, right=1-2.5/figw,
                                              bottom=15.0/figh, top=1-5.0/figh,
                                              wspace=1/(((figw-5.0)/2.5+1)/2-1)),
                             subplot_kw=dict(projection=proj))
    cax = fig.add_axes([2.5/figw, 7.5/figh, 1-5.0/figw, 5.0/figh])

    # plot
    for i, ax in enumerate(grid):
        levs = range(-500, 501, 100)
        cs = rate[i].plot.contourf(ax=ax, levels=levs, cmap='RdBu',
                                   add_colorbar=False)
        ax.set_title('%s to %s' % (matches[i], matches[i+1]))

    # set axes limits and add coastline
    for ax in grid:
        ax.set_xlim(-650e3, 900e3)    # 1550 km = 38.75 * 40
        ax.set_ylim(-3400e3, -600e3)  # 2800 km = 70.00 * 40
        ax.coastlines(resolution='50m', color='k', lw=0.5)

    # plot Qaanaaq location
    c = 'k'
    ut.pl.add_waypoint('Qaanaaq', ax=ax, color=c)
    ax.text(-450000, -1250000, 'Qaanaaq', color=c, ha='left', fontweight='bold')

    # add colorbar and save
    cb = fig.colorbar(cs, cax, orientation='horizontal')
    cb.set_label('Mass change rate ($mm\ w.eq.\,a^{-1}$ or $kg\,m^{-1}\,a^{-1}$)', labelpad=2)
    ut.pl.savefig(fig)

    # close dataset
    ds.close()

def multiplot(*args):
    """Plot multiple figures for comparison."""

    # plot for each targetlist
    for targets in args:
        plot(targets, ofile='map_grl_gmb_%s.png' % ''.join([m[2:4] for m in targets]))

if __name__ == '__main__':
    """Main program."""

    # plot single figure
    plot(['2002-09-16', '2007-09-16', '2015-09-16'])  # extended Shu14

    # plot multiple figures
    #multiplot(
    #    ['2003-02-16', '2007-02-16', '2009-06-16'],  # Khan et al. (2010)
    #    ['2003-09-16', '2007-09-16', '2011-08-16'],  # Sutterley et al. (2014)
    #    ['2002-09-16', '2007-09-16', '2015-09-16'],  # extended Shu14
    #)
