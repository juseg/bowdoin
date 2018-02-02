#!/usr/bin/env python2

import util as ut
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


# target dates
targets = ['2003-02-16', '2007-02-16', '2009-06-16']  # Khan et al. (2010)
targets = ['2003-09-16', '2007-09-16', '2011-08-16']  # Sutterley et al. (2014)
targets = ['2002-09-16', '2007-09-16', '2009-06-16', '2016-09-16']

# geographic projection
proj = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                          true_scale_latitude=70.0)

# initialize figure
nmaps = len(targets)-1
figw, figh = 150.0, 75.0
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=1, ncols=nmaps,
                              sharex=True, sharey=True, wspace=2.5,
                              left=2.5, right=22.5, bottom=2.5, top=2.5,
                              subplot_kw=dict(projection=proj))
cax = fig.add_axes([1-20.0/figw, 2.5/figh, 5.0/figw, 1-5.0/figh])

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
rate = ddm / dt

# close dataset
ds.close()

# contour levels and colors (xarray fails on color arrays)
levs = range(-500, 501, 100)
cols = list(plt.get_cmap('PRGn', len(levs)+1)(range(len(levs)+1)))

# plot
for i, ax in enumerate(grid):
    levs = range(-500, 501, 100)
    cs = rate[i].plot.contourf(ax=ax, levels=levs, colors=cols,
                               cbar_ax=cax, add_labels=False)

    # add text label
    ax.text(0.93, 0.04, '%s\nto %s' % (matches[i], matches[i+1]),
            transform=ax.transAxes, ha='right', va='bottom')

    # add coastline
    ax.coastlines(resolution='50m', color='k', lw=0.5)

    # set axes limits
    ax.set_xlim(-675e3, 925e3)  # 1600 km = 40.0 * 40
    ax.set_ylim(-3400e3, -600e3)  # 2800 km = 70.0 * 40

# plot Qaanaaq location
c = 'k'
ut.pl.add_waypoint('Qaanaaq', ax=grid[1], color=c)
grid[1].text(-450000, -1250000, 'Qaanaaq', color=c, ha='left', fontweight='bold')

# add cbar label
cax.set_ylabel('Mass change rate ($mm\ w.eq.\,a^{-1}$ or $kg\,m^{-1}\,a^{-1}$)')

# add colorbar and save
ut.pl.savefig(fig)