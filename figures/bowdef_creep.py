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


def load_schohn_etal_2025():
    """Load Schohn et al data in a dataframe."""
    columns = [
        'control', 'strain', 'strain_rate', 'strain_rate_error',
        'shear_stress', 'shear_stress_error', 'water_content',
        'water_content_err']
    data = {
        '1A': ['Stress',      0.094, 27.2, '0.7', 0.24, '<0.01', 1.55,  0.4],
        '1B': ['Stress',      0.112,  9.9, '0.3', 0.15, '<0.01', 1.53, 0.26],
        '1C': ['Stress',      0.137, 14.6, '1.2', 0.21, '<0.01', 1.65, 0.33],
        '1D': ['Stress',      0.145,  8.8, '0.4', 0.18, '<0.01', 1.48, 0.29],
        '2A': ['Strain rate', 0.069, 11.7, '0.3', 0.19, '<0.01', 1.54, 0.13],
        '2B': ['Strain rate', 0.075,  2.6,'<0.1', 0.05, '<0.01', 1.62, 0.08],
        '2C': ['Strain rate', 0.103,  8.9, '1.9', 0.16, '<0.01', 1.28, 0.18],
        '3A': ['Stress',      0.126, 21.1, '0.7', 0.24, '<0.01', 1.57, 0.13],
        '3B': ['Strain rate', 0.174,  4.6, '0.9', 0.09, '<0.01', 1.49, 0.16],
        '4A': ['Stress',      0.119, 13.7, '1.0', 0.22, '<0.01', 1.47, 0.19],
        '4B': ['Strain rate', 0.141,  7.3, '0.4', 0.15, '<0.01', 1.35, 0.11],
        '4C': ['Strain rate', 0.189,  5.8, '0.4', 0.11, '<0.01', 1.27, 0.36],
        '4D': ['Strain rate', 0.214,  3.9, '0.3', 0.12, '<0.01', 1.16, 0.25],
        '5A': ['Stress',      0.114, 13.6, '1.5', 0.19, '<0.01', 0.74, 0.08],
        '5B': ['Strain rate', 0.145,  6.2, '1.3', 0.11, '<0.01', 0.77, 0.08],
        '5C': ['Strain rate', 0.162,  4.7, '1.0', 0.08, '<0.01',  0.8,  0.1],
        '5D': ['Strain rate',  0.19,  5.3, '0.5', 0.09, '<0.01', 0.76, 0.14],
        '6A': ['Strain rate', 0.161,  7.7, '0.5', 0.13, '<0.01', 1.84, 0.17],
        '6B': ['Strain rate', 0.177,  4.2, '1.0', 0.09, '<0.01', 1.64, 0.17]}
    return pd.DataFrame(data=data, index=columns).transpose().infer_objects()


def plot_strain_stress(ax, stress, strain_rate, label, color=None):
    """Plot strain rate vs stress data and fit a power law."""

    # compute power fit
    exponent, constant = bowdef_utils.compute_power_fit(stress, strain_rate)
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
    df = load_schohn_etal_2025()
    plot_strain_stress(
        ax, 1e3*df.shear_stress,
        1e-8*df.strain_rate*pd.to_timedelta('365d')/pd.to_timedelta('1s'),
        'Schohn et al. 2025', color='0.5')

    # set axes properties
    ax.set_xlabel('stress (kPa)')
    ax.set_ylabel('strain rate ($a^{-1}$)')
    ax.set_xscale('log')
    ax.set_yscale('log')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
