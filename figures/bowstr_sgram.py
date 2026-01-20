#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress spectrograms."""

import absplots as apl
import matplotlib as mpl
import numpy as np
import pandas as pd
import pywt

import bowstr_utils


def plot_cwt(series, ax):
    """Plot spectrogram from continuous wavelet transform."""

    # compute wavelet transform
    series = series.dropna()
    sampling = (series.index[1] - series.index[0]).total_seconds() / 3600
    periods = np.arange(6, 31, 1)
    scales = pywt.frequency2scale('morl', sampling / periods)
    cwt, freqs = pywt.cwt(series, scales, 'morl', sampling_period=sampling)

    # plot wavelet transform
    img = ax.imshow(
        np.abs(cwt), aspect='auto', cmap='Greys', origin='lower', vmin=0,
        vmax=np.quantile(np.abs(cwt), 0.98), extent=[
            *mpl.dates.date2num((series.index[0], series.index[-1])),
            1.5*1/freqs[0]-0.5*1/freqs[1], 1.5*1/freqs[-1]-0.5*1/freqs[-2]])

    # plot invisible timeseries to format axes as pandas
    (18+0*series.resample('1D').mean()).plot(ax=ax, visible=False)

    # set axes properties
    ax.set_yticks([12, 24])

    # return image for colorbar
    return img


def plot_fft(series, ax, color):
    """Plot spectrogram from Fast Fourier Transform."""

    # plot spectrogram (values range ca. -170 to -50)
    series = series.diff() / series.index.to_series().diff().dt.total_seconds()
    sfreq = int(pd.to_timedelta('1D') / series.index.freq)
    per, freqs, bins, img = ax.specgram(
        series, cmap='Greys', Fs=sfreq, NFFT=sfreq*14, noverlap=sfreq*12,
        xextent=mpl.dates.date2num((series.index[0], series.index[-1])),
        vmin=-150, vmax=-50)

    # plot 22-26 vs 10-14 hour bands power ratio
    pow12 = per[(24/14 <= freqs) & (freqs <= 24/10), :].sum(axis=0)
    pow24 = per[(24/26 <= freqs) & (freqs <= 24/22), :].sum(axis=0)
    index = series.index[0] + np.asarray(mpl.dates.num2timedelta(bins))
    ratio = 1 / (1 + pow24 / pow12)
    ratio = pd.Series(ratio, index=index)
    ratio = ratio.where(pow12 > 1e-15).resample('2D').mean()
    (1+ratio).plot(ax=ax, color='w', lw=2, alpha=0.5)
    (1+ratio).plot(ax=ax, color=color)

    # set axes properties
    ax.set_ylim(2.5, 0.5)
    ax.set_yticks([2, 1])
    ax.set_yticklabels(['12', '24'])

    # return image for colorbar
    return img


def plot_spectrogram(series, ax, color, method='fft'):
    """Plot spectrogram from data series."""
    func = globals().get(f'plot_{method}')
    args = (series, ax) + (color,) * (method == 'fft')
    return func(*args)


def plot(method='stfft'):
    """Plot and return full figure for given options."""

    # initialize figure
    fig, pax = apl.subplots_mm(figsize=(180, 120), gridspec_kw={
        'left': 10, 'right': 7.5, 'bottom': 10, 'top': 2.5})
    axes = bowstr_utils.subsubplots(fig, [pax], nrows=8)[0]
    cax = fig.add_axes_mm([100, 45, 60, 5])

    # load stress and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    dates = bowstr_utils.load_freezing_dates()
    df = bowstr_utils.load_spectral(resample='10min', variable=method[:2])
    df = df.drop(columns=['UI03', 'UI02'])

    # plot spectrograms and text labels
    for i, unit in enumerate(df):
        ax = axes[i]
        color = f'C{i+2*(i > 3)}'
        series = df.loc[dates.get(unit, None):, unit]
        img = plot_spectrogram(series, ax, color, method=method[2:])
        ax.text(
            1.02, 0.5, 'Pituffik\ntide'r'$\,/\,$10' if unit == 'tide' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=color,
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

    # add colorbar
    cax.figure.colorbar(img, cax=cax, orientation='horizontal')
    cax.set_xlabel(
        'continuous wavelet transform' if method[2:] == 'cwt' else
        'power spectral density')

    # set axes properties
    axes[0].set_xlim('20140701', '20170801')
    axes[4].set_ylabel('period (h)', ha='left', labelpad=0)

    # save partial (for fft only)
    # for ax in axes:
    #     for line in ax.lines:
    #         line.set_visible(False)
    # fig.savefig(f'{__file__[:-3]}_{method}_01')
    # for ax in axes:
    #     for line in ax.lines:
    #         line.set_visible(True)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    methods = ['stcwt', 'stfft', 'ticwt', 'tifft']
    plotter = bowstr_utils.MultiPlotter(plot, methods=methods)
    plotter()


if __name__ == '__main__':
    main()
