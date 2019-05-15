#!/usr/bin/env python

import util as ut
import numpy as np
import scipy.interpolate as sinterp
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import cartopy.crs as ccrs
import gpxpy


# Arctic DEM strip
strp = 'SETSM_WV01_20140906_10200100318E9F00_1020010033454500_seg2_2m_v2.0'
strp = 'SETSM_WV01_20140906_10200100318E9F00_1020010033454500_seg4_2m_v3.0',
date = '2014-09-06 17:30:00'


# Initialize figure
# -----------------

# projections and map boundaries
ll = ccrs.PlateCarree()
utm = ccrs.UTM(19)
ste = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                         true_scale_latitude=70.0)
utmreg = 510400, 510700, 8623700, 8624050  # axes extent 300x350 m
stereg = -535100, -534700, -1227100, -1226600  # Arctic DEM crop region

# initialize figure
figw, figh = 150.0, 75.0
fig = plt.figure(figsize=(figw/25.4, figh/25.4))
ax1 = fig.add_axes([2.5/figw, 2.5/figh, 60.0/figw, 1-5.0/figh], projection=utm)
ax2 = fig.add_axes([75.0/figw, 10.0/figh, 72.5/figw, 1-12.5/figh])


# Map axes
# --------

ax = ax1

# prepare axes
ax.set_rasterization_zorder(2.5)
ax.set_extent(utmreg, crs=utm)

# relief shading colormap
cols = [(0.0, (1,1,1,1)), (0.5, (1,1,1,0)), (0.5, (0,0,0,0)), (1.0, (0,0,0,1))]
smap = LinearSegmentedColormap.from_list('shades', cols)

# load elevation data
z, extent = ut.io.open_gtif('../data/external/%s.tif' % strp, extent=stereg)
z = np.ma.masked_equal(z, -9999.0)

# plot elevation map
im = ax.imshow(z, extent=extent, cmap='Blues_r',
               transform=ste, interpolation='bilinear')

# plot shadows
s = sum(ut.pl.shading(z, extent=extent, altitude=30.0, transparent=True,
                      azimuth=a) for a in [240.0, 270.0, 300.0])/3.0
#s = ut.pl.shading(z, extent=extent, altitude=30.0, azimuth=270.0, transparent=True)
ax.imshow(s, extent=extent, cmap=smap, vmin=-1.0, vmax=1.0,
          transform=ste, interpolation='bilinear')

# plot contours
levs = np.arange(70.0, 100.0, 1.0)
cs = ax.contour(z, levels=levs[(levs % 5 != 0)], extent=extent,
                colors='k', linewidths=0.1, alpha=0.75, transform=ste)
cs = ax.contour(z, levels=levs[(levs % 5 == 0)], extent=extent,
                colors='k', linewidths=0.25, alpha=0.75, transform=ste)
cs.clabel(fmt='%d')

# open continuous gps data
#ax.plot(x, y, 'k+', transform=utm)

# open waypoints dictionary
with open('../data/locations.gpx', 'r') as gpx_file:
    pts = {wpt.name: wpt for wpt in gpxpy.parse(gpx_file).waypoints}

# open dgps location at DEM time
dgps = ut.io.load_data('dgps', 'velocity', 'upper').interpolate().loc[date]

# for each borehole
xy = dict()
for bh, c in zip(ut.bowtem_bhnames, ut.bowtem_colours):

    # get init coords in UTM
    wpt = pts['B14'+bh.upper()]
    xy0 = utm.transform_point(wpt.longitude, wpt.latitude, ll)

    # if bh1, compute and plot displacement
    if bh == 'bh1':
        xy1 = dgps[['x', 'y']].values
        dxy = xy1 - xy0
        ax.annotate('', xy=xy1, xytext=xy0,
                    arrowprops=dict(arrowstyle='->', color='0.25'))

    # plot locations
    ax.plot(*xy0, color='0.25', marker='+')
    ax.plot(*xy0+dxy, color=c, marker='+')

    # add uncertainty circles
    if bh != 'bh1':
        ax.add_patch(plt.Circle(xy0+dxy, radius=10.0, fc='w', ec=c, alpha=0.5))

    # add text label
    ax.text(*xy0+dxy+np.array([10, 0]), s=bh.upper(), color=c,
            ha='left', va='center', fontweight='bold')

    # save coords for profile
    xy[bh] = xy0+dxy

# add scale
w, e, s, n = ax.get_extent()
bar, pad = 100.0, 25.0
ax.plot([e-pad-bar, e-pad], [s+pad]*2, 'k|-')
ax.text(e-pad-0.5*bar, s+1.2*pad, '100m', ha='center', fontweight='bold')


# Distance axes
# -------------

ax = ax2

# profile start and end points
x3, y3 = ste.transform_point(*xy['bh3'], src_crs=utm)
x1, y1 = ste.transform_point(*xy['bh1'], src_crs=utm)

# coords to sample at
xp = np.linspace(2*x3-x1, 2*x1-x3, 101)
yp = np.linspace(2*y3-y1, 2*y1-y3, 101)

# coordinates for Arctic DEM
x, y = ut.pl.coords_from_extent(extent, *z.shape[::-1])

# compute distance along profile
dp = ((xp-xp[0])**2+(yp-yp[0])**2)**0.5
d3 = ((x3-xp[0])**2+(y3-yp[0])**2)**0.5
d1 = ((x1-xp[0])**2+(y1-yp[0])**2)**0.5

# interpolate DEM along profile
zp = sinterp.interpn((y[::-1], x), z[::-1], (yp, xp), method='linear', bounds_error=False)

# plot topographic profile
ax.plot(dp, zp, color='0.25')

# mark borehole locations
ax.axvline(d1, c=ut.bowtem_colours[0])
ax.axvline(d3, c=ut.bowtem_colours[2])
ax.text(d1+10.0, 76.0, 'BH1', color=ut.bowtem_colours[0], fontweight='bold')
ax.text(d3+10.0, 76.0, 'BH3', color=ut.bowtem_colours[2], fontweight='bold')

# set axes properties
ax.set_xlabel('distance along flow (m)')
ax.set_ylabel('surface elevation (m)')

# save
ut.pl.savefig(fig)
