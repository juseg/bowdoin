# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin geographic utils.
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import gpxpy


# Plotting methods
# ----------------

def add_scale_bar(ax=None, length=1000, pad=None, label=None, color='k'):
    """Add a bar showing map scale."""
    # FIXME: Move this scale bar method to Cartowik?
    ax = ax or plt.gca()
    pad = pad or 0.25*length
    west, east, south, north = ax.get_extent()
    ax.plot([east-pad-length, east-pad], [south+pad]*2, c=color, marker='|')
    ax.text(east-pad-0.5*length, south+pad, label+'\n',
            color=color, fontweight='bold', ha='center', va='center')


def add_waypoint(name, ax=None, color=None, marker='o', text=None,
                 textpos='ul', offset=8, **kwargs):
    """Plot and annotate waypoint from GPX file"""
    # FIXME: Move the GPX interface to Cartowik?

    # read waypoint from GPX file
    with open('../data/locations.gpx', 'r') as gpx_file:
        locations = {wpt.name: wpt for wpt in gpxpy.parse(gpx_file).waypoints}
    wpt = locations[name]

    # process arguments
    ax = ax or plt.gca()
    crs = ccrs.PlateCarree()
    text = text or wpt.name
    yloc, xloc = textpos

    # plot annotated waypoint
    ax.plot(wpt.longitude, wpt.latitude, c=color, marker=marker, transform=crs)
    ax.annotate(text, xy=(wpt.longitude, wpt.latitude),
                xytext=({'l': -1, 'c': 0, 'r': 1}[xloc]*offset,
                        {'l': -1, 'c': 0, 'u': 1}[yloc]*offset),
                xycoords=crs._as_mpl_transform(ax), textcoords='offset points',
                ha={'l': 'right', 'c': 'center', 'r': 'left'}[xloc],
                va={'l': 'top', 'c': 'center', 'u': 'bottom'}[yloc],
                arrowprops=dict(arrowstyle='->', color=color,
                                relpos=({'l': 1, 'c': 0.5, 'r': 0}[xloc],
                                        {'l': 1, 'c': 0.5, 'u': 0}[yloc])),
                bbox=dict(pad=0, ec='none', fc='none'), color=color,
                fontweight='bold', **kwargs)


def waypoint_scatter(names, ax=None, text=True, textloc='ur', offset=15,
                     alpha=1.0, **kwargs):
    """Draw annotated scatter plot from GPX waypoints."""

    # get current axes if None given
    ax = ax or plt.gca()

    # initialize coordinate lists
    xlist = []
    ylist = []

    # expand textpos to a list
    if type(textloc) is str:
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
                xy = proj.transform_point(wpt.longitude, wpt.latitude, crs)
                x, y = xy
                xlist.append(x)
                ylist.append(y)

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
                ha = {'r': 'left', 'l': 'right', 'c': 'center'}[loc[1]]
                va = {'u': 'bottom', 'l': 'top', 'c': 'center'}[loc[0]]
                xytext = xoffset, yoffset
                ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va=va,
                            textcoords='offset points',
                            bbox=dict(boxstyle='square,pad=0.5', fc='w'),
                            arrowprops=dict(arrowstyle='->', color='k',
                                            relpos=relpos, alpha=alpha))

    # add scatter plot
    ax.scatter(xlist, ylist, alpha=alpha, **kwargs)
