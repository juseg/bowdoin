#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


# Initialize figure
# -----------------

# projections and map boundaries
ll = ccrs.PlateCarree()
utm = ccrs.UTM(19)
reg = 507.5e3, 512.5e3, 8620e3, 8627e3  # 5.0x7.0 km full glacier tongue
reg = 507.6e3, 512.4e3, 8620.7e3, 8626.3e3  # 4.8x5.6 km full glacier tongue

# initialize figure
figw, figh = 150.0, 75.0
fig = plt.figure(figsize=(figw/25.4, figh/25.4))
ax1 = fig.add_axes([2.5/figw, 2.5/figh, 60.0/figw, 1-5.0/figh], projection=utm)
ax2 = fig.add_axes([75.0/figw, 10.0/figh, 72.5/figw, 1-12.5/figh])


# Map axes
# --------

ax = ax1

# initialize figure
ax.set_rasterization_zorder(2.5)
ax.set_extent(reg, crs=utm)

# plot image data
filename = '../data/external/S2A_20160808_175915_456_RGB.jpg'
data, extent = ut.io.open_gtif(filename)
data = np.moveaxis(data, 0, 2)
ax.imshow(data, extent=extent, transform=utm, cmap='Blues')

# plot borehole locations
for bh, c in zip(ut.bowtem_bhnames, ut.bowtem_colours):
    for y in ['14', '16', '17']:
        ut.pl.add_waypoint('B'+y+bh.upper(), text='20'+y, ax=ax, color=c,
                           marker='o', textpos=('lr' if bh == 'bh1' else 'ul'))

# plot camp location
ut.pl.add_waypoint('Tent Swiss', text='Camp', ax=ax, color='C3',
                    marker='^', textpos='lc')

# add scale
ax.plot([508.25e3, 509.25e3], [8620.25e3]*2, 'w|-')
ax.text(508.75e3, 8620.4e3, '1km', color='w', ha='center', fontweight='bold')


# Distance axes
# -------------

ax = ax2

# borehole plot properties
distdict = dict(bh1=2.015, bh2=1.985, bh3=1.85)
markdict = dict(zip(ut.bowtem_sensors, ut.bowtem_markers))
xoffdict = dict(zip(ut.bowtem_sensors, [0.01, -0.01, -0.01]))

# loop on boreholes
for bh, c in zip(ut.bowtem_bhnames, ut.bowtem_colours):
    t, z, b = ut.io.load_bowtem_data(bh)
    d = distdict[bh]
    for u in z.index:
        m = markdict[u[1]]
        x = xoffdict[u[1]]
        ax.plot(d+1*x, z[u], c=c, marker=m, ls='', label='')
        ax.text(d+2*x, z[u], u,
                ha=('left' if x>0 else 'right'),
                va=('bottom' if u in ('LP') else
                    'top' if u in ('LT01', 'UT01') else
                    'center'))
    ax.plot([d, d], [b, 0.0], 'k-_')
    ax.text(d, -5.0, bh.upper(), ha='center', va='bottom')
    ax.text(d, b+5.0, '%d m' % b, ha='center', va='top')

# add flow direction arrow
ax.text(0.9, 0.55, 'ice flow', ha='center', transform=ax.transAxes)
ax.annotate('', xy=(0.85, 0.5), xytext=(0.95, 0.5),
            xycoords=ax.transAxes, textcoords=ax.transAxes,
            arrowprops=dict(arrowstyle='->',  lw=1.0))

# add standalone legend
ax.legend([plt.Line2D([], [], ls='none', marker=m) for m in ut.bowtem_markers],
          ['Inclinometers', 'Thermistors', 'Piezometres'],
          bbox_to_anchor=(1.0, 0.95))

# set axes properties
ax.set_xlim(1.75, 2.15)
ax.set_ylim(292.0, -20.0)
ax.set_xticks([1.85, 2.0])
ax.set_xlabel('approximate distance from front in 2014 (km)')
ax.set_ylabel('depth (m)')

# save
ut.pl.savefig(fig)
