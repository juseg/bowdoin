#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation cross spectrograms."""

import absplots as apl
import matplotlib as mpl
import numpy as np
import pywt

import bowdef_utils
import bowstr_utils


def colorize_complex_array(array):
    """Compute rgb visualization from a complex array."""

    # extract the phase and power
    power = np.abs(array)
    phase = np.angle(array, deg=True)

    # colorize (after https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_HSV)
    hue = (1/3 + phase/360) % 1  # red < green=0 < blue
    lightness = 1 - power / power.max()
    value = 2 * lightness.clip(0, 0.5)
    saturation = 2 * (1-np.divide(
        lightness, value, out=np.ones_like(lightness), where=value!=0))
    hsv = np.stack([hue, saturation, value], axis=-1)

    # return rgb image
    return mpl.colors.hsv_to_rgb(hsv)


def plot_cross_wavelet_transform(ax, series, other, wavelet='cmor1-1'):
    """Plot spectrogram from wavelet coherence transform."""

    # strip initial and final nan values and interpolate
    first = max(series.first_valid_index(), other.first_valid_index())
    last = min(series.last_valid_index(), other.last_valid_index())
    series = series.loc[first:last].interpolate(method='time')
    other = other.loc[first:last].interpolate(method='time')

    # compute cross wavelet transform
    sampling = (series.index[1] - series.index[0]).total_seconds() / 3600
    scales = pywt.frequency2scale(wavelet, sampling / np.arange(6, 31, 1))
    cwt0, freqs = pywt.cwt(series, scales, wavelet, sampling_period=sampling)
    cwt1, freqs = pywt.cwt(other, scales, wavelet, sampling_period=sampling)
    xwt = cwt0 * np.conj(cwt1)

    # plot wavelet transform
    rgb = colorize_complex_array(xwt)
    ax.imshow(rgb, aspect='auto', origin='lower', extent=[
        *mpl.dates.date2num((series.index[0], series.index[-1])),
        1.5*1/freqs[0]-0.5*1/freqs[1], 1.5*1/freqs[-1]-0.5*1/freqs[-2]])

    # plot invisible timeseries to format axes as pandas
    (18+0*series.resample('1D').mean()).plot(ax=ax, visible=False)


def plot_colorbar(cax, var, ref):
    """Plot standalone phase delay colorbar."""

    # plot 2d gradient image
    phase = np.linspace(-np.pi, np.pi, 90)
    power = np.linspace(0, 1, 21)
    rgb = colorize_complex_array(power[:, None] * np.exp(phase*1j))
    cax.imshow(rgb, aspect='auto', origin='lower', extent=[-182, 182, 0, 1])

    # set axes properties
    labels = {
        'azim': 'azimuth', 'gnss': 'speed', 'pres': 'stress', 'tide': 'tide',
        'tilt': 'tilt rate'}
    cax.set_xlabel(f'{labels[var]} vs {labels[ref]} phase delay (°)')
    cax.set_xlim(-180, 180)
    cax.set_xticks(np.linspace(-180, 180, 7))
    cax.set_yticks([])


def plot(couple='ti2sp', method='inner'):
    """Plot and return full figure for given options."""

    # correlation variables
    var = {'az': 'azim', 'sp': 'gnss', 'st': 'pres', 'tr': 'tilt'}[couple[:2]]
    ref = {'az': 'azim', 'sp': 'gnss', 'ti': 'tide', 'tr': 'tilt'}[couple[3:]]

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 10, 'right': 7.5, 'bottom': 10+37.5*(var=='gnss'), 'top': 2.5})
    cax = fig.add_axes_mm([100, 30, 60, 5], zorder=2)

    # load all variables
    depth = bowstr_utils.load(variable='dept').iloc[0]
    df = bowdef_utils.load_multivariate(filt='24hbp', join=method)
    df = df.drop(columns=['UI03', 'UI02'], level=1)

    # initialize subsubplots
    units = df[var].columns
    axes = [ax] if len(units) == 1 else bowstr_utils.subsubplots(
        ax.figure, [ax], nrows=len(units))[0]

    # for each unit
    for i, unit in enumerate(units):
        ax = axes[i]
        color = f'C{i+2*(i > 3)}'

        # plot wavelet coherence transform
        plot_cross_wavelet_transform(ax, df[var][unit], df[ref].get(unit, df[ref].squeeze()))

        # add text label
        ax.text(
            1.02, 0.5, r'surface speed ($m\,a^{-1}$)' if unit =='GNSS' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=color,
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.tick_params(labelleft=ax.get_subplotspec().is_last_row())
        ax.set_xlim('20140701', '20170801')
        ax.set_yticks([12, 24])

    # set axes properties
    axes[len(axes)//2].set_ylabel('period (h)', labelpad=6*(len(axes)>1))

    # add colorbar
    plot_colorbar(cax, var, ref)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    couples = [
        'az2sp', 'az2ti', 'sp2ti', 'st2sp', 'st2az', 'st2ti', 'st2tr',
        'tr2sp', 'tr2ti']
    plotter = bowstr_utils.MultiPlotter(plot, couples=couples)
    plotter()


if __name__ == '__main__':
    main()
