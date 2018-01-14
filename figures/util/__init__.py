#!/usr/bin/env python2
# coding: utf-8

"""Utils and parameters for this project."""

import matplotlib.pyplot as plt

import al
import io
import pl

# temporary fix for https://github.com/pydata/xarray/issues/1661
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
