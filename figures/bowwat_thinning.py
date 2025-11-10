#!/usr/bin/env python2
# Copyright (c) 2018-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)
# coding: utf-8

import util as ut
import gpxpy
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


years = [2014, 2016, 2017]
colors = ['C0', 'C1', 'C2']

# Initialize figure
# -----------------

# projections and map boundaries
ll = ccrs.PlateCarree()
utm = ccrs.UTM(19)
reg = 507.5e3, 512.5e3, 8620e3, 8627e3

# initialize figure
figw, figh = 150.0, 75.0
fig = plt.figure(figsize=(figw/25.4, figh/25.4))
ax1 = fig.add_axes([2.5/figw, 2.5/figh, 50.0/figw, 1-5.0/figh], projection=utm)
ax2 = fig.add_axes([67.5/figw, 10.0/figh, 80.0/figw, 1-12.5/figh])
ax1.set_rasterization_zorder(2.5)
ax1.set_extent(reg, crs=utm)


# Read GPX data
# -------------

# open GPX file as a dictionary
locations = {}
with open('../data/locations.gpx', 'r') as gpx_file:
    for wpt in gpxpy.parse(gpx_file).waypoints:
        xy = utm.transform_point(wpt.longitude, wpt.latitude, ll)
        locations[wpt.name] = xy

# compute distances
distances = {}
for y in years:
    ux, uy = locations['B%2dBH2' % (y-2000)]
    lx, ly = locations['B%2dBH3' % (y-2000)]
    distances[y] = ((ux-lx)**2 + (uy-ly)**2)**0.5

# load time-dependent base and sensor depths
lb = bowdef_utils.load_data('pressure', 'base', 'lower')
ub = bowdef_utils.load_data('pressure', 'base', 'upper')
lz = bowdef_utils.load_data('pressure', 'depth', 'lower')
uz = bowdef_utils.load_data('pressure', 'depth', 'upper')


# Map axes
# --------

ax = ax1

# plot image data
filename = '../data/native/S2A_20160808_175915_456_RGB.jpg'
data, extent = bowdef_utils.open_gtif(filename)
data = np.moveaxis(data, 0, 2)
ax.imshow(data, extent=extent, transform=utm, cmap='Blues')

# plot borehole locations
for y, c in zip(years, colors):
    kwa = {'ax': ax, 'color': c, marker: 'o'}
    bowdef_utils.add_waypoint('B%2dBH2' % (y-2000), text=y, **kwa)
    bowdef_utils.add_waypoint('B%2dBH3' % (y-2000), **kwa)

# plot camp location
kwa = {'ax': ax, 'color': 'C3', 'marker': '^'}
bowdef_utils.add_waypoint('Tent Swiss', text='Camp', **kwa)

# add scale
ax.plot([508.25e3, 509.25e3], [8620.25e3]*2, 'w|-')
ax.text(508.75e3, 8620.4e3, '1km', color='w', ha='center', fontweight='bold')


# Distance axes
# -------------

ax = ax2

# plot equal areas
for y, c in zip(years, colors):
    d = distances[y]
    ax.plot([0.0, d], [lz[str(y)].squeeze(), uz[str(y)].squeeze()], 'k+')
    ax.fill_between([0.0, d], [lb[str(y)].squeeze(), ub[str(y)].squeeze()],
                    [0.0]*2, edgecolor=c, facecolor='none', lw=1.0)
    ax.text(d, ub[str(y)].squeeze(), '  %d' % y, color=c, fontweight='bold')

# add text
ax.text(0.4, 0.55, 'assumed equal area', ha='center', va='center',
        transform=ax.transAxes)
ax.text(0.0, -5.0, 'lower', fontweight='bold', ha='center')
ax.text(d, -5.0, 'upper', fontweight='bold', ha='center')

# add flow direction arrow
ax.text(0.9, 0.55, 'ice flow', ha='center', transform=ax.transAxes)
ax.annotate(
    '', xy=(0.85, 0.5), xytext=(0.95, 0.5), xycoords=ax.transAxes,
    textcoords=ax.transAxes, arrowprops={'arrowstyle': '->', 'lw': 1})

# set axes properties
ax.set_xlim(-15.0, 245.0)
ax.set_ylim(270.0, -20.0)
ax.set_xlabel('distance from lower borehole (m)')
ax.set_ylabel('depth (m)')

# save
bowdef_utils.savefig(fig)
