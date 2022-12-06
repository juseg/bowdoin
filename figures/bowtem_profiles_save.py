#!/usr/bin/env python
# Copyright (c) 2019-2022, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin simple temperature profiles and save to csv."""

import pandas as pd
import absplots as apl
import util.tem


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(
        figsize=(90, 90), sharey=True, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=2.5))

    # for each borehole excluding 'err'
    for bh in ['bh1', 'bh2', 'bh3']:

        # load bowtem paper profiles
        temp, depth, base = util.tem.load_profiles(bh)

        # take only the first date
        temp = temp.iloc[:, 0]

        # plot profile
        ax.plot(temp, depth)

        # combine depth and temp in a dataframe
        profile = pd.DataFrame({'d': depth, 't': temp})

        # save dropping the index (sensor name)
        profile.to_csv(f'{__file__[:-3]}_{bh}_{temp.name}.csv', index=False)

    # set axes properties
    ax.invert_yaxis()
    ax.set_ylabel('initial sensor depth (m)')
    ax.set_xlabel(u'ice temperature (°C)')
    ax.set_xlim(-11.5, 0.5)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
