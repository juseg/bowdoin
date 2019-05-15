#!/usr/bin/env python

"""Utils and parameters for this project."""

import matplotlib.pyplot as plt

import util.al  # data analysis
import util.io  # input and output
import util.pl  # plotting tools

# temporary fix for https://github.com/pydata/xarray/issues/1661
import pandas as pd
if pd.__version__.startswith('0.21'):
    from pandas.tseries import converter
    converter.register()

# build color brewer Paired palette
colorkeys = [tone+hue
             for hue in ('blue', 'green', 'red', 'orange', 'purple', 'brown')
             for tone in ('light', 'dark')]
colorvals = plt.get_cmap('Paired', 12)(range(12))
palette = dict(zip(colorkeys, colorvals))

# borehole properties
boreholes = ['upper', 'lower']
colors = {'lower': palette['darkblue'],
          'upper': palette['darkred'],
          'dgps': palette['darkgreen']}


# Bowdoin temperature parameters
# ------------------------------

bowtem_bhdates = '20140716', '20140717', '20140722'
bowtem_bhnames = 'bh1', 'bh2', 'bh3'
bowtem_colours = 'C0', 'C1' ,'C2'
bowtem_sensors = 'I', 'T', 'P'
bowtem_markers = '^', 'o', 's'
