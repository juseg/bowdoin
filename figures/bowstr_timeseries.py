#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress time series."""

from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import pandas as pd
import absplots as apl
import bowtem_utils
import bowstr_utils


def add_closure_dates(ax, data, date):
    """Add borehole closure dates."""
    for i, unit in enumerate(data):
        ax.plot(
            date[[unit]].astype('int') // 1e9 // 3600,
            data[unit][date[unit]], color=f'C{i}', marker='o')
        ax.axvline(date[unit], color=f'C{i}', lw=0.5)


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
        ncols=2, nrows=2, figsize=(180, 120), sharex='col', sharey='row',
        gridspec_kw={
            'left': 12.5, 'right': 2.5, 'bottom': 10, 'top': 2.5,
            'height_ratios': (3, 1), 'hspace': 2.5,
            'width_ratios': [1, 3], 'wspace': 1})
    insets = fig.subplots_mm(ncols=2, gridspec_kw={
        'left': 52.5, 'right': 5, 'bottom': 95, 'top': 5, 'wspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_label(ax=axes[0, 0], text='(a)')
    bowtem_utils.add_subfig_label(ax=axes[1, 0], text='(d)')
    bowtem_utils.add_subfig_label(ax=insets[0], text='(b)', loc='sw')
    bowtem_utils.add_subfig_label(ax=insets[1], text='(c)', loc='sw')

    # load stress, temperature and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(variable='wlev').resample('1h').mean() / 1e3
    temp = bowstr_utils.load(variable='temp').resample('1h').mean()
    date = bowstr_utils.load_freezing_dates()

    # plot pressure data in top panels
    for ax in axes[0]:
        pres.plot(ax=ax, legend=False)
        add_closure_dates(ax, pres, date)
        bowtem_utils.add_field_campaigns(ax=ax, ytext=0.02)

    # plot temperature data in bottom panels
    for ax in axes[1]:
        temp.plot(ax=ax, legend=False)
        add_closure_dates(ax, temp, date)
        bowtem_utils.add_field_campaigns(ax=ax, ytext=None)

    # plot pressure data in insets
    for ax in insets:
        pres.plot(ax=ax, legend=False)

    # add unit labels
    add_unit_labels(axes[0, 1], pres, depth, offsets={
        'LI05': -4, 'UI02': 4, 'UI03': -12})
    add_unit_labels(axes[1, 1], temp, depth)

    # set main axes properties
    axes[1, 0].set_xlabel('')
    axes[0, 0].set_ylabel('stress (MPa)')
    axes[1, 0].set_ylabel('temperature (°C)')
    axes[0, 0].set_xlim('20140708', '20140908')
    axes[0, 1].set_xlim('20140908', '20171216')
    axes[0, 0].set_ylim(-1/12, 4-1/12)
    axes[1, 0].set_ylim(-6.5, 0.5)

    # set inset axes limits
    insets[0].set_xlim('20140901', '20141001')
    insets[0].set_ylim(1.15, 1.55)
    insets[1].set_xlim('20140906', '20140916')
    insets[1].set_ylim(1.28, 1.40)
    insets[1].set_xlim('20140922', '20140930')
    insets[1].set_ylim(1.42, 1.50)

    # emulate broken axes
    for ax in axes.flat:
        gs = ax.get_subplotspec()
        ax.spines['left'].set_visible(gs.is_first_col())
        ax.spines['right'].set_visible(gs.is_last_col())
        ax.tick_params(
            labelbottom=gs.is_last_row(), left=gs.is_first_col())
        ax.plot(
            [1*gs.is_first_col()]*2, [0, 1], clip_on=False, ls='',
            marker=[(-1, -2), (1, 2)], mec='k', ms=6, transform=ax.transAxes)

    # remove ticks, add grid
    for ax in insets:
        ax.set_xticklabels([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.grid(which='minor')

    # mark insets
    mark_inset(axes[0, 0], insets[0], loc1=2, loc2=4, ec='0.75', ls='--')
    mark_inset(insets[0], insets[1], loc1=2, loc2=3, ec='0.75', ls='--')

    # save default
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
