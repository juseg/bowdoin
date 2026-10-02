#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation against GNSS velocity."""

import absplots as apl

import bowdef_utils
import bowstr_utils
import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=3, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
            'height_ratios': (3, 3, 1), 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # plot borehole velocity
    df = bowdef_utils.load_gnss_velocities(method='twopoint')
    df.vh.plot(ax=axes[0], color='0.9')
    df = bowdef_utils.load_multivariate()
    df.gnss.plot(ax=axes[0], color='tab:blue', legend=False)

    # plot tilt rates and tide
    df.tilt.plot(ax=axes[1], legend=False)
    (df.tide/1e1).plot(ax=axes[2], legend=False, c='C9')

    # add tilt unit legend
    depth = bowstr_utils.load(variable='dept').iloc[0]
    axes[1].legend(
        [f'{unit} ({depth[unit]:.0f}' r'$\,$m)' for unit in df.tilt],
        loc='upper right', bbox_to_anchor=(0, 0, 11/12, 1), ncol=3)

    # set axes limits
    axes[0].grid(which='minor')
    axes[1].grid(which='minor')
    axes[2].set_xlabel('')
    axes[0].set_ylabel(r'velocity ($m\,a^{-1}$)', labelpad=0)
    axes[1].set_ylabel(r'tilt rate ($°\,a^{-1}$)')
    axes[2].set_ylabel('tide / 10 (kPa)', labelpad=0)
    axes[0].set_ylim(-50, 950)
    axes[1].set_ylim(-1, 21)
    axes[2].set_ylim(-2.4, 2.4)

    # zoom on tidal oscillations
    # axes[0].set_xlim('20160801', '20161001')
    # axes[1].set_ylim(-1, 14)
    # axes[2].set_ylim(1.99, 2.14)

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
