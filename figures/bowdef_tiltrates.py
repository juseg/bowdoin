#!/usr/bin/env python
# Copyright (c) 2019-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation tilt rates."""

import absplots as apl

import bowdef_utils
import bowstr_utils
import bowtem_utils


def plot_faded(ax, df, dates):
    """Plot dataframe columns with faded records before given dates."""
    for i, (unit, series) in enumerate(df.items()):
        series[:dates[unit]].plot(
            ax=ax, alpha=0.25, color=f'C{i}', label='_nolegend_')
        series[dates[unit]:].plot(ax=ax, color=f'C{i}')


def add_unit_labels(ax, data, depth, offsets=None):
    """Add unit labels at the end of each line."""
    offsets = offsets or {}
    for i, unit in enumerate(data):
        last = data[unit].dropna().tail(1)
        ax.annotate(
            fr'{unit}, {depth[unit]:.0f}$\,$m', color=f'C{i}', fontsize=6,
            fontweight='bold', textcoords='offset points', va='center',
            xy=(last.index[0], last.iloc[0]), xytext=(4, offsets.get(unit, 0)))


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        nrows=2, figsize=(180, 120), sharex=True, gridspec_kw={
            'left': 12.5, 'right': 2.5, 'bottom': 10, 'top': 2.5,
            'height_ratios': (3, 1), 'hspace': 2.5})
    insets = fig.subplots_mm(ncols=2, gridspec_kw={
        'left': 42.5, 'right': 5, 'bottom': 85, 'top': 5, 'wspace': 12.5})

    # add subfigure labels
    bowtem_utils.add_subfig_label(ax=axes[0], text='(a)')
    bowtem_utils.add_subfig_label(ax=axes[1], text='(d)')
    bowtem_utils.add_subfig_label(ax=insets[0], text='(b)')
    bowtem_utils.add_subfig_label(ax=insets[1], text='(c)')

    # load tilt rate, temperature, depth and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    tilt = bowdef_utils.load_tilt_rates(method='kernel', window='3h')
    temp = bowstr_utils.load(variable='temp').resample('1h').mean()
    dates = bowstr_utils.load_freezing_dates()

    # plot tilt rate and temperature in main panels
    plot_faded(axes[0], tilt, dates)
    plot_faded(axes[1], temp, dates)
    bowtem_utils.add_field_campaigns(ax=axes[0], color='0.75')
    bowtem_utils.add_field_campaigns(ax=axes[1], color='0.75')

    # plot summer zooms in insets
    for ax, year in zip(insets, [2015, 2016]):
        tilt.plot(ax=ax, legend=False, xlabel='')
        bowtem_utils.add_field_campaigns(ax=ax, color='0.75')
        ax.set_xlim(f'{year}0601', f'{year}0901')
        ax.set_ylim(0, 21)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(which='minor')

    # add unit labels
    add_unit_labels(axes[1], temp, depth, offsets={'UI02': 3, 'UI03': -3})

    # set axes properties
    axes[0].set_ylabel(r'tilt rate ($°\,a^{-1}$)')
    axes[1].set_ylabel('temperature (°C)')
    axes[1].set_xlabel('')
    axes[0].set_xlim('20140701', '20171201')
    axes[0].set_ylim(-5/6, 30+5/6)
    axes[1].set_ylim(-6.5, 0.5)

    # mark insets
    for ax in insets:
        bowdef_utils.add_inset_indicator(axes[0], ax, connectors=(1, 3))

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
