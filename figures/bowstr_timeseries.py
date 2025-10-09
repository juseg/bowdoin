#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress time series."""

import absplots as apl
import matplotlib as mpl
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


def add_inset_indicator(ax, inset, connectors=None):
    """Add inset indicator with custom connector visibility.

    The clip_on property is overriden by matplotlib if it detects that some
    other styling properties are the same for the indicator rectangle as for
    the connectors, so we trick matplotlib into believing that the rectangle
    has a different linestyle by using the 'dashed' style for the connectors
    and the matching dashed pattern tuple for the rectangle; this works
    (https://github.com/matplotlib/matplotlib/issues/30642).
    """
    dashes = mpl.rcParams['lines.dashed_pattern']
    indicator = ax.indicate_inset(inset_ax=inset, ls='dashed')
    indicator.rectangle.set_clip_on(True)
    indicator.rectangle.set_clip_box(ax.bbox)
    indicator.rectangle.set_linestyle((0, dashes))
    if connectors is not None:
        for i, connector in enumerate(indicator.connectors):
            connector.set_clip_on(False)
            connector.set_clip_box(ax.figure.bbox)
            connector.set_visible(i in connectors)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        ncols=2, nrows=2, figsize=(180, 120), sharex='col', sharey='row',
        gridspec_kw={
            'left': 12.5, 'right': 2.5, 'bottom': 10, 'top': 2.5,
            'height_ratios': (3, 1), 'hspace': 2.5,
            'width_ratios': (1, 5), 'wspace': 1})
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
    axes[0, 1].set_xlim('20140908', '20171201')
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
        ax.tick_params(labelbottom=gs.is_last_row(), left=gs.is_first_col())
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
    axes[0, 0].set_zorder(axes[0, 1].get_zorder()+1)
    add_inset_indicator(axes[0, 0], insets[0], connectors=(1,))
    add_inset_indicator(axes[0, 1], insets[0], connectors=(2,))
    add_inset_indicator(insets[0], insets[1], connectors=(0, 1))

    # fix mysterious behaviour of pandas private ticker
    axes[1, 0].set_xticks([], minor=True)
    axes[1, 0].set_xticks(axes[1, 0].get_xticks()[1:-1])
    axes[1, 0].set_xticklabels([
        label.get_text().lstrip('\n')
        for label in axes[1, 0].get_xticklabels()])

    # save default
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
