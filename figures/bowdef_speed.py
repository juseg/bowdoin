#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation against GNSS velocity."""

import absplots as apl

import bowdef_utils
import bowdef_shear  # FIXME move imports to utils
import bowstr_utils
import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=3, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 12.5, 'top': 2.5,
            'height_ratios': (1, 1, 1), 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # load strain rates and speed
    strain = bowdef_utils.load_strain_rates(method='savgol', window='12h')
    speed = bowdef_utils.load_gnss_velocities(method='savgol', window='12h').vh
    depth = bowstr_utils.load(variable='dept').iloc[0]
    base = bowstr_utils.load(variable='base').iloc[0]

    # limit to a given period
    strain = strain.loc['20150516':'20150815']  # 2015 full gnss record

    # reindex to intersection
    index = strain.index.join(speed.index, how='inner')
    speed = speed.reindex(index).interpolate(limit=2, method='time')
    strain = strain.reindex(index).interpolate(limit=2, method='time')

    # subset for testing
    strain = strain.drop(columns=['UI03', 'UI02'])
    depth = depth.drop(index=['UI03', 'UI02'])

    # plot surface speed
    speed.plot(ax=axes[0], color='tab:blue')

    # for each borehole
    for bh in ('BH3', 'BH1'):
        mask = depth.index.str.startswith('U' if bh == 'BH1' else 'L')

        # compute shear and basal speed
        coefs = strain.apply(
            lambda s: bowdef_shear.compute_power_fit(depth[mask], s[mask]), axis=1)
        exponent = coefs.apply(lambda t: t[0])
        constant = coefs.apply(lambda t: t[1])
        power = exponent + 1
        shear = 2 * constant / power * base[f'{bh}B']**power
        basal = speed - shear
        ratio = shear / speed

        # plot shear and basal speeds
        color = f'C{mask.argmax()}'
        shear.plot(ax=axes[1], color=color)
        ratio.plot(ax=axes[2], color=color)

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
