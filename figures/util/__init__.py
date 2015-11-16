#!/usr/bin/env python2
# coding: utf-8

"""Utils and parameters for this project."""

import io
import pl

# the color brewer Paired palette
# light/drak blue, green, red, orange, purple, brown
palette = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
           '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928']

# borehole properties
boreholes = ['downstream', 'upstream']
colors = palette[1], palette[5], palette[3]  # the third color for GPS
