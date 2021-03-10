#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides pressure time series."""

from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import pandas as pd
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax0 = apl.subplots_mm(figsize=(180, 120), gridspec_kw=dict(
        left=12.5, right=2.5, bottom=12.5, top=2.5))
    insets = fig.subplots_mm(ncols=2, gridspec_kw=dict(
        left=52.5, right=5, bottom=85, top=5, wspace=2.5))

    # plot tilt unit water level
    depth = util.tid.load_inc('dept').iloc[0]
    freq = pd.to_timedelta('1D')/24  # needed for x-axis alignment
    pres = util.tid.load_inc('wlev').resample(freq).mean()/1e3
    for ax in (ax0, *insets):
        pres.plot(ax=ax, legend=False)

    # plot freezing dates
    # temp = util.tid.load_inc('temp')['20140717':].resample('1H').mean()
    # date = abs(temp-(0.1*temp.max()+0.9*temp.min())).idxmin()
    # for ax in (ax0, ax1):
    #     ax.plot(date, [pres.loc[date[k], k] for k in date.index], 'k+')

    # add unit labels
    offsets = dict(LI05=-4, UI02=4, UI03=-12)
    for i, unit in enumerate(pres):
        last = pres[unit].dropna().tail(1)
        ax0.annotate(
            r'{}, {:.0f}$\,$m'.format(unit, depth[unit]),
            color='C{}'.format(i), fontsize=6, fontweight='bold',
            xy=(last.index[0], last), xytext=(4, offsets.get(unit, 0)),
            textcoords='offset points', ha='left', va='center')

    # add campaigns
    util.com.plot_field_campaigns(ax=ax0, ytext=0.01)

    # set main axes properties
    ax0.set_xlabel('')
    ax0.set_ylabel('pressure (MPa)')
    ax0.set_xlim('20140615', '20171215')

    # set inset axes limits
    insets[0].set_xlim('20140901', '20141001')
    insets[0].set_ylim(1.15, 1.55)
    insets[1].set_xlim('20140906', '20140916')
    insets[1].set_ylim(1.28, 1.40)
    insets[1].set_xlim('20140922', '20140930')
    insets[1].set_ylim(1.42, 1.50)

    # remove ticks, add grid
    for ax in insets:
        ax.set_xticklabels([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.grid(which='minor')

    # mark insets
    mark_inset(ax0, insets[0], loc1=2, loc2=4, ec='0.75', ls='--')
    mark_inset(insets[0], insets[1], loc1=2, loc2=3, ec='0.75', ls='--')

    # save default
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
