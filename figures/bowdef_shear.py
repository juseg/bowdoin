#!/usr/bin/env python
# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation shear profiles."""


import absplots as apl
import matplotlib as mpl
import numpy as np

import bowstr_utils


def powerfit(x, y, deg, **kwargs):
    """Fit to a power law."""
    logx = np.log(x)
    logy = np.log(y)
    p = np.polyfit(logx, logy, deg, **kwargs)
    return p


def glenfit(base, depth, exz, g=9.80665, rhoi=910.0, slope=0.03):
    """Fit to a power law with exp(C) = A * (rhoi*g*slope)**n."""
    # FIXME: the slope (sin alpha) is an approximate value from MEASURES
    # FIXME: this results in very variable and sometimtes even negative values
    # for n. The negative values cause divide by zero encountered in power
    # runtime warnings in vsia(). A better approach would be to fix n = 3 and
    # fit for C only
    n, C = powerfit(depth, exz, 1)
    A = np.exp(C) / (rhoi*g*slope)**n
    A *= base**n  # bugfix
    return n, A


def vsia(depth, depth_base, n, A, g=9.80665, rhoi=910.0, slope=0.03):
    """Return simple horizontal shear velocity profile."""
    C = A * (rhoi*g*slope)**n
    C /= depth_base**n  # bugfix
    v = 2*C/(n+1) * (depth_base**(n+1) - depth**(n+1))
    return v


def plot_shear_profile(ax, base, depth, strain, color='tab:blue'):
    """Fit and plot tilt velocity profile."""

    # compute discrete and extrapolated shear profiles
    exponent, softness = glenfit(base, depth, strain)
    depth_int = np.linspace(0, base, 51)
    shear_int = vsia(depth_int, base, exponent, softness)
    shear = vsia(depth, base, exponent, softness)

    # plot interpolated shear profile
    ax.fill_betweenx(depth_int, 0, shear_int, color=color, alpha=0.25)
    ax.plot(shear_int, depth_int, color=color)
    ax.plot([0, shear_int[0]], [0, 0], color=color)
    ax.plot([0, 0], [base, 0], 'k-_')

    # plot unit markers (FIXME unit colors)
    for i, unit in enumerate(depth.index):
        bbox = ax.get_window_extent()
        ratio = bbox.width / bbox.height * ax.get_data_ratio()
        angle = np.arctan(2*strain[unit]*ratio)
        vertices = [(1, 2), (-1, 2), (-1, -2), (1, -2), (1, 2)]
        transform = mpl.transforms.Affine2D().rotate_deg(angle * 180 / np.pi)
        marker = mpl.markers.MarkerStyle(vertices, transform=transform)
        ax.plot(shear[unit], depth[unit], mec=color, marker=marker, ms=20)
        offset = np.sin(angle) + 0.5 * np.cos(angle)
        ax.annotate(
            '', xy=(shear[unit] - offset, depth[unit]),
            xytext=(0, depth[unit]), arrowprops={
                'arrowstyle': '-|>', 'color': color, 'linewidth': 1,
                'linestyle': 'dashed'})

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
    costilt = np.cos(tilx) * np.cos(tily)
    strain = 0.5 * (1 - costilt**2) ** 0.5 / costilt

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
