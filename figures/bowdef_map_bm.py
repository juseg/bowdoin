#!/usr/bin/env python2

import util as ut
import numpy as np
import netCDF4 as nc4
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs


# projections and map boundaries
ll = ccrs.PlateCarree()
utm = ccrs.UTM(19)
ste = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                         true_scale_latitude=70.0)

# initialize figure
figw, figh = 175.0, 125.0
fig = plt.figure(0, (figw/25.4, figh/25.4))
ax = fig.add_axes([0, 0, 1, 1], projection=ste)
cax = fig.add_axes([5.0/figw, 1-10.0/figh, 50.0/figw, 5.0/figh])
ax.set_rasterization_zorder(2.5)
ax.outline_patch.set_linewidth(2.0)

# read topo data
filename = ('/scratch_net/iceberg_second/juliens/geodata/icesheets/'
            'greenland-bedmachine/BedMachineGreenland-2017-09-20.nc')
ds = nc4.Dataset(filename)
imin, imax = 500, 850
jmin, jmax = 3875, 4125
x = ds.variables['x'][imin:imax]
y = ds.variables['y'][jmin:jmax]
b = ds.variables['bed'][jmin:jmax, imin:imax]
h = ds.variables['thickness'][jmin:jmax, imin:imax]
s = ds.variables['surface'][jmin:jmax, imin:imax]
ds.close()
extent = ut.pl.extent_from_coords(x, y[::-1])

# shades colormap
cmap = mcolors.LinearSegmentedColormap.from_list('shades', [(0.0, (0,0,0,0)), (1.0, (0,0,0,1))])

# plot shaded relief
shade = ut.pl.shading(b, extent=extent, transparent=True)
ax.imshow(b[::-1], extent=extent, cmap='Greys', vmin=-3e3, vmax=3e3)
ax.imshow(shade[::-1], extent=extent, cmap=cmap, vmin=0.0, vmax=1.0)

# plot contours
levs = np.arange(-1000.0, 1200.0, 20.0)
cs = ax.contour(x, y, b, levels=levs[(levs % 100 != 0)],
                colors='k', linewidths=0.1)
cs = ax.contour(x, y, b, levels=levs[(levs % 100 == 0)],
                colors='k', linewidths=0.25)
cs.clabel(fmt='%d')
cs = ax.contourf(x, y, b, levels=[-1000.0, 0.0], colors='w', alpha=0.25)

# plot ice thickness
h = np.ma.masked_equal(h, 0.0)
im = ax.imshow(h[::-1], extent=extent, vmin=0.0, vmax=3e2, cmap='Blues', alpha=0.75)
ax.contour(h[::-1].mask, extent=extent, levels=[0.5], colors='k', linewidths=0.5)
ax.set_extent(extent, crs=ax.projection)

# add colorbar
cb = fig.colorbar(im, cax, extend='max', orientation='horizontal')
cb.set_label('ice thickness (m)')

# plot waypoints
kwa = dict(ax=ax, color='k', marker='o', offset=15,
           bbox=dict(boxstyle='square,pad=0.5', fc='w'))
ut.pl.add_waypoint('Qaanaaq', text='Qaanaaq', textpos='cl', **kwa)
ut.pl.add_waypoint('Tent Swiss', text='Camp', textpos='cr', **kwa)

# save
ut.pl.savefig(fig)
