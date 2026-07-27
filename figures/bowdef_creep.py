#!/usr/bin/env python
# Copyright (c) 2015-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation creep diagram."""


import absplots as apl
import numpy as np
import pandas as pd

import bowstr_utils


def compute_power_fit(depth, strain):
    """Fit to a power law strain = constant * depth ** exponent."""
    exponent, constant = np.polyfit(np.log(depth), np.log(strain), 1)
    return exponent, np.exp(constant)


def compute_shear_profile(base, depth, exponent, constant):
    """Compute horizontal shear profile from fitted exponent and constant."""
    power = exponent + 1
    shear = 2 * constant / power * (base**power - depth**power)
    return shear


def main(start='2014-11-01', end='2015-11-01'):
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(
        figsize=(180, 90), ncols=1, sharex=True, sharey=True, gridspec_kw={
            'left': 15, 'bottom': 10, 'right': 2.5, 'top': 2.5, 'wspace': 2.5})

    # load total strain (do we need an util)
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]
    tilx = bowstr_utils.load(variable='tilx')
    tily = bowstr_utils.load(variable='tily')
    tilx = tilx.loc[end].mean() - tilx.loc[start].mean()
    tily = tily.loc[end].mean() - tily.loc[start].mean()
    costilt = np.cos(tilx) * np.cos(tily)
    strain = 0.5 * (1 - costilt**2) ** 0.5 / costilt
    time_delta = pd.to_datetime(end) - pd.to_datetime(start)
    strain_rate = strain / time_delta.total_seconds()

    # plot Schohn et al. 2025
    df = pd.read_csv('../data/native/schohn_etal_2025.csv', index_col='exp')
    ax.plot(df['shear_stress'], df['strain_rate']*1e-8, color='0.5', linestyle='', marker='+')

    # plot power fit
    exponent, constant = compute_power_fit(df['shear_stress'], df['strain_rate']*1e-8)
    stress = np.array([0.04, 0.4])
    ax.plot(stress, constant*stress**exponent, color='0.5', linestyle='--')
    ax.text(
        0.98*stress[0], 0.72*constant*stress[0]**exponent,
        f'Schohn et al. 2025\nn = {exponent:.2f}', color='0.5', ha='right',
        fontweight='bold')

    # plot velocity profile
    for bh in ('BH3', 'BH1'):
        mask = strain.notnull() & strain.index.str.startswith(
            'U' if bh == 'BH1' else 'L')
        color = f'C{mask.argmax()}'
        stress = 917 * 9.80665 * depth * np.sin(1.6*np.pi/180) * 1e-6
        ax.plot(stress[mask], strain_rate[mask], color=color, linestyle='', marker='+')
        # ax.text(1, 20, bh, color=color, fontweight='bold', ha='right')

        # plot power fit
        exponent, constant = compute_power_fit(stress[mask], strain_rate[mask])
        stress = np.array([0.02, 0.1])
        ax.plot(stress, constant*stress**exponent, color=color, linestyle='--')
        ax.text(
            1.02*stress[-1], 0.72*constant*stress[-1]**exponent,
            f'{bh}\nn = {exponent:.2f}', color=color, fontweight='bold')

    # set axes properties
    ax.set_xlabel('stress (MPa)')
    ax.set_ylabel('strain rate ($s^{-1}$)')
    ax.set_xscale('log')
    ax.set_yscale('log')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
