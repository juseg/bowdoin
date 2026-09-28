#!/usr/bin/env python
# Copyright (c) 2016-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin spring and summer strain rates from Landsat images."""


import absplots as apl
import matplotlib.colors as mcolors
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

    # to compute rotated strain rates instead
    # epp = (u**2*du_dx+u*v*(du_dy+dv_dx)+v**2*dv_dy) / (u**2+v**2)
    # eoo = (v**2*du_dx-u*v*(du_dy+dv_dx)+ u**2*dv_dy) / (u**2+v**2)
    # epo = (u*v*(dv_dy-du_dx)+0.5*(u**2-v**2)*(du_dy+dv_dx)) / (u**2+v**2)

    # return effective strain rate
    return (2*(du_dx**2+dv_dy**2)+(du_dy+dv_dx)**2)**0.5


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 90), ncols=2, sharex=True, sharey=True, gridspec_kw={
            'left': 2.5, 'bottom': 2.5, 'right': 23, 'top': 2.5, 'wspace': 2.5})
    cax = fig.add_axes_mm([159.5, 2.5, 4, 85])

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
            cmap='Reds', extend='both', norm=mcolors.LogNorm(0.03, 1))
        bowtem_utils.add_subfig_label(
            f'{label}\n{mean.pairs} pairs', ax=ax, color='w', loc='sw')
        print(f'{label}: {mean.pairs} pairs, median {eff.median().item():.3f}'
              f', 99th pct {eff.quantile(0.99).item():.3f} a-1')

    # set axes properties
    for ax in axes:
        ax.set_aspect('equal')
        ax.set_xlim(510e3-17e3/6*76/85, 510e3+17e3/6*76/85)
        ax.set_title('')
    cax.set_ylabel(r'effective strain rate ($a^{-1}$)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
