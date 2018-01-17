#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


# initialize figure
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


# map axes
# --------

ax = ax1

# initialize figure
#fig = plt.figure()
#ax = fig.add_axes([0, 0, 1, 1], projection=utm)
ax.set_rasterization_zorder(2.5)
ax.set_extent(reg, crs=utm)

# plot image data
filename = '../data/external/S2A_20160808_175915_456_RGB.jpg'
data, extent = ut.io.open_gtif(filename)
data = np.moveaxis(data, 0, 2)
ax.imshow(data, extent=extent, transform=utm, cmap='Blues')

# plot borehole and camera locations
kwa = dict(ax=ax, color='C0', marker='o')
ut.pl.add_waypoint('B14BH1', text='2014', **kwa)
ut.pl.add_waypoint('B16BH1', text='2016', **kwa)
ut.pl.add_waypoint('B17BH1', text='2017', **kwa)
kwa = dict(ax=ax, color='C6', marker='o')
ut.pl.add_waypoint('B14BH3', **kwa)
ut.pl.add_waypoint('B16BH3', **kwa)
ut.pl.add_waypoint('B17BH3', **kwa)
kwa = dict(ax=ax, color='C1', marker='^')
ut.pl.add_waypoint('Camera Upper', **kwa)
ut.pl.add_waypoint('Camera Lower', text='Camera', **kwa)
kwa = dict(ax=ax, color='C3', marker='^')
ut.pl.add_waypoint('Tent Swiss', text='Camp', **kwa)
#ut.pl.add_waypoint('Camp Hill', text='Hill', **kwa)

# add scale
ax.plot([508.25e3, 509.25e3], [8620.25e3]*2, 'w|-')
ax.text(508.75e3, 8620.4e3, '1km', color='w', ha='center', fontweight='bold')


# distance axes
# -------------

ax = ax2

# arbitrary borehole distances
distances = {'U':2.0, 'L':1.85}

# plot tilt unit depths
z = ut.io.load_bowtid_depth()
for u in z.index:
    x = distances[u[0]]
    ax.plot(x, z[u], marker='s')
    ax.text(x+0.01, z[u], u, va='center')

# add base line
zp = ut.io.load_depth('pressure', 'both')
for u in zp.index:
    x = distances[u[0]]
    b = max(zp[u], z[z.index.str.startswith(u[0])].max())
    ax.plot([x, x], [b, 0.0], 'k-_')

# add flow direction arrow
ax.text(0.9, 0.55, 'ice flow', ha='center', transform=ax.transAxes)
ax.annotate('', xy=(0.85, 0.5), xytext=(0.95, 0.5),
            xycoords=ax.transAxes, textcoords=ax.transAxes,
            arrowprops=dict(arrowstyle='->',  lw=1.0))

# set axes properties
ax.set_xlim(1.75, 2.15)
ax.set_xticks(distances.values())
ax.set_xlabel('approximate distance from front in 2014 (km)')
ax.set_ylabel('depth (m)')
ax.invert_yaxis()

# save
ut.pl.savefig(fig)
