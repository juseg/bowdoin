#!/usr/bin/env python2

import matplotlib.pyplot as plt
import util as ut

if __name__ == '__main__':

    # initialize figure
    fig, ax = plt.subplots()

    # plot histogram
    filename = '../data/satellite/bowdoin-landsat/16072015_17082015.tif'
    data, extent = ut.io.open_gtif(filename)
    ax.hist(data.flatten(), bins=range(0,451,1), ec='none', fc=ut.palette['darkorange'])

    # save
    ut.pl.savefig(fig)
