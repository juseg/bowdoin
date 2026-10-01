#!/usr/bin/env python
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides pressure circles animation."""

import absplots as apl
import geopandas as gpd
import matplotlib as mpl
import matplotlib.animation
import numpy as np

import bowstr_utils


class CustomAnimation():
    """Adapted from: https://izziswift.com/how-to-animate-a-scatter-plot/."""

    def __init__(self):
        """Construct the animation."""

        # load filtered pressure series
        pres = bowstr_utils.load().resample('1h').mean()
        pres = pres['20150302':'20150329'].dropna(axis=1)
        pres = bowstr_utils.butter(pres, cutoff=1/12)
        self.pres = pres
        tide = bowstr_utils.load_pituffik_tides(unit='m').resample('1h').mean()
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
        locations = gpd.read_file('../data/locations.gpx', layer='waypoints')
        surf = locations.set_index('name').ele[['B14BH1', 'B14BH3']]
        surf = surf.set_axis(['U', 'L'])
        base = bowstr_utils.load(variable='base').iloc[0]
        base = base.set_axis(base.index.str[2].map({'1': 'U', '3': 'L'}))
        dist = {'U': 2, 'L': 1.84}
        for bh in ('U', 'L'):
            ax.plot([dist[bh]]*2, [surf[bh]-base[bh], surf[bh]], 'k-_')

        # add scatter plot
        depth = bowstr_utils.load(variable='dept').iloc[0][self.pres.columns]
        elev = surf[depth.index.str[0]].values - depth
        dist = depth.index.str[0].map(dist).to_series(index=depth.index)
        colors = mpl.color_sequences['tab10'][:len(elev)]
        self.scatter = ax.scatter(dist, elev, c=colors, alpha=0.75)
        for unit, color in zip(elev.index, colors):
            ax.text(dist[unit]+0.02, elev[unit], unit, color=color,
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
