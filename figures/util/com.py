# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin common utils.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms


# Plotting methods
# ----------------

def plot_field_campaigns(ax=None, color='C1', ytext=0.0):
    """Mark 2014--2017 summer field campaigns."""

    # get axes if None provided
    ax = ax or plt.gca()

    # prepare blended transform
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)

    # for dates when people were on Bowdoin
    for start, end in [('2014-07-15', '2014-07-29'),
                       ('2015-07-06', '2015-07-20'),
                       ('2016-07-04', '2016-07-21'),
                       ('2017-07-04', '2017-07-17')]:

        # add rectangular spans
        ax.axvspan(start, end, ec='none', fc=color, alpha=0.25)

        # add text annotations
        duration = pd.to_datetime(end) - pd.to_datetime(start)
        midpoint = pd.to_datetime(start) + duration / 2
        ax.text(midpoint, ytext, midpoint.year, color=color, fontweight='bold',
                ha='center', transform=trans)


def savefig(fig=None, suffix=''):
    """Save figure to script filename."""
    fig = fig or plt.gcf()
    res = fig.savefig(os.path.splitext(sys.argv[0])[0]+suffix)
    return res
