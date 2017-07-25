#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import util as ut

def get_profiles(depth, temp):
    """Return avg, min and max temperature profile from data frame."""

    # remove sensors above the ground
    inicecols = depth > 0.0
    temp = temp[temp.columns[inicecols]]
    depth = depth[inicecols]

    # order by depth
    depth = depth.sort_values()
    temp = temp[depth.index.values]

    # extract values
    tmin = temp.min().values
    tavg = temp.mean().values
    tmax = temp.max().values
    z = depth.values

    return z, tmin, tavg, tmax

# initialize figure
figw, figh = 135.0, 120.0
fig, grid = ut.pl.subplots_mm(nrows=1, ncols=2, figsize=(figw, figh),
                              left=10.0, bottom=45.0, right=10.0, top=5.0,
                              wspace=5.0, hspace=5.0, sharey=True)
tsax = fig.add_axes([10.0/figw, 10.0/figh, 1-20.0/figw, 30.0/figh])

# add a, b, and c labels
grid[0].text(0.02, 0.92, '(a)', fontweight='bold', transform=grid[0].transAxes)
grid[1].text(0.02, 0.92, '(b)', fontweight='bold', transform=grid[1].transAxes)
tsax.text(0.05, 0.88, '(c)', fontweight='bold', transform=tsax.transAxes)

# dates to plot
start = '2014-11-01'
end = '2015-11-01'

# plot upstream temperature profile
ax = grid[0]
bh = ut.boreholes[0]
c = ut.colors[bh]

# read temperature values
temp_temp = ut.io.load_data('thstring', 'temp', bh).resample('1D').mean()[start:end]
tilt_temp = ut.io.load_data('tiltunit', 'temp', bh).resample('1D').mean()[start:end]

# read depths
temp_depth = ut.io.load_depth('thstring', bh).squeeze()
tilt_depth = ut.io.load_depth('tiltunit', bh).squeeze()
base_depth = ut.io.load_depth('pressure', bh).squeeze()

# sensors can't be lower than the base
temp_depth = np.minimum(temp_depth, base_depth)

# extract profiles
temp_z, temp_tmin, temp_tavg, temp_tmax = get_profiles(temp_depth, temp_temp)
tilt_z, tilt_tmin, tilt_tavg, tilt_tmax = get_profiles(tilt_depth, tilt_temp)

# plot profile
ax.fill_betweenx(temp_z, temp_tmin, temp_tmax,
                 facecolor=c, edgecolor='none', alpha=0.25)
ax.fill_betweenx(tilt_z, tilt_tmin, tilt_tmax,
                 facecolor='0.75', edgecolor='none', alpha=0.25)
ax.plot(temp_tavg, temp_z, '-o', c=c, label=bh)
ax.plot(tilt_tavg, tilt_z, '-^', c='0.75')

# add base line
ax.axhline(base_depth, c='k')

# plot melting point
g = 9.80665     # gravity
rhoi = 910.0    # ice density
beta = 7.9e-8   # Luethi et al. (2002)
base_temp_melt = -beta * rhoi * g * base_depth
ax.plot([0.0, base_temp_melt], [0.0, base_depth], c='k', ls=':')

# set axes properties
ax.set_xlim(-12.0, 1.0)
ax.set_ylim(270.0, 0.0)
ax.set_ylabel('depth (m)')
ax.set_title(u'ice temperature (°C)')

# plot upstream tilt profile
ax = grid[1]

# read data values
exz = ut.io.load_total_strain(bh, start, end)
notnull = exz.notnull()
tilt_depth = tilt_depth[notnull]
exz = exz[notnull]

# plot velocity profile
ut.pl.plot_vsia_profile(tilt_depth, exz, base_depth, ax=ax, c=c, annotate=False)

# set axes properties
ax.set_xlim(32.5, 0.0)
ax.set_title(r'ice deformation (m a$^{-1}$)')

# plot downstream water level time series
ax = tsax
bh = ut.boreholes[0]
c = ut.colors[bh]
ts = ut.io.load_data('pressure', 'wlev', bh).resample('12H').mean()[1:]
ts.plot(ax=ax, c=c, legend=False)

# add label
ax.set_ylabel('water level (m)', color=c)
ax.locator_params(axis='y', nbins=6)

# plot GPS velocity
ax = ax.twinx()
c = ut.colors['dgps']
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('12H').mean()
ts.plot(ax=ax, c=c, legend=False)

# add label and set limits
ax.set_ylabel(r'surface velocity ($m\,a^{-1}$)', labelpad=0.0, color=c)
ax.set_xlim('2014-07-01', '2016-08-01')
ax.set_ylim(0, 800)
ax.locator_params(axis='y', nbins=6)

# add field campaigns
ut.pl.plot_campaigns(ax)

# save
ut.pl.savefig(fig)
