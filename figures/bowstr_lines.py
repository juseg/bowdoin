#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress filtered line plots."""

import absplots as apl

import bowstr_utils


def plot(filt='24hhp'):
    """Plot and return full figure for given options."""

    # initialize figure (keep main axes for labels and inset)
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=2, sharey=True, gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 10, 'top': 2.5,
            'hspace': 10})
    subaxes = bowstr_utils.subsubplots(fig, axes)

    # add subfigure labels
    for ax, label in zip(subaxes[:, 0], ['(a)', '(b)']):
        ax.text(-0.05, 0, label, fontweight='bold', transform=ax.transAxes)

    # load filtered stress series
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(filt=filt, resample='1h', tide=True)

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

            # set axes properties
            ax.grid(False)
            ax.get_lines()[0].set_clip_box(pax.bbox)
            ax.set_ylim((-.2, .2) if filt == 'deriv' else (-2, 2))
            ax.set_yticks([-.1, .1] if filt == 'deriv' else (-1, 1))

            # stagger tick labels
            ax.tick_params(labelleft=ax.get_subplotspec().is_last_row())
            ax.yaxis.set_major_formatter(
                lambda y, pos: f'{y}' + 3 * (pos % 2) * ' ')

            # add grid on background ghost axes
            ax = fig.add_subplot(ax.get_subplotspec(), sharex=ax, sharey=ax)
            ax.grid(which='minor')
            ax.tick_params(which='both', **{k: False for k in [
                'labelleft', 'labelbottom', 'left', 'bottom']})
            ax.patch.set_visible(False)
            ax.set_zorder(-1)
            for spine in ax.spines.values():
                spine.set_visible(False)

        # set labels
        panel[4].set_ylabel(
            'stress change (Pa/s)' if filt == 'deriv' else 'stress (kPa)')
        panel[9].set_xlabel('')

    # set axes limits
    subaxes[0, 0].set_xlim('20140701', '20170801')
    subaxes[1, 0].set_xlim('20140816', '20141016')

    # remove empty headlines in date tick labels
    subaxes[1, -1].set_xticks(subaxes[1, -1].get_xticks())
    subaxes[1, -1].set_xticks(
        subaxes[1, -1].get_xticks(), [
            label.get_text().lstrip('\n') for label
            in subaxes[1, -1].get_xticklabels()])

    # mark zoom inset
    indicator = axes[0].indicate_inset(inset_ax=axes[1], ls='--')
    indicator.connectors[0].set_visible(False)
    indicator.connectors[1].set_visible(True)
    indicator.connectors[2].set_visible(False)
    indicator.connectors[3].set_visible(True)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    filters = ['12hbp', '12hhp', '24hbp', '24hhp', 'deriv'] # FIXME 'phase'
    plotter = bowstr_utils.MultiPlotter(plot, filters=filters)
    plotter()


if __name__ == '__main__':
    main()
