#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation against GNSS velocity."""

import absplots as apl
import matplotlib as mpl
import pandas as pd

import bowdef_utils
import bowstr_utils
import bowtem_utils


def load_weather_station():
    """Load SIGMA-B hourly air temperature and surface height."""
    return pd.read_csv(
        '../data/external/SIGMA_AWS_SiteB_2012-2020_Lv1_3.csv',
        index_col='date', parse_dates=True, usecols=['date', 'T1', 'sh'],
        na_values=(-9999, -9998, -8888)).rename_axis(None)


def load_water_levels():
    """Load hourly piezometer pressure head."""
    wlev = pd.concat([bowtem_utils.load(
        f'../data/processed/bowdoin.{bh}.pzm.wlev.csv')
        for bh in ('bh2', 'bh3')], axis=1)
    wlev = wlev.rename(columns={'UP': 'BH2', 'LP': 'BH3'})
    return wlev[wlev > 0].resample('1h').mean()


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 180), nrows=6, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
            'height_ratios': (3, 3, 2, 2, 2, 1), 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # plot borehole velocity
    df = bowdef_utils.load_gnss_velocities(method='twopoint')
    df.vh.plot(ax=axes[0], color='0.9', label='_nolegend_')
    df = bowdef_utils.load_multivariate()
    df.gnss.plot(ax=axes[0], color='tab:blue', legend=False)

    # plot satellite velocities
    tab20 = mpl.color_sequences['tab20']
    bowdef_utils.plot_errorbar(
        axes[0], bowdef_utils.load_landsat_velocities(), color=tab20[3],
        label='Landsat')
    bowdef_utils.plot_errorbar(
        axes[0], bowdef_utils.load_sentinel_velocities(), color=tab20[11],
        label='Sentinel')

    # plot tilt rates, pressure head, air temperature, surface height and tide
    df.tilt.plot(ax=axes[1], legend=False)
    load_water_levels().plot(
        ax=axes[2], color={'BH2': 'tab:blue', 'BH3': 'tab:pink'})
    aws = load_weather_station()
    aws.T1.plot(ax=axes[3], c='C3')
    axes[3].axhline(0, c='k', lw=0.5)
    aws.sh.plot(ax=axes[4], c='C5')
    (df.tide/1e1).plot(ax=axes[5], legend=False, c='C9')

    # add velocity, tilt unit and borehole legends
    depth = bowstr_utils.load(variable='dept').iloc[0]
    axes[0].legend(loc='upper right', bbox_to_anchor=(0, 0, 11/12, 1))
    axes[1].legend(
        [f'{unit} ({depth[unit]:.0f}' r'$\,$m)' for unit in df.tilt],
        loc='upper right', bbox_to_anchor=(0, 0, 11/12, 1), ncol=3)
    axes[2].legend(loc='lower right', bbox_to_anchor=(0, 0, 11/12, 1))

    # set axes limits
    axes[0].grid(which='minor')
    axes[1].grid(which='minor')
    axes[2].grid(which='minor')
    axes[3].grid(which='minor')
    axes[4].grid(which='minor')
    axes[5].set_xlabel('')
    axes[0].set_ylabel(r'velocity ($m\,a^{-1}$)', labelpad=0)
    axes[1].set_ylabel(r'tilt rate ($°\,a^{-1}$)')
    axes[2].set_ylabel('pressure head (m)')
    axes[3].set_ylabel('air temp. (°C)')
    axes[4].set_ylabel('surface height (cm)')
    axes[5].set_ylabel('tide / 10 (kPa)', labelpad=0)
    axes[0].set_ylim(-50, 950)
    axes[1].set_ylim(-1, 21)
    axes[2].set_ylim(190, 260)
    axes[3].set_ylim(-45, 15)
    axes[4].set_ylim(-60, 140)
    axes[5].set_ylim(-2.4, 2.4)

    # zoom on tidal oscillations
    # axes[0].set_xlim('20160801', '20161001')
    # axes[1].set_ylim(-1, 14)
    # axes[2].set_ylim(1.99, 2.14)

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
