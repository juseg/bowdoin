#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature borehole setup."""

import cartowik.decorations as cde
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    gridspec_kw = dict(left=12.5, right=2.5, wspace=12.5, bottom=12.5, top=2.5)
    fig, (ax0, ax1) = apl.subplots_mm(figsize=(180, 90), ncols=2, sharex=True,
                                      gridspec_kw=gridspec_kw)

    # add subfigure labels
    cde.add_subfig_label(ax=ax0, text='(a)')
    cde.add_subfig_label(ax=ax1, text='(b)')

    # for each boreholes
    for bh, color in util.tem.COLOURS.items():

        # load daily means
        temp, depth, base = util.tem.load_all(bh)
        temp = temp.resample('6H').mean()

        # estimate closure times
        closure_times = util.tem.estimate_closure_state(bh, temp).time
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
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
