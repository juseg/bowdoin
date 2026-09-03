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


def compute_power_fit_dataframe(depth, strain):
    """Fit to a power law strain = constant * depth ** exponent."""
    return strain.dropna(axis=0, how='all').apply(lambda series: pd.Series(
        data=bowdef_utils.compute_power_fit(depth, series),
        index=['exponent', 'constant']), axis=1)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=4, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
            'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(
        axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # load strain rates and speed
    strain = bowdef_utils.load_strain_rates(method='savgol', window='12h')
    speed = bowdef_utils.load_gnss_velocities(method='savgol', window='12h').vh
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]

    # reindex to intersection
    index = strain.index.join(speed.index, how='inner')
    speed = speed.reindex(index).interpolate(limit=2, method='time')
    strain = strain.reindex(index).interpolate(limit=2, method='time')

    # plot new sentinel velocity
    df = pd.read_csv(
        '../data/satellite/bowdoin-sentinel.txt', delimiter=',\\s+',
        index_col='YYYY-MM-DD (avg)', parse_dates=True, engine='python')
    print(df.index)
    print(speed.index)
    dt = pd.to_timedelta(df['time-diff (days)'], unit='D')
    mid = df.index
    vel = df['vel (m/a)']
    err = df['vel_error (m/a)']
    mask = dt <= pd.to_timedelta('12D')
    axes[0].errorbar(
        mpl.dates.date2num(mid[mask]), vel[mask],
        xerr=dt[mask]/pd.to_timedelta('1d')/2, yerr=err[mask],
        c='tab:pink', ls='', lw=0.5, zorder=4, alpha=0.75)
    axes[0].errorbar(
        mpl.dates.date2num(mid[-mask]), vel[-mask],
        xerr=dt[-mask]/pd.to_timedelta('1d')/2, yerr=err[-mask],
        c='tab:purple', ls='', lw=0.5, zorder=4, alpha=0.75)

    # plot landsat velocity
    df = pd.read_csv('../data/satellite/bowdoin-landsat.csv',
                     parse_dates=['start', 'end'])
    dt = df['end'] - df['start']
    mid = df['start'] + dt/2
    vel = df['vel']
    err = df['err']
    mid = pd.DatetimeIndex(mid)
    axes[0].errorbar(
        mpl.dates.date2num(mid), vel,
        xerr=dt/pd.to_timedelta('1d')/2, yerr=err,
        c='tab:orange', lw=0.5, ls='', zorder=3, alpha=0.75)

    # plot surface speed
    speed.plot(ax=axes[0], color='tab:blue')

    # for each borehole
    for bh, prefix in zip(['BH3', 'BH1'], ['U', 'L']):
        mask = strain.columns.str.startswith(prefix)

        # compute shear and basal speed
        coefs = compute_power_fit_dataframe(depth[mask], strain.loc[:, mask])
        power = coefs.exponent + 1
        shear = 2 * coefs.constant / power * base[f'{bh}B']**power
        ratio = 100 - 100 * shear / speed

        # plot shear and basal speeds
        shear.plot(ax=axes[1], color=f'C{mask.argmax()}')
        ratio.plot(ax=axes[2], color=f'C{mask.argmax()}')
        coefs.exponent.plot(ax=axes[3], color=f'C{mask.argmax()}')

    # set axes properties
    axes[0].grid(which='minor')
    axes[1].grid(which='minor')
    axes[2].grid(which='minor')
    axes[3].grid(which='minor')
    axes[3].set_xlabel('')
    axes[0].set_ylabel(r'surface ($m\,a^{-1}$)', labelpad=0)
    axes[1].set_ylabel(r'shear ($m\,a^{-1}$)')
    axes[2].set_ylabel('slip ratio (%)')
    axes[3].set_ylabel('flow exponent', labelpad=8)
    axes[0].set_xlim('20140701', '20170801')
    # axes[0].set_xlim('20150601', '20150930')
    # axes[0].set_xlim('20160601', '20160930')
    axes[1].set_ylim(5, 55)
    axes[2].set_ylim(92.5, 97.5)
    axes[3].set_ylim(-0.5, 4.5)

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
