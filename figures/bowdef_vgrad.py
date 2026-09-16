#!/usr/bin/env python
# Copyright (c) 2016-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin velocity gradient from Landsat images."""


import matplotlib.pyplot as plt
import xarray as xr

import bowtem_utils


def main():
    """Main program called during execution."""

    # projections and map boundaries
    fig = plt.figure(figsize=(60/25.4, 60/25.4))
    ax = fig.add_axes([0, 0, 1, 1])

    # plot image data
    bowtem_utils.plot_bowdoin_map(
        fig.axes[0], boreholes=['bh1', 'bh3'],
        colors=['tab:blue', 'tab:pink'], season='summer')

    # plot velocity contours
    prefix = '../data/satellite/bowdoin-landsat-uv/16072015_17082015_161111_1117'
    u = xr.open_dataarray(prefix+'_f_u.nc').squeeze().where(lambda x: x!=65535)
    v = xr.open_dataarray(prefix+'_f_v.nc').squeeze().where(lambda x: x!=65535)
    img = (u**2+v**2)**0.5

    # img = (img.differentiate('x')**2 + img.differentiate('y')**2)**0.5
    # img.plot.imshow(ax=ax, add_labels=False, alpha=0.75, cmap='Reds')
    img.plot.contour(ax=ax, add_labels=False, alpha=0.75, cmap='Reds')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
