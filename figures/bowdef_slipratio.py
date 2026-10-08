#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin surface and shear velocities and slip ratio."""

import absplots as apl
import matplotlib as mpl
import numpy as np
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


def load_shear_velocities(**kwargs):
    """Load internal deformation velocity from tilt rates."""

    # load strain rates and speed
    strain = bowdef_utils.load_strain_rates(**kwargs)
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]

    # group by borehole and fit a power law (axis=1 is deprecated)
    coefs = strain.T.groupby(strain.columns.str[0]).apply(
        lambda df: compute_power_fit_dataframe(depth[df.index], df.T).T)
    coefs = coefs.rename({'L': 'BH3', 'U': 'BH1'}).swaplevel(0, 1).T

    # return shear velocities
    base = base.set_axis(base.index.str[:3])
    shear = 2 * coefs.constant / (coefs.exponent+1) * base**(coefs.exponent+1)
    return shear, coefs.exponent


def plot_shear_profile(ax, depth, base, strain, color, colors, summer=False):
    """Fit and plot a shear velocity profile, return exponent and surface."""
    n, c = bowdef_utils.compute_power_fit(depth, strain)
    z = depth[strain.notna()]
    v = 2*c/(n+1) * (base**(n+1) - z**(n+1))
    ax.scatter(v, z, c=colors[z.index], edgecolors=color, zorder=3)
    z = np.linspace(0, base, 51)
    v = 2*c/(n+1) * (base**(n+1) - z**(n+1))
    if summer:
        ax.fill_betweenx(z, 0, v, color=color, alpha=0.25)
        ax.plot([0, v[0]], [0, 0], color=color)
    ax.plot(v, z, color=color, ls='-' if summer else '--')
    return n, v[0]


def plot_faded(ax, df, dates, colors):
    """Plot dataframe columns with faded records before given dates."""
    for bh, series in df.items():
        series[:dates[bh]].plot(
            ax=ax, alpha=0.25, color=colors[bh], label='_nolegend_')
        series[dates[bh]:].plot(ax=ax, color=colors[bh])


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=4, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 50, 'bottom': 12.5, 'top': 2.5,
            'hspace': 2.5})
    pfaxes = [fig.add_axes_mm([132.5, 66.25, 32.5, 51.25])]
    pfaxes.append(fig.add_axes_mm(
        [132.5, 12.5, 32.5, 51.25], sharex=pfaxes[0], sharey=pfaxes[0]))

    # add subfigure labels
    bowtem_utils.add_subfig_labels(
        [*axes, *pfaxes], bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # load shear and surface speeds and compute ratio where they intersect
    shear, exponent = load_shear_velocities(method='kernel', window='3h')
    speed = bowdef_utils.load_gnss_velocities(method='kernel', window='3h').vh
    index = shear.index.intersection(speed.index)
    ratio = 100 - 100 * shear.divide(speed, axis=0).reindex(index)

    # load velocities from landsat and sentinel images
    landsat = bowdef_utils.load_landsat_velocities().assign(source='landsat')
    sentinel = bowdef_utils.load_sentinel_velocities().assign(
        source='sentinel')
    sat = pd.concat([landsat, sentinel])

    # compute slip ratio from satellite and propagate uncertainties
    sat_shear = compute_interval_aggregates(shear, sat, func='mean')
    sat_speed = 100 - 100 * sat_shear.divide(sat.speed, axis=0)
    sat_error = 100 * sat_shear.multiply(
        1/(sat.speed-sat.error/2)-1/(sat.speed+sat.error/2), axis=0)

    # load latest freezing date in each borehole
    dates = bowstr_utils.load_freezing_dates()
    dates = dates.groupby(dates.index.str[0]).max()
    dates = dates.rename({'L': 'BH3', 'U': 'BH1'})

    # plot surface speed, shear and slip ratio from geopositioning
    color_dict = {'BH1': 'tab:blue', 'BH3': 'tab:pink'}
    speed.plot(ax=axes[0], color='tab:orange', label='GNSS')
    plot_faded(axes[1], shear, dates, color_dict)
    plot_faded(axes[2], ratio, dates, color_dict)
    plot_faded(axes[3], exponent, dates, color_dict)
    for ax in axes:
        bowtem_utils.add_field_campaigns(ax=ax, color='0.75')

    # plot winter and summer shear profiles
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]
    colors = pd.Series([f'C{i}' for i in range(depth.size)], index=depth.index)
    boreholes = [(pfaxes[0], 'BH3', 'L'), (pfaxes[1], 'BH1', 'U')]
    for ax, bh, prefix in boreholes:
        ax.plot([0, 0], [base[f'{bh}B'], 0], 'k-_')
        ax.text(0.05, 0.21, bh, color=color_dict[bh], fontweight='bold',
                transform=ax.transAxes)
    for start, end, summer in [('2015-01-01', '2015-02-01', False),
                               ('2015-07-01', '2015-08-01', True)]:
        days = (pd.to_datetime(end) - pd.to_datetime(start)).days
        strain = bowdef_utils.load_strain(start, end) * 365 / days
        surfaces = []
        for ax, bh, prefix in boreholes:
            mask = strain.index.str.startswith(prefix)
            n, surface = plot_shear_profile(
                ax, depth[mask], base[f'{bh}B'], strain[mask],
                color_dict[bh], colors[mask], summer=summer)
            surfaces.append(surface)
            ax.text(0.05, 0.05 + 0.08 * summer,
                    f'{pd.to_datetime(start):%b.} n = {n:.2f}',
                    color=color_dict[bh], transform=ax.transAxes)

        # mark profile interval
        converter = axes[1].xaxis.get_converter()
        x0, x1 = converter.convert(
            pd.to_datetime([start, end]), None, axes[1].xaxis)
        y0, y1 = min(surfaces) - 5, max(surfaces) + 5
        axes[1].indicate_inset(
            bounds=[x0, y0, x1-x0, y1-y0], ls='dashed', zorder=5)

    # plot surface speed and slip ratio from satellite
    tab20 = mpl.color_sequences['tab20']
    bowdef_utils.plot_errorbar(axes[0], landsat, color=tab20[3], label='Landsat')
    bowdef_utils.plot_errorbar(axes[0], sentinel, color=tab20[11], label='Sentinel')
    bowdef_utils.plot_errorbar(axes[2], sat.assign(
        speed=sat_speed['BH1'], error=sat_error['BH1']), color=tab20[1])
    bowdef_utils.plot_errorbar(axes[2], sat.assign(
        speed=sat_speed['BH3'], error=sat_error['BH3']), color=tab20[13])

    # set axes properties
    axes[0].legend(loc='upper right', bbox_to_anchor=(0, 0, 11/12, 1))
    axes[2].legend(loc='upper right', bbox_to_anchor=(0, 0, 11/12, 1))
    axes[0].grid(which='minor')
    axes[1].grid(which='minor')
    axes[2].grid(which='minor')
    axes[3].grid(which='minor')
    axes[3].set_xlabel('')
    axes[0].set_ylabel(r'surface ($m\,a^{-1}$)', labelpad=0)
    axes[1].set_ylabel(r'shear ($m\,a^{-1}$)')
    axes[2].set_ylabel('slip ratio (%)')
    axes[3].set_ylabel('flow exponent', labelpad=8)
    for ax in pfaxes:
        ax.grid(which='minor')
        ax.yaxis.set_label_position('right')
        ax.yaxis.tick_right()
        ax.set_ylabel('depth (m)')
    pfaxes[0].tick_params(labelbottom=False)
    pfaxes[1].set_xlabel(r'shear ($m\,a^{-1}$)')
    pfaxes[0].set_xlim(30, 0)
    pfaxes[0].set_ylim(280, 0)
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
