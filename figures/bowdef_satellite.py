#!/usr/bin/env python
# Copyright (c) 2016-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin April and June strain rates from Landsat images."""


import absplots as apl
import matplotlib as mpl
import pandas as pd

import bowdef_utils
import bowtem_utils


def compute_monthly_average(ds, month):
    """Average pairs within a month excluding poorly covered pixels."""

    # select monthly data
    ds = ds[['u', 'v']].sel(time=month)

    # compute average excluding pixels with less than half coverage
    # (mostly beyond the calving front and along the glacier margins)
    mean = ds.mean('time').where(ds.u.notnull().mean('time') >= 0.5)

    # return monthly average and number of pairs
    return mean.assign_attrs(pairs=ds.sizes['time'])


def compute_effective_strain_rate(u, v):
    """Compute effective strain rate from velocity components."""

    # compute velocity gradients
    du_dx = u.differentiate('x')
    du_dy = u.differentiate('y')
    dv_dx = v.differentiate('x')
    dv_dy = v.differentiate('y')

    # return effective strain rate
    return (2*(du_dx**2+dv_dy**2)+(du_dy+dv_dx)**2)**0.5


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(150, 90), ncols=2, sharex=True, sharey=True, gridspec_kw={
            'left': 2.5, 'bottom': 2.5, 'right': 25, 'top': 2.5,
            'wspace': 2.5})
    cax = fig.add_axes_mm([127.5, 2.5, 5, 85])

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes=axes, colors='w')

    # open landsat pairs
    ds = bowdef_utils.open_landsat_pairs()

    # plot effective strain rates at lowest and highest velocities
    for ax, month in zip(axes, ['2015-04', '2015-06']):
        label = pd.to_datetime(month).strftime('%B %Y')
        mean = compute_monthly_average(ds, month)
        eff = compute_effective_strain_rate(mean.u, mean.v)
        bowtem_utils.plot_bowdoin_map(ax, boreholes=[], season='summer')
        eff.plot.imshow(
            ax=ax, add_labels=False, alpha=0.75, cbar_ax=cax,
            cmap='Reds', extend='both', norm=mpl.colors.LogNorm(10**-1.5, 1))
        bowdef_utils.plot_velocity_quiver(ax, mean)

        # plot borehole locations interpolated to the monthly average
        _, projected = bowtem_utils.project_borehole_locations(
            month, crs='+proj=utm +zone=19')
        for bh, point in zip(['bh1', 'bh3'], ['se', 'nw']):
            ax.plot(*projected.loc[bh], color='1', marker='o')
            bowtem_utils.annotate_by_compass(
                bh.upper(), ax=ax, color='w', fontweight='bold',
                xy=projected.loc[bh], point=point)

        bowtem_utils.add_subfig_label(
            f'{label}\n{mean.pairs} pairs', ax=ax, color='w', loc='sw')

    # set axes properties
    for ax in axes:
        ax.set_aspect('equal')
        ax.set_title('')
    cax.set_ylabel(r'effective strain rate ($a^{-1}$)')
    cax.yaxis.set_minor_locator(mpl.ticker.NullLocator())
    cax.yaxis.set_major_locator(mpl.ticker.LogLocator(base=10**0.5))
    cax.yaxis.set_major_formatter('{x:.1g}')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
