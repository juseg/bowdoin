#!/usr/bin/env python
# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation shear profiles."""


import absplots as apl
import matplotlib as mpl
import numpy as np

import bowstr_utils


def compute_power_fit(depth, strain):
    """Fit to a power law strain = constant * depth ** exponent."""
    exponent, constant = np.polyfit(np.log(depth), np.log(strain), 1)
    return exponent, np.exp(constant)


def compute_shear_profile(base, depth, exponent, constant):
    """Compute horizontal shear profile from fitted exponent and constant."""
    power = exponent + 1
    shear = 2 * constant / power * (base**power - depth**power)
    return shear


def plot_shear_profile(ax, base, depth, strain, color='tab:blue'):
    """Fit and plot tilt velocity profile."""

    # compute and plot discrete and extrapolated shear profiles
    exponent, constant = compute_power_fit(depth, strain)
    depth_int = np.linspace(0, base, 51)
    shear_int = compute_shear_profile(base, depth_int, exponent, constant)
    shear = compute_shear_profile(base, depth, exponent, constant)
    plot_shear_profile_lines(ax, base, depth_int, shear_int, color=color)
    plot_shear_profile_markers(ax, depth, shear, strain, color=color)

    # print total shear and surface motion fraction for EGU26 abstract
    # print(shear_int[0], shear_int[0] / 356.412 * 100)

    # add fit values
    ax.text(
        shear_int[0]-1, 20, f'n = {exponent:.2f}', color=color,
        fontweight='bold')


def plot_shear_profile_lines(ax, base, depth, shear, color='C0'):
    """Plot and fill continuous shear profile line."""
    ax.fill_betweenx(depth, 0, shear, color=color, alpha=0.25)
    ax.plot(shear, depth, color=color)
    ax.plot([0, shear[0]], [0, 0], color=color)
    ax.plot([0, 0], [base, 0], 'k-_')


def plot_shear_profile_markers(ax, depth, shear, strain, color='C0'):
    """Mark tilt units on shear profile with rotated rectangles."""
    for i, unit in enumerate(depth.index):
        unit_color = f'C{i+int(color[1])}'
        bbox = ax.get_window_extent()
        ratio = bbox.width / bbox.height * ax.get_data_ratio()
        angle = np.arctan(2*strain[unit]*ratio)
        vertices = [(1, 2), (-1, 2), (-1, -2), (1, -2), (1, 2)]
        transform = mpl.transforms.Affine2D().rotate_deg(angle * 180 / np.pi)
        marker = mpl.markers.MarkerStyle(vertices, transform=transform)
        ax.plot(
            shear[unit], depth[unit], color=unit_color, mec=color,
            marker=marker, ms=20)
        offset = np.sin(angle) + 0.5 * np.cos(angle)
        ax.annotate(
            '', xy=(shear[unit] - offset, depth[unit]),
            xytext=(0, depth[unit]), arrowprops={
                'arrowstyle': '-|>', 'color': color, 'linewidth': 1,
                'linestyle': 'dashed'})


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
        plot_shear_profile(
            ax, base[f'{bh}B'], depth[mask], strain[mask], color=color)
        ax.text(1, 20, bh, color=color, fontweight='bold', ha='right')
        ax.xaxis.set_inverted(True)
        ax.yaxis.set_inverted(True)

    # set axes properties
    axes[0].set_xlabel(f'shear deformation from {start} to {end} (m)').set_x(1)
    axes[0].set_ylabel('depth (m)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
