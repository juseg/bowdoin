#!/usr/bin/env python
# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation shear profiles."""


import absplots as apl
import numpy as np

import bowdef_utils
import bowstr_utils

# dates to plot
start = '2014-11-01'
end = '2015-11-01'


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 90), ncols=2, sharex=True, sharey=True, gridspec_kw={
            'left': 15, 'bottom': 10, 'right': 2.5, 'top': 2.5, 'wspace': 2.5})

    # load total strain (do we need an util)
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]
    tilx = bowstr_utils.load(variable='tilx')
    tily = bowstr_utils.load(variable='tily')
    tilx = tilx.loc[end].mean() - tilx.loc[start].mean()
    tily = tily.loc[end].mean() - tily.loc[start].mean()
    strain = (1 - (np.cos(tilx) * np.cos(tily)) ** 2) ** 0.5

    # plot velocity profile
    for ax, bh in zip(axes, ('BH3', 'BH1')):
        mask = strain.notnull() & strain.index.str.startswith(
            'U' if bh == 'BH1' else 'L')
        color = f'C{mask.argmax()}'
        bowdef_utils.plot_vsia_profile(
            depth[mask], strain[mask], base[f'{bh}B'], ax=ax, c=color)
        ax.text(4, 20, bh, color=color, fontweight='bold')

    # set axes properties
    ax.xaxis.set_inverted(True)
    ax.yaxis.set_inverted(True)

    # add common labels
    figw, figh = fig.get_size_inches()*25.4
    xlabel = 'total ice deformation from %s to %s (m)' % (start, end)
    fig.text(0.5, 2.5/figh, xlabel, ha='center')
    fig.text(2.5/figw, 0.5, 'depth (m)', va='center', rotation='vertical')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
