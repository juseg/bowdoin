#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides highpass-filtered timeseries."""

from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import numpy as np
import absplots as apl
import bowstr_utils
import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure (keep main axes for labels and inset)
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=2, sharey=True, gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 12.5, 'top': 2.5,
            'hspace': 12.5})
    subaxes = np.array([ax.get_subplotspec().subgridspec(
        ncols=1, nrows=10, hspace=10/(fig.get_position_mm(ax)[3]-9),
        ).subplots() for ax in axes])

    # reimplement sharex and sharey
    for panel in subaxes:
        for ax in panel:
            ax.sharex(panel[0])
            ax.sharey(panel[0])

    # hide parent axes
    for ax in axes:
        ax.set_axis_off()

    # only show subaxes outer spines
    for ax in subaxes.flat:
        ax.spines['top'].set_visible(ax.get_subplotspec().is_first_row())
        ax.spines['bottom'].set_visible(ax.get_subplotspec().is_last_row())
        ax.tick_params(bottom=ax.get_subplotspec().is_last_row(), which='both')

    # add subfigure labels
    for ax, label in zip(subaxes[:, 0], ['(a)', '(b)']):
        ax.text(-0.05, 0, label, fontweight='bold', transform=ax.transAxes)

    # highpass-filter stress series
    # IDEA implement filter=True, tide=True in bowstr_utils.load()
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load().resample('1h').mean()
    pres = bowstr_utils.filter(pres)

    # load tide data
    tide = bowstr_utils.load_pituffik_tides().resample('1h').mean()  # kPa
    pres['tide'] = tide / 10

    # plot stress and tide data
    for pax, panel in zip(axes, subaxes):
        for i, unit in enumerate(pres):
            ax = panel[i]
            color = f'C{i}'
            label = (
                'Pituffik\ntide'r'$\,/\,$10' if unit == 'tide' else
                f'{unit}\n{depth[unit]:.0f}'r'$\,$m')
            pres[unit].plot(ax=ax, color=color, legend=False)
            ax.text(
                1.01, 0, label, color=color, fontsize=6, fontweight='bold',
                transform=ax.transAxes)

            # clip lines to main axes
            ax.patch.set_alpha(0)
            ax.get_lines()[0].set_clip_box(pax.bbox)

            # set axes properties
            ax.grid(which='minor')
            ax.set_ylim(-2, 2)
            ax.set_yticks([-1, 1])

            # staggered ticks (IDEA use a scale bar instead?)
            ax.tick_params(labelleft=ax.get_subplotspec().is_last_row())
            ax.yaxis.set_major_formatter(
                lambda y, pos: f'{y}' + 3 * (pos % 2) * ' ')

        # set labels
        panel[4].set_ylabel('stress (kPa)')
        panel[9].set_xlabel('')

    # set axes limits
    subaxes[0, 0].set_xlim('20140701', '20170801')
    subaxes[1, 0].set_xlim('20140816', '20141016')

    # mark zoom inset
    mark_inset(subaxes[0, 0], subaxes[1, 0], loc1=1, loc2=2, ec='0.75', ls='--')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
