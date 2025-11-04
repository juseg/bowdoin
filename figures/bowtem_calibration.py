#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature calibration curves."""

import numpy as np
import matplotlib.pyplot as plt
import absplots as apl


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw=dict(
        left=12.5, right=2.5, bottom=12.5, top=2.5))

    # for each borehole
    for bh in ['bh1', 'bh3']:
        cmap = dict(bh1='Blues', bh3='Greens')[bh]
        site = dict(bh1='U', bh3='L')[bh]
        logger = dict(bh1='Th-Bowdoin-2', bh3='Th-Bowdoin-1')[bh]

        # input file name
        cfilename = '../data/original/temperature/%s_Coefs.dat' % logger

        # read rearranged calibration coefficients
        # sensor order lower: BH2A[1-9] + BH2B[1-7],
        #              upper: BH1A[1-9] + BH1B[1-4,7,5-6].
        coefs = np.loadtxt(cfilename)
        cmap = plt.get_cmap(cmap, coefs.shape[0])

        # compute temperature from resistance
        res = np.linspace(20, 40, 101)
        for i, (cf1, cf2, cf3) in enumerate(coefs):
            temp = 1 / (cf1 + cf2*np.log(res) + cf3*np.log(res)**3) - 273.15
            ax.plot(
                res, temp, color=cmap(i), lw=0.5, label=f'{site}T{i+1:02d}')

    # set axes properties
    ax.set_xlabel(r'resistance ($k\Omega$)')
    ax.set_ylabel(u'temperature (°C)')
    ax.legend(ncol=4)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
