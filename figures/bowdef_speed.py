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


def compute_interval_aggregates(series, intervals, **kwargs):
    """Aggregate series over intervals defined in a dataframe."""
    return intervals.apply(
        lambda row: series[row.start: row.end].aggregate(**kwargs), axis=1)


def load_landsat_velocities():
    """Load surface velocities from Landsat feature-tracking."""
    df = pd.read_csv(
        '../data/satellite/bowdoin-landsat.csv', parse_dates=['start', 'end'])
    df = df.assign(delay=df.end-df.start)
    df = df.set_index(df.start+df.delay/2)
    df = df.assign(delay=df.delay/pd.to_timedelta('1d'))
    df = df.rename(columns={'vel': 'speed', 'err': 'error'})
    return df


def load_sentinel_velocities():
    """Load surface velocities from Sentinel feature-tracking."""
    df = pd.read_csv(
        '../data/satellite/bowdoin-sentinel.txt', delimiter=',\\s+',
        engine='python', index_col='YYYY-MM-DD (avg)',
        parse_dates=['YYYY-MM-DD (1st)', 'YYYY-MM-DD (2nd)'])
    df = df.rename_axis(None).rename(columns={
        'time-diff (days)': 'delay', 'vel (m/a)': 'speed',
        'vel_error (m/a)': 'error', 'YYYY-MM-DD (1st)': 'start',
        'YYYY-MM-DD (2nd)': 'end'})
    return df


def load_shear_velocities(**kwargs):
    """Load internal deformation velocity from tilt rates."""

    # load strain rates and speed
    strain = bowdef_utils.load_strain_rates(**kwargs)
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]

    # group by borehole and fit a power law (axis=1 is deprecated)
    coefs = strain.T.groupby(strain.columns.str[0]).apply(
        lambda df: compute_power_fit_dataframe(depth[df.index], df.T).T)
    coefs = coefs.rename({'L': 'BH1', 'U': 'BH3'}).swaplevel(0, 1).T

    # return shear velocities (FIXME and exponent)
    base = base.set_axis(base.index.str[:3])
    return 2 * coefs.constant / (coefs.exponent+1) * base**(coefs.exponent+1)


def plot_satellite(ax, df, **kwargs):
    """Plot satellite velocities from dataframe."""
    index = ax.xaxis.get_converter().convert(df.index, None, ax.xaxis)
    xerr = (df.end-df.start)/2/pd.to_timedelta('1'+ax.xaxis.freq)
    return ax.errorbar(
        index, df.speed, xerr=xerr, yerr=df.error,
        linestyle='', linewidth=0.5, zorder=0, **kwargs)


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

    # load shear and surface speeds and compute ratio where they intersect
    shear = load_shear_velocities(method='savgol', window='12h')
    speed = bowdef_utils.load_gnss_velocities(method='savgol', window='12h').vh
    index = shear.index.intersection(speed.index)
    ratio = 100 - 100 * shear.divide(speed, axis=0).reindex(index)

    # load satellite velocities
    landsat = load_landsat_velocities().assign(source='landsat')
    sentinel = load_sentinel_velocities().assign(source='sentinel')
    sat = pd.concat([landsat, sentinel])

    # compute slip ratio from satellite and propagate uncertainties
    sat_shear_speed = compute_interval_aggregates(shear, sat, func='mean')
    sat_ratio_speed = 100 - 100 * sat_shear_speed.divide(sat.speed, axis=0)
    sat_ratio_error = 100 * sat_shear_speed.multiply(
        1/(sat.speed-sat.error/2)-1/(sat.speed+sat.error/2), axis=0)

    # plot surface speed, shear and slip ratio from geopositioning
    speed.plot(ax=axes[0], color='tab:orange')
    shear.plot(ax=axes[1], color={'BH1': 'tab:blue', 'BH3': 'tab:pink'})
    ratio.plot(ax=axes[2], color={'BH1': 'tab:blue', 'BH3': 'tab:pink'}, legend=False)

    # plot surface speed and slip ratio from satellite
    plot_satellite(axes[0], landsat, color=mpl.color_sequences['tab20'][3], label='Landsat')
    plot_satellite(axes[0], sentinel, color=mpl.color_sequences['tab20'][11], label='Sentinel')
    for bh in ['BH3', 'BH1']:
        plot_satellite(axes[2], sat.assign(
            speed=sat_ratio_speed[bh], error=sat_ratio_error[bh]),
            color=mpl.color_sequences['tab20'][{'BH1': 1, 'BH3': 13}[bh]])

    # set axes properties
    axes[0].legend()
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
