#!/usr/bin/env python

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import gpxpy
import util

# from mpl_toolkits.axes_grid1.inset_locator import mark_inset


def waypoint_scatter(names, ax=None, text=True, textloc='ur', offset=15,
                     alpha=1.0, **kwargs):
    """Draw annotated scatter plot from GPX waypoints."""

    # get current axes if None given
    ax = ax or plt.gca()

    # initialize coordinate lists
    xlist = []
    ylist = []

    # expand textpos to a list
    if isinstance(textloc, str):
        textloc = [textloc] * len(names)

    # GPX usually uses geographic coordinates
    crs = ccrs.PlateCarree()

    # open GPX file
    with open('../data/locations.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

        # find the right waypoints
        for wpt in gpx.waypoints:
            if wpt.name in names:

                # extract point coordinates
                proj = ax.projection
                coords = proj.transform_point(wpt.longitude, wpt.latitude, crs)
                xlist.append(coords[0])
                ylist.append(coords[1])

                # stop here if text is unwanted
                if text is False:
                    continue

                # add annotation
                text = '%s\n%.0f m' % (wpt.name, wpt.elevation)
                loc = textloc[names.index(wpt.name)]
                xshift = ((loc[1] == 'r')-(loc[1] == 'l'))
                xoffset = xshift * offset
                yshift = ((loc[0] == 'u')-(loc[0] == 'l'))
                yoffset = yshift * offset
                relpos = (0.5*(1-xshift), 0.5*(1-yshift))
                halign = {'r': 'left', 'l': 'right', 'c': 'center'}[loc[1]]
                valign = {'u': 'bottom', 'l': 'top', 'c': 'center'}[loc[0]]
                xytext = xoffset, yoffset
                ax.annotate(text, xy=coords, xytext=xytext,
                            textcoords='offset points', ha=halign, va=valign,
                            bbox=dict(boxstyle='square,pad=0.5', fc='w'),
                            arrowprops=dict(arrowstyle='->', color='k',
                                            relpos=relpos, alpha=alpha))

    # add scatter plot
    ax.scatter(xlist, ylist, alpha=alpha, **kwargs)


if __name__ == '__main__':

    # geographic projections
    ll = ccrs.PlateCarree()
    utm = ccrs.UTM(19)
    limits = [[505.5e3, 513.5e3, 8619.5e3, 8625.5e3]] * 5

    # regions w, e, s, n
    regions = [
        (503750, 516250, 8619000, 8629000),  # Bowdoin 12.5x10.0 km
        (505000, 506500, 8621350, 8622350),  # Sentinel nunatak 1.5x1.0
        (509000, 513000, 8620000, 8622000),  # Bartlett hill 4.0x2.0
        (511350, 512350, 8623000, 8624300),  # Upper cam hill 1.0x1.3
        (514250, 515250, 8625100, 8625800)]  # East arm moraine 1.0x0.7

    # initialize figure
    figw, figh = 175.0, 150.0
    fig = plt.figure(0, (figw/25.4, figh/25.4))
    frames = [[0.0/figw, 50.0/figh, 125.0/figw, 100.0/figh],
              [0.0/figw, 0.0/figh, 75.0/figw, 50.0/figh],
              [75.0/figw, 0.0/figh, 100.0/figw, 50.0/figh],
              [125.0/figw, 50.0/figh, 50.0/figw, 65.0/figh],
              [125.0/figw, 115.0/figh, 50.0/figw, 35.0/figh]]
    grid = [fig.add_axes(rect, projection=utm) for rect in frames]
    for ax, reg in zip(grid, regions):
        ax.set_extent(reg, crs=utm)
        ax.outline_patch.set_linewidth(2.0)
        ax.outline_patch.set_edgecolor('k')

#    # mark inset locations
#    kwa = dict(fc='none', ec='k', lw=1.0, alpha=0.75)
#    mark_inset(grid[0], grid[1], loc1='none', loc2='none', **kwa)
#    mark_inset(grid[0], grid[2], loc1=1, loc2=3, **kwa)
#    mark_inset(grid[0], grid[3], loc1=2, loc2=3, **kwa)
#    mark_inset(grid[0], grid[4], loc1=2, loc2=4, **kwa)

    # add subfigure labels
    for reg, label in zip(regions[1:], list('bcde')):
        w, e, s, n = reg
        rect = plt.Rectangle((w, n), (e-w), (s-n), fc='none', ec='k')
        grid[0].add_patch(rect)
        grid[0].text(w, n+100, '(%s)' % label, fontweight='bold')
    util.com.add_subfig_label('(a) Bowdoin Glacier', ax=grid[0])
    util.com.add_subfig_label('(b) Sentinel hill', ax=grid[1])
    util.com.add_subfig_label('(c) Bartlett hill', ax=grid[2])
    util.com.add_subfig_label('(d) Upper cam. hill', ax=grid[3])
    util.com.add_subfig_label('(e) East Branch moraine', ax=grid[4])

    # plot S2A image
    img = xr.open_rasterio('../data/external/20160410_180125_659_S2A_RGB.jpg')
    for ax in grid:
        img.plot.imshow(ax=ax)

    # plot all sample locations on main panel
    comkwa = dict(s=40, alpha=0.5)
    bedkwa = dict(marker='s', c='C0', **comkwa)
    boukwa = dict(marker='o', c='C3', **comkwa)
    carkwa = dict(marker='^', c='w', **comkwa)
    waypoint_scatter(['BOW16-JS-%02d' % i for i in range(1, 4)] +
                     ['BOW16-MF-BED%d' % i for i in range(1, 4)],
                     ax=grid[0], text=False, **bedkwa)
    waypoint_scatter(['BOW15-%02d' % i for i in range(1, 10)] +
                     ['BOW16-JS-%02d' % i for i in range(4, 14)] +
                     ['BOW16-MF-BOU%d' % i for i in range(1, 4)],
                     ax=grid[0], text=False, **boukwa)
    waypoint_scatter(['BOW16-CA-%02d' % i for i in range(2, 5)],
                     ax=grid[0], text=False, **carkwa)

    # plot Sentinel hill sample locations
    waypoint_scatter(['BOW16-MF-BED%d' % i for i in range(1, 4)],
                     textloc=['ul', 'lr', 'll'],
                     ax=grid[1], **bedkwa)
    waypoint_scatter(['BOW16-MF-BOU%d' % i for i in range(1, 4)],
                     textloc=['ll', 'cr', 'ur'],
                     ax=grid[1], **boukwa)

    # plot Bartlett hill sample locations
    waypoint_scatter(['BOW15-%02d' % i for i in range(1, 10)] +
                     ['BOW16-JS-%02d' % i for i in (12, 13)],
                     textloc=['ur', 'cr', 'cl', 'ur', 'ul', 'cr', 'lr',
                              'll', 'cl', 'cl', 'ul'],
                     ax=grid[2], **boukwa)

    # plot Camp carbon sample locations
    waypoint_scatter(['BOW16-CA-%02d' % i for i in range(2, 5)],
                     textloc=['lr', 'cr', 'ur'],
                     ax=grid[3], **carkwa)

    # plot Upper cam hill sample locations
    waypoint_scatter(['BOW16-JS-%02d' % i for i in range(1, 4)],
                     textloc=['cr', 'cl', 'll'],
                     ax=grid[3], **bedkwa)
    waypoint_scatter(['BOW16-JS-%02d' % i for i in range(4, 7)],
                     textloc=['ul', 'ur', 'lr'],
                     ax=grid[3], **boukwa)

    # plot East Branch moraine sample locations
    waypoint_scatter(['BOW16-JS-%02d' % i for i in range(7, 12)],
                     textloc=['cr', 'lr', 'll', 'ul', 'ur'],
                     ax=grid[4], **boukwa)

    # save
    util.com.savefig(fig)
