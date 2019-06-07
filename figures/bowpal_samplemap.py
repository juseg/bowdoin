#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin paleo sample map."""

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import absplots as apl
import cartowik.annotations as can
import util


def mark_inset(ax0, ax1, text='', **kwargs):
    """Custom method to mark inset on geoaxes."""
    west, east, south, north = ax1.get_extent()
    rectangle = plt.Rectangle((west, north), east-west, south-north, **kwargs)
    ax0.add_patch(rectangle)
    ax0.text(west, north+100, text, fontweight='bold')


def annotate_sample(location,
                    text='{location.name:s}\n{location.elevation:.0f} m',
                    **kwargs):
    """Annotate a sample and label with name and altitude."""
    color = dict(bedrock='C0', boulder='C3', organic='k')[location.type]
    marker = dict(bedrock='s', boulder='o', organic='^')[location.type]
    return can.annotate_location(location, color=color, marker=marker,
                                 bbox=dict(ec=color, fc='w', pad=2),
                                 offset=12, text=text, **kwargs)


def main():
    """Main program called during execution."""

    # regions extents and axes position in figure
    # FIXME: Implement add_axes_mm / add_subplot_mm for unique subplots.
    figw, figh = 175, 150
    subregions = {
        '(a) Bowdoin Glacier':     (503750, 516250, 8619000, 8629000),
        '(b) Sentinel hill':       (505000, 506500, 8621350, 8622350),
        '(c) Bartlett hill':       (509000, 513000, 8620000, 8622000),
        '(d) Upper cam. hill':     (511350, 512350, 8623000, 8624300),
        '(e) East Branch moraine': (514250, 515250, 8625100, 8625800)}
    axposition = {
        '(a) Bowdoin Glacier':     [0/figw, 50/figh, 125/figw, 100/figh],
        '(b) Sentinel hill':       [0/figw, 0/figh, 75/figw, 50/figh],
        '(c) Bartlett hill':       [75/figw, 0/figh, 100/figw, 50/figh],
        '(d) Upper cam. hill':     [125/figw, 50/figh, 50/figw, 65/figh],
        '(e) East Branch moraine': [125/figw, 115/figh, 50/figw, 35/figh]}

    # read sample locations and background image
    locs = util.geo.read_locations('../data/locations.gpx')
    img = xr.open_rasterio('../data/external/20160410_180125_659_S2A_RGB.jpg')

    # initialize figure
    fig = apl.figure_mm(figsize=(figw, figh))
    proj = ccrs.UTM(19)
    grid = dict()

    # for each region
    for region, extent in subregions.items():

        # add axes
        ax = grid[region] = fig.add_axes(axposition[region], projection=proj)
        ax.set_extent(extent, crs=ax.projection)
        ax.outline_patch.set_linewidth(2.0)
        ax.outline_patch.set_edgecolor('k')

        # add subfigure label and mark inset
        util.com.add_subfig_label(region, ax=ax)
        mark_inset(ax0=fig.axes[0], ax1=ax, text=region[:3], fc='none', ec='k')

        # plot Sentinel image
        img.plot.imshow(ax=ax)

    # plot all sample locations on the main panel
    ax = grid['(a) Bowdoin Glacier']
    for name, loc in locs.items():
        if name.startswith('BOW1'):
            annotate_sample(loc, ax=ax, text='')

    # plot Sentinel hill sample locations
    ax = grid['(b) Sentinel hill']
    annotate_sample(locs['BOW16-MF-BED1'], ax=ax, point='nw')
    annotate_sample(locs['BOW16-MF-BED2'], ax=ax, point='se')
    annotate_sample(locs['BOW16-MF-BED3'], ax=ax, point='sw')
    annotate_sample(locs['BOW16-MF-BOU1'], ax=ax, point='sw')
    annotate_sample(locs['BOW16-MF-BOU2'], ax=ax, point='e')
    annotate_sample(locs['BOW16-MF-BOU3'], ax=ax, point='ne')

    # plot Bartlett hill sample locations
    ax = grid['(c) Bartlett hill']
    annotate_sample(locs['BOW15-01'], ax=ax, point='ne')
    annotate_sample(locs['BOW15-02'], ax=ax, point='e')
    annotate_sample(locs['BOW15-03'], ax=ax, point='w')
    annotate_sample(locs['BOW15-04'], ax=ax, point='ne')
    annotate_sample(locs['BOW15-05'], ax=ax, point='nw')
    annotate_sample(locs['BOW15-06'], ax=ax, point='e')
    annotate_sample(locs['BOW15-07'], ax=ax, point='se')
    annotate_sample(locs['BOW15-08'], ax=ax, point='sw')
    annotate_sample(locs['BOW15-09'], ax=ax, point='w')
    annotate_sample(locs['BOW16-JS-12'], ax=ax, point='w')
    annotate_sample(locs['BOW16-JS-13'], ax=ax, point='nw')

    # plot Camp carbon sample locations
    ax = grid['(d) Upper cam. hill']
    annotate_sample(locs['BOW16-CA-02'], ax=ax, point='se')
    annotate_sample(locs['BOW16-CA-03'], ax=ax, point='e')
    annotate_sample(locs['BOW16-CA-04'], ax=ax, point='ne')

    # plot Upper cam hill sample locations
    annotate_sample(locs['BOW16-JS-01'], ax=ax, point='e')
    annotate_sample(locs['BOW16-JS-02'], ax=ax, point='w')
    annotate_sample(locs['BOW16-JS-03'], ax=ax, point='sw')
    annotate_sample(locs['BOW16-JS-04'], ax=ax, point='nw')
    annotate_sample(locs['BOW16-JS-05'], ax=ax, point='ne')
    annotate_sample(locs['BOW16-JS-06'], ax=ax, point='se')

    # plot East Branch moraine sample locations
    ax = grid['(e) East Branch moraine']
    annotate_sample(locs['BOW16-JS-07'], ax=ax, point='e')
    annotate_sample(locs['BOW16-JS-08'], ax=ax, point='se')
    annotate_sample(locs['BOW16-JS-09'], ax=ax, point='sw')
    annotate_sample(locs['BOW16-JS-10'], ax=ax, point='nw')
    annotate_sample(locs['BOW16-JS-11'], ax=ax, point='ne')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
