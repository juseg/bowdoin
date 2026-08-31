#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation against GNSS velocity."""

import absplots as apl
import numpy as np
import pandas as pd

import bowdef_utils
import bowstr_utils
import bowtem_utils


def compute_power_fit_nan(depth, strain):
    """Fit to a power law strain = constant * depth ** exponent."""
    log_strain = np.log(strain.dropna())
    log_depth = np.log(depth.reindex(log_strain.index))
    exponent, constant = np.polyfit(log_depth, log_strain, 1)
    return exponent, np.exp(constant)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=3, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 12.5, 'top': 2.5,
            'height_ratios': (1, 1, 1), 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # load strain rates and speed
    strain = bowdef_utils.load_strain_rates(method='savgol', window='12h')
    speed = bowdef_utils.load_gnss_velocities(method='savgol', window='12h').vh
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]

    # limit to a given period
    strain = strain.loc['20150516':'20150815']  # 2015 full gnss record

    # reindex to intersection
    index = strain.index.join(speed.index, how='inner')
    speed = speed.reindex(index).interpolate(limit=2, method='time')
    strain = strain.reindex(index).interpolate(limit=2, method='time')

    # subset for testing
    # strain = strain.drop(columns=['UI03', 'UI02'])
    # depth = depth.drop(index=['UI03', 'UI02'])

    # plot surface speed
    speed.plot(ax=axes[0], color='tab:blue')

    # for each borehole
    for bh, prefix in zip(['BH3', 'BH1'], ['U', 'L']):
        mask = (strain.count() > 0) & strain.columns.str.startswith(prefix)

        # compute shear and basal speed
        coefs = strain.apply(
            lambda series: pd.Series(
                data=compute_power_fit_nan(depth, series),
                index=['exponent', 'constant']), axis=1)
        power = coefs.exponent + 1
        shear = 2 * coefs.constant / power * base[f'{bh}B']**power
        basal = speed - shear
        ratio = shear / speed * 100

        # plot shear and basal speeds
        shear.plot(ax=axes[1], color=f'C{mask.argmax()}')
        ratio.plot(ax=axes[2], color=f'C{mask.argmax()}')

    # set axes properties
    axes[0].grid(which='minor')
    axes[1].grid(which='minor')
    axes[2].grid(which='minor')
    axes[2].set_xlabel('')
    axes[0].set_ylabel(r'surface velocity ($m\,a^{-1}$)', labelpad=0)
    axes[1].set_ylabel(r'shear velocity ($m\,a^{-1}$)')
    axes[2].set_ylabel('shear ratio (%)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
