#!/usr/bin/env python2

import matplotlib.pyplot as plt
import bowdef_utils

if __name__ == '__main__':

    # initialize figure
    fig, ax = plt.subplots()

    # plot histogram
    filename = '../data/satellite/bowdoin-landsat/16072015_17082015.tif'
    data, extent = bowdef_utils.open_gtif(filename)
    ax.hist(data.flatten(), bins=range(0,451,1), ec='none', fc=bowdef_utils.palette['darkorange'])

    # save
    bowdef_utils.savefig(fig)
