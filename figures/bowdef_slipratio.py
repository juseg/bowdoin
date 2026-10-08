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


def compute_interval_aggregates(series, intervals, **kwargs):
    """Aggregate series over intervals defined in a dataframe."""
    return intervals.apply(
        lambda row: series[row.start: row.end].aggregate(**kwargs), axis=1)


def compute_power_fits(depth, strain):
    """Fit power laws strain = constant * depth ** exponent on each row."""

    # least squares in log space, ignoring missing values on each row
    valid = strain.notna().to_numpy()
    x = np.where(valid, np.log(depth[strain.columns].to_numpy()), 0)
    y = np.where(valid, np.log(strain.to_numpy()), 0)
    count = valid.sum(axis=1)
    sx, sy = x.sum(axis=1), y.sum(axis=1)
    sxx, sxy = (x*x).sum(axis=1), (x*y).sum(axis=1)
    exponent = (count*sxy - sx*sy) / (count*sxx - sx**2)
    constant = np.exp((sy - exponent*sx) / count)

    # return as series
    return (pd.Series(exponent, index=strain.index),
            pd.Series(constant, index=strain.index))


def compute_shear_velocities(strain, depth, base):
    """Compute shear velocity and flow exponent from strain rate profiles."""
    shear, exponent = {}, {}
    for bh, prefix in [('BH3', 'L'), ('BH1', 'U')]:

        # fit a power law strain = constant * depth ** exponent at each time
        rates = strain.loc[:, strain.columns.str.startswith(prefix)]
        rates = rates.dropna(how='all')
        exponent[bh], constant = compute_power_fits(depth, rates)

        # integrate strain rate over ice thickness
        power = exponent[bh] + 1
        shear[bh] = 2 * constant / power * base[f'{bh}B']**power

    # return as dataframes
    return pd.DataFrame(shear), pd.DataFrame(exponent)


def compute_shear_profile(base, depth, exponent, surface):
    """Compute horizontal shear profile from exponent and surface velocity."""
    power = exponent + 1
    shear = surface * (1 - (depth/base)**power)
    return shear


def plot_shear_profile(
        ax, base, depth, exponent, surface, *, colors, color='C0',
        summer=False):
    """Plot shear velocity profile from exponent and surface velocity."""

    # compute and plot discrete and extrapolated shear profiles
    depth_int = np.linspace(0, base, 51)
    shear_int = compute_shear_profile(base, depth_int, exponent, surface)
    shear = compute_shear_profile(base, depth, exponent, surface)
    plot_shear_profile_lines(
        ax, depth_int, shear_int, color=color, summer=summer)
    plot_shear_profile_markers(
        ax, depth, shear, colors=colors, color=color, summer=summer)


def plot_shear_profile_lines(ax, depth, shear, color='C0', summer=False):
    """Plot continuous shear profile line, fill summer profile."""
    if summer:
        ax.fill_betweenx(depth, 0, shear, color=color, alpha=0.25)
        ax.plot([0, shear[0]], [0, 0], color=color)
    ax.plot(shear, depth, color=color, ls='-' if summer else '--')


def plot_shear_profile_markers(
        ax, depth, shear, *, colors, color='C0', summer=False):
    """Mark tilt units on shear profile, with arrows in winter."""
    ax.scatter(shear, depth, c=colors[depth.index], edgecolors=color, zorder=3)
    if summer:
        return
    for unit in depth.index[shear > 5]:  # skip arrows too short for a head
        arrowprops = {
            'color': color, 'clip_box': ax.bbox, 'clip_on': True,
            'shrinkB': 4}

        # draw a dashed tail ending inside the head, and a solid head
        ax.annotate(
            '', xy=(shear[unit], depth[unit]), xytext=(0, depth[unit]),
            zorder=2, arrowprops={
                **arrowprops, 'arrowstyle': '-', 'linestyle': 'dashed',
                'linewidth': 1, 'shrinkB': 6})
        ax.annotate(
            '', xy=(shear[unit], depth[unit]), xytext=(8, 0),
            textcoords='offset points', zorder=2, arrowprops={
                **arrowprops, 'arrowstyle': '-|>', 'linewidth': 1,
                'shrinkA': 0})


def plot_faded(ax, df, dates, colors):
    """Plot dataframe columns with faded records before given dates."""
    for bh, series in df.items():
        series[:dates[bh]].plot(
            ax=ax, alpha=0.25, color=colors[bh], label='_nolegend_')
        series[dates[bh]:].plot(ax=ax, color=colors[bh])


def main():
    """Main program called during execution."""

    # initialize figure (disable sharex on pfaxes as pandas handle_shared_axes
    # otherwise detect them as sharing axes with the timeseries)
    fig = apl.figure_mm(figsize=(180, 120))
    axes = fig.subplots_mm(nrows=4, sharex=True, gridspec_kw={
        'left': 12.5, 'right': 47.5, 'bottom': 12.5, 'top': 2.5,
        'hspace': 2.5})
    pfaxes = fig.subplots_mm(nrows=2, sharey=True, gridspec_kw={
        'left': 135, 'right': 12.5, 'bottom': 12.5, 'top': 2.5, 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels([*axes, *pfaxes])

    # load sensor depths and ice thickness
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]

    # load shear and surface speeds and compute ratio where they intersect
    strain = bowdef_utils.load_strain_rates(method='kernel', window='3h')
    shear, exponent = compute_shear_velocities(strain, depth, base)
    speed = bowdef_utils.load_gnss_velocities(method='kernel', window='3h').vh
    index = shear.index.intersection(speed.index)
    ratio = 100 - 100 * shear.divide(speed, axis=0).reindex(index)

    # load velocities from landsat and sentinel images
    landsat = bowdef_utils.load_landsat_velocities()
    sentinel = bowdef_utils.load_sentinel_velocities()
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

    # share profile x axes only after pandas plotting (see above)
    pfaxes[1].sharex(pfaxes[0])

    # plot winter and summer shear profiles from mean power-law fits
    colors = pd.Series([f'C{i}' for i in range(depth.size)], index=depth.index)
    boreholes = [(pfaxes[0], 'BH3', 'L'), (pfaxes[1], 'BH1', 'U')]
    for ax, bh, prefix in boreholes:
        ax.text(0.05, 0.21, bh, color=color_dict[bh], fontweight='bold',
                transform=ax.transAxes)
    # FIXME: winter starts on Jan. 4 to skip the UI04 tilt offset jump of
    # 2015 Jan. 2, restore Jan. 1 once the jump is fixed in preprocessing.
    for start, end, summer in [('2015-01-04', '2015-02-01', False),
                               ('2015-07-01', '2015-08-01', True)]:
        surfaces = []
        for ax, bh, prefix in boreholes:
            units = strain.loc[start:end, strain.columns.str.startswith(
                prefix)].dropna(axis=1, how='all').columns
            mean_exponent = exponent[bh][start:end].mean()
            surface = shear[bh][start:end].mean()
            plot_shear_profile(
                ax, base[f'{bh}B'], depth[units], mean_exponent, surface,
                colors=colors, color=color_dict[bh], summer=summer)
            surfaces.append(surface)
            ax.text(0.05, 0.05 + 0.08 * summer,
                    f'{pd.to_datetime(start):%b.} n = {mean_exponent:.2f}',
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
    bowdef_utils.plot_errorbar(
        axes[0], landsat, color=tab20[3], label='Landsat-8')
    bowdef_utils.plot_errorbar(
        axes[0], sentinel, color=tab20[11], label='Sentinel-1')
    for bh, color in [('BH1', tab20[1]), ('BH3', tab20[13])]:
        bowdef_utils.plot_errorbar(axes[2], sat.assign(
            speed=sat_speed[bh], error=sat_error[bh]), color=color)

    # set axes properties
    axes[0].legend(loc='upper right', bbox_to_anchor=(0, 0, 0.94, 1))
    axes[2].legend(loc='upper right', bbox_to_anchor=(0, 0, 0.94, 1))
    for ax in [*axes, *pfaxes]:
        ax.grid(which='minor')
    axes[3].set_xlabel('')
    axes[0].set_ylabel(r'surface ($m\,a^{-1}$)', labelpad=0)
    axes[1].set_ylabel(r'shear ($m\,a^{-1}$)')
    axes[2].set_ylabel('slip ratio (%)')
    axes[3].set_ylabel('flow exponent', labelpad=8)
    for ax in pfaxes:
        ax.yaxis.set_label_position('right')
        ax.yaxis.tick_right()
        ax.set_xlim(30, 0)
        ax.yaxis.set_inverted(True)
        ax.set_ylabel('depth (m)')
    pfaxes[0].tick_params(labelbottom=False)
    pfaxes[1].set_xlabel(r'shear ($m\,a^{-1}$)')
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
