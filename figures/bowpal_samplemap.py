#!/usr/bin/env python

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import gpxpy
import cartowik.annotations as can
import util

# from mpl_toolkits.axes_grid1.inset_locator import mark_inset


def waypoint_scatter(locations, **kwargs):
    """Draw annotated scatter plot from GPX waypoints."""
    for loc in locations:
        can.annotate_location(loc, text=' ', **kwargs)


def annotate_sample(location, **kwargs):
    """Annotate a sample and label with name and altitude."""
    text = '{:s}\n{:.0f} m'.format(location.name, location.elevation)
    can.annotate_location(location, text=text, **kwargs)


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

    # read sample locations
    locs = util.geo.read_locations('../data/locations.gpx')

    # plot all sample locations on main panel
    bedkwa = dict(marker='s', color='C0')
    boukwa = dict(marker='o', color='C3')
    carkwa = dict(marker='^', color='k')
    waypoint_scatter([locs['BOW16-JS-%02d' % i] for i in range(1, 4)] +
                     [locs['BOW16-MF-BED%d' % i] for i in range(1, 4)],
                     ax=grid[0], **bedkwa)
    waypoint_scatter([locs['BOW15-%02d' % i] for i in range(1, 10)] +
                     [locs['BOW16-JS-%02d' % i] for i in range(4, 14)] +
                     [locs['BOW16-MF-BOU%d' % i] for i in range(1, 4)],
                     ax=grid[0], **boukwa)
    waypoint_scatter([locs['BOW16-CA-%02d' % i] for i in range(2, 5)],
                     ax=grid[0], **carkwa)

    # plot Sentinel hill sample locations
    ax = grid[1]
    annotate_sample(locs['BOW16-MF-BED1'], ax=ax, point='nw', **bedkwa)
    annotate_sample(locs['BOW16-MF-BED2'], ax=ax, point='se', **bedkwa)
    annotate_sample(locs['BOW16-MF-BED3'], ax=ax, point='sw', **bedkwa)
    annotate_sample(locs['BOW16-MF-BOU1'], ax=ax, point='sw', **boukwa)
    annotate_sample(locs['BOW16-MF-BOU2'], ax=ax, point='e', **boukwa)
    annotate_sample(locs['BOW16-MF-BOU3'], ax=ax, point='ne', **boukwa)

    # plot Bartlett hill sample locations
    ax = grid[2]
    annotate_sample(locs['BOW15-01'], ax=ax, point='ne', **boukwa)
    annotate_sample(locs['BOW15-02'], ax=ax, point='e', **boukwa)
    annotate_sample(locs['BOW15-03'], ax=ax, point='w', **boukwa)
    annotate_sample(locs['BOW15-04'], ax=ax, point='ne', **boukwa)
    annotate_sample(locs['BOW15-05'], ax=ax, point='nw', **boukwa)
    annotate_sample(locs['BOW15-06'], ax=ax, point='e', **boukwa)
    annotate_sample(locs['BOW15-07'], ax=ax, point='se', **boukwa)
    annotate_sample(locs['BOW15-08'], ax=ax, point='sw', **boukwa)
    annotate_sample(locs['BOW15-09'], ax=ax, point='w', **boukwa)
    annotate_sample(locs['BOW16-JS-12'], ax=ax, point='w', **boukwa)
    annotate_sample(locs['BOW16-JS-13'], ax=ax, point='nw', **boukwa)

    # plot Camp carbon sample locations
    ax = grid[3]
    annotate_sample(locs['BOW16-CA-02'], ax=ax, point='se', **carkwa)
    annotate_sample(locs['BOW16-CA-03'], ax=ax, point='e', **carkwa)
    annotate_sample(locs['BOW16-CA-04'], ax=ax, point='ne', **carkwa)

    # plot Upper cam hill sample locations
    annotate_sample(locs['BOW16-JS-01'], ax=ax, point='e', **bedkwa)
    annotate_sample(locs['BOW16-JS-02'], ax=ax, point='w', **bedkwa)
    annotate_sample(locs['BOW16-JS-03'], ax=ax, point='sw', **bedkwa)
    annotate_sample(locs['BOW16-JS-04'], ax=ax, point='nw', **boukwa)
    annotate_sample(locs['BOW16-JS-05'], ax=ax, point='ne', **boukwa)
    annotate_sample(locs['BOW16-JS-06'], ax=ax, point='se', **boukwa)

    # plot East Branch moraine sample locations
    ax = grid[4]
    annotate_sample(locs['BOW16-JS-07'], ax=ax, point='e', **boukwa)
    annotate_sample(locs['BOW16-JS-08'], ax=ax, point='se', **boukwa)
    annotate_sample(locs['BOW16-JS-09'], ax=ax, point='sw', **boukwa)
    annotate_sample(locs['BOW16-JS-10'], ax=ax, point='nw', **boukwa)
    annotate_sample(locs['BOW16-JS-11'], ax=ax, point='ne', **boukwa)

    # save
    util.com.savefig(fig)
