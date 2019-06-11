#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature borehole setup."""

import pandas as pd
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    gridspec_kw = dict(left=10, right=2.5, wspace=10, bottom=10, top=2.5)
    fig, (ax0, ax1) = apl.subplots_mm(figsize=(150, 75), ncols=2, sharex=True,
                                      gridspec_kw=gridspec_kw)

    # add subfigure labels
    util.com.add_subfig_label(ax=ax0, text='(a)')
    util.com.add_subfig_label(ax=ax1, text='(b)')

    # for each boreholes
    for bh, color in util.tem.COLOURS.items():

        # load daily means
        temp, depth, base = util.tem.load_all(bh)
        temp = temp.resample('6H').mean()

        # estimate closure dates
        closure_dates = util.tem.estimate_closure_dates(bh, temp)
        closure_temps = [temp.loc[closure_dates[k], k] for k in temp]
        closure_temps = pd.Series(index=closure_dates, data=closure_temps)

        # compute closure times
        drilling_date = util.tem.DRILLING_DATES[bh.replace('err', 'bh3')]
        drilling_date = pd.to_datetime(drilling_date)
        closure_times = closure_dates - drilling_date
        closure_times = closure_times.dt.total_seconds()/(24*3600)

        # for each sensor type
        for sensor, marker in util.tem.MARKERS.items():
            cols = closure_times.index.str[1] == sensor
            ax0.plot(closure_times[cols], temp.min(axis=0)[cols], color=color,
                     marker=marker, ls='', label=bh.upper()+sensor)
            ax1.plot(closure_times[cols], depth[cols], color=color,
                     marker=marker, ls='')

        # add baseline
        ax1.axhline(base, color=color, lw=0.5)

    # set axes properties
    ax0.legend()
    ax0.set_xscale('log')
    ax0.set_xlabel('days to freezing')
    ax0.set_ylabel(u'minimum temperature (°C)')
    ax1.set_xlabel('days to freezing')
    ax1.set_ylabel('depth (m)')
    ax1.axhline(0.0, c='k', lw=0.5)
    ax1.invert_yaxis()

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
