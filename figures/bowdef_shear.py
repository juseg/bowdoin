#!/usr/bin/env python
# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation shear profiles."""


import absplots as apl
import numpy as np

import bowdef_utils
import bowstr_utils


def plot_shear_profile(ax, base, depth, strain, color='tab:blue'):
    """Fit and plot tilt velocity profile."""

    # compute discrete and extrapolated shear profiles
    exponent, softness = bowdef_utils.glenfit(depth, strain)
    depth_int = np.linspace(0, base, 51)
    shear_int = bowdef_utils.vsia(depth_int, base, exponent, softness)
    shear = bowdef_utils.vsia(depth, base, exponent, softness)

    # plot interpolated shear profile
    ax.plot(shear_int, depth_int, c=color)
    ax.fill_betweenx(depth_int, 0, shear_int, color=color, alpha=0.25)

    # plot displacement and tilt arrows at unit locations
    for d, s in zip(depth, shear):
        ax.arrow(
            0, d, s, 0, fc='none', ec=color, head_width=5, head_length=1,
            length_includes_head=True)
    ax.quiver(shear, depth, -strain*2, np.sqrt(1-(2*strain)**2),
              angles='xy', scale=5.0)

    # add horizontal lines
    ax.axhline(0, color='0.25', linestyle='dashed')
    ax.axhline(base, color='0.25', linestyle='dashed')
    # ax.plot([0, 0], [base, 0], 'k-_')

    # add fit values
    ax.text(
        0.05, 0.05,
        f'A={softness:.2e}'r'$\,Pa^{-n}\,s^{-2}$, 'f'n={exponent:.2f}',
        transform=ax.transAxes)


def main(start='2014-11-01', end='2015-11-01'):
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
        plot_shear_profile(ax, base[f'{bh}B'], depth[mask], strain[mask], color=color)
        ax.text(4, 20, bh, color=color, fontweight='bold')
        ax.xaxis.set_inverted(True)
        ax.yaxis.set_inverted(True)

    # set axes properties
    axes[0].set_xlabel(f'shear deformation from {start} to {end} (m)').set_x(1)
    axes[0].set_ylabel('depth (m)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
