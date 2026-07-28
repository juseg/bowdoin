#!/usr/bin/env python
# Copyright (c) 2015-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation creep diagram."""


import absplots as apl
import numpy as np
import pandas as pd

import bowdef_utils
import bowstr_utils

DENSITY = 917           # Ice density,          kg m-3          (CP10, p. 12)
GRAVITY = 9.80665       # Standard gravity,     m s-2           (--)
SLOPE = 1.6             # Bowdoin slope,        °               (Sug24)


def compute_power_fit(depth, strain):
    """Fit to a power law strain = constant * depth ** exponent."""
    exponent, constant = np.polyfit(np.log(depth), np.log(strain), 1)
    return exponent, np.exp(constant)


def compute_shear_profile(base, depth, exponent, constant):
    """Compute horizontal shear profile from fitted exponent and constant."""
    power = exponent + 1
    shear = 2 * constant / power * (base**power - depth**power)
    return shear


def plot_strain_stress(ax, stress, strain_rate, label, color=None):
    """Plot strain rate vs stress data and fit a power law."""

    # compute power fit
    exponent, constant = compute_power_fit(stress, strain_rate)
    stress_fit = np.array([stress.min()*2/3, stress.max()*3/2])
    strain_fit = constant*stress_fit**exponent

    # plot markers and line
    ax.plot(stress, strain_rate, color=color, linestyle='', marker='+')
    ax.plot(stress_fit, strain_fit, color=color, linestyle='--')

    # add text label
    textright = stress.max() < 100
    ax.text(
        (0.98+0.04*textright)*stress_fit[1*textright], strain_fit[1*textright],
        f'{label}\nn = {exponent:.2f}', color=color, fontweight='bold',
        ha='left' if textright else 'right', va='center')


def main(start='2014-11-01', end='2015-11-01'):
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(
        figsize=(180, 90), ncols=1, sharex=True, sharey=True, gridspec_kw={
            'left': 15, 'bottom': 10, 'right': 2.5, 'top': 2.5, 'wspace': 2.5})

    # load total strain
    depth = bowstr_utils.load(variable='dept').iloc[0]
    strain = bowdef_utils.load_strain(start, end)
    time_delta = pd.to_datetime(end) - pd.to_datetime(start)
    strain_rate = strain * pd.to_timedelta('365d') / time_delta
    stress = DENSITY * GRAVITY * depth * np.sin(SLOPE*np.pi/180) * 1e-3

    # plot Bowdoin data
    for bh, prefix in zip(['BH3', 'BH1'], ['U', 'L']):
        mask = strain.notnull() & strain.index.str.startswith(prefix)
        plot_strain_stress(
            ax, stress[mask], strain_rate[mask], bh, color=f'C{mask.argmax()}')

    # plot Schohn et al. 2025
    df = pd.read_csv('../data/native/schohn_etal_2025.csv', index_col='exp')
    stress = df['shear_stress'] * 1e3
    strain_rate = df['strain_rate'] * 1e-8
    strain_rate = strain_rate * pd.to_timedelta('365d') / pd.to_timedelta('1s')
    plot_strain_stress(ax, stress, strain_rate, 'Schohn et al. 2025', color='0.5')

    # set axes properties
    ax.set_xlabel('stress (kPa)')
    ax.set_ylabel('strain rate ($a^{-1}$)')
    ax.set_xscale('log')
    ax.set_yscale('log')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
