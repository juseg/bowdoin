#!/usr/bin/env python
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides pressure circles animation."""

import sys
import os.path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import absplots as apl

# import figure utils by relative path
# pylint: disable=import-error, no-name-in-module, wrong-import-position
sys.path.append(os.path.join('..', 'figures'))
import util.com  # noqa
import util.geo  # noqa
import util.str  # noqa
# pylint: enable=import-error, no-name-in-module, wrong-import-position
# pylint: disable=no-member


class CustomAnimation():
    """Adapted from: https://izziswift.com/how-to-animate-a-scatter-plot/."""

    def __init__(self):
        """Construct the animation."""

        # load filtered pressure series
        pres = util.str.load().resample('1H').mean()
        pres = pres['20150302':'20150329'].dropna(axis=1)
        pres = util.str.filter(pres, cutoff=1/12)
        self.pres = pres
        tide = util.str.load_pituffik_tides(unit='m').resample('1H').mean()
        self.tide = tide

        # initialize figure
        self.fig = self.setup()
        self.update(pres.index[0])

        # setup funcanimation
        self.ani = mpl.animation.FuncAnimation(
            self.fig, self.update, blit=True, frames=pres.index,
            interval=1000/25)

    def preview(self, filename):
        """Save the initial animation frame as a figure."""
        self.fig.savefig(filename)

    def setup(self):
        """Draw boreholes long profile with intrumental setup."""

        # initialize figure
        fig, ax = apl.subplots_mm(figsize=(96, 54), dpi=508)

        # plot vertical lines symbolising the boreholes
        locations = util.geo.read_locations_dict('../data/locations.gpx')
        for bh in ('bh1', 'bh3'):
            surf = locations['B14'+bh.upper()].elevation
            base = surf - util.com.load_file(
                '../data/processed/bowdoin.{}.inc.base.csv'.format(bh)
                ).iloc[0].squeeze()
            dist = dict(bh1=2, bh3=1.84)[bh]
            ax.plot([dist, dist], [base, surf], 'k-_')

        # add scatter plot
        elev = surf - util.str.load(variable='dept').iloc[0]
        elev = elev[self.pres.columns]
        dist = 1.84 + elev.index.to_series().str.startswith('U') * 0.16
        colors = plt.get_cmap('tab10')(range(len(elev)))
        self.scatter = ax.scatter(dist, elev, c=colors, alpha=0.75)
        for i, unit in enumerate(elev.index):
            color = 'C%d' % i
            ax.text(dist[i]+0.02, elev[unit], unit, color=color,
                    fontweight='bold', va='center')

        # add sea level
        self.sealevel = ax.axhline(
            0, color='tab:blue', label='Pituffik tide x10')

        # add date tag
        self.datetag = ax.text(
            0.98, 0.04, '', ha='right', transform=ax.transAxes)

        # add flow direction arrow
        ax.text(0.9, 0.45, 'ice flow', ha='center', transform=ax.transAxes)
        ax.annotate('', xy=(0.85, 0.4), xytext=(0.95, 0.4),
                    xycoords=ax.transAxes, textcoords=ax.transAxes,
                    arrowprops=dict(arrowstyle='->', lw=1.0))

        # set axes properties
        ax.set_xlim(1.78, 2.18)
        ax.set_xticks([1.84, 2.0])
        ax.set_xticklabels(['BH3', 'BH1'])
        ax.set_ylabel('initial altitude (m)', labelpad=2)
        ax.set_title('Bowdoin Glacier stress anomalies')
        ax.legend()
        ax.grid(False, axis='x')

        # return figure
        return fig

    def update(self, date):
        """Update the scatter plot."""

        # update scatter plot
        sizes = 64 + 32*self.pres.loc[date]
        sizes = np.clip(sizes, 0, 128)
        self.scatter.set_sizes(sizes)

        # update tidal sea level
        self.sealevel.set_ydata([self.tide.loc[date]*10]*2)

        # update date tag
        self.datetag.set_text(date)

        return self.scatter, self.sealevel


def main():
    """Main program called during execution."""
    ani = CustomAnimation()
    ani.preview(__file__[:-3] + '_main.png')
    ani.ani.save(__file__[:-3] + '_main.mp4')


if __name__ == '__main__':
    main()
