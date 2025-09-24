#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides highpass-filtered timeseries."""

from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import numpy as np
import absplots as apl
import util.str


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=2, sharey=True, gridspec_kw=dict(
            left=12.5, right=12.5, bottom=12.5, top=2.5, hspace=12.5))

    # add subfigure labels
    util.com.add_subfig_labels(axes, bbox=dict(alpha=0.85, ec='none', fc='w'))

    # highpass-filter stress series
    depth = util.str.load(variable='dept').iloc[0]
    pres = util.str.load().resample('1h').mean()
    pres = util.str.filter(pres)

    # load tide data
    tide = util.str.load_pituffik_tides().resample('1h').mean()  # kPa

    # apply transformation for plotting
    tide /= 10
    pres += 5*(1+np.arange(len(pres.columns)))[::-1]

    # plot stress and tide data
    for ax in axes:
        pres.plot(ax=ax, legend=False)
        tide.plot(ax=ax, c='C9')

        # set axes properties
        ax.grid(which='minor')
        ax.set_xlabel('')
        ax.set_ylabel('stress (kPa)')

        # add labels
        kwargs = dict(fontsize=6, fontweight='bold', transform=ax.transAxes)
        ax.text(1.01, 0, 'Pituffik\ntide'+r'$\,/\,$10', color='C9', **kwargs)
        for i, unit in enumerate(pres):
            ax.text(
                1.01, 0.9-0.1*i, unit+'\n'+r'{:.0f}$\,$m'.format(depth[unit]),
                color='C{}'.format(i), **kwargs)

    # set axes limits
    axes[1].set_ylim(-2.5, 47.5)
    axes[1].set_xlim('20140816', '20141016')

    # mark zoom inset
    mark_inset(axes[0], axes[1], loc1=1, loc2=2, ec='0.75', ls='--')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
