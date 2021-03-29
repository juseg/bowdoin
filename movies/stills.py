#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Assemble bumbers for Bowdoin Glacier animation."""

# NOTE: this is virtually the same script as for the Cordillera project.

import os.path
import argparse
import subprocess
import yaml
import requests
import matplotlib.pyplot as plt


def bumper_init():
    """Init figure and axes for animation bumper."""
    fig = plt.figure(figsize=(192.0/25.4, 108.0/25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('k')
    ax.set_xlim(-96, 96)
    ax.set_ylim(-54, 54)
    return fig, ax


def bumper_main(prefix, info, subtitle=None):
    """Prepare title animation bumper."""

    # initialize figure
    fig, ax = bumper_init()

    # draw text
    ax.text(0, 24, info['Title'], color='1.0', fontsize=18,
            ha='center', va='center', linespacing=1.5)
    ax.text(0, -8, info['Author'], ha='center', va='center')
    ax.text(-80, -40, info['Credit'], linespacing=1.5)

    # add subtitle
    if subtitle not in (None, 'none'):
        ax.text(0, 8, info['Subtitle'][subtitle], ha='center', va='center')

    # save
    fig.savefig(prefix+'_head.png')
    plt.close(fig)


def bumper_bysa(prefix, info):
    """Prepare CC-BY-SA animation bumper."""

    # initialize figure
    fig, ax = bumper_init()

    # create icons directory if missing
    if not os.path.isdir('icons'):
        os.mkdir('icons')

    # retrieve icons if missing
    for icon in ['cc', 'by', 'sa']:
        url = 'https://mirrors.creativecommons.org/presskit/icons/'+icon+'.svg'
        pngpath = 'icons/' + icon + '.png'
        svgpath = 'icons/' + icon + '.svg'
        if not os.path.isfile('icons/{}.svg'.format(icon)):
            text = requests.get(url).text
            text = text.replace('FFFFFF', '000000')
            text = text.replace('path', 'path fill="#bfbfbf"')
            with open(svgpath, 'w') as svgfile:
                svgfile.write(text)

        # prepare cc icon bitmaps
        cmd = 'inkscape {} -w 640 -h 640 --export-filename={}'
        if not os.path.isfile(pngpath):
            subprocess.call(cmd.format(svgpath, pngpath).split(' '))

    # add cc icons
    ax.imshow(plt.imread('icons/cc.png'), extent=[-56, -24, -4, 28])
    ax.imshow(plt.imread('icons/by.png'), extent=[-16, +16, -4, 28])
    ax.imshow(plt.imread('icons/sa.png'), extent=[+24, +56, -4, 28])

    # draw text
    ax.text(0, -20, info['License text'], ha='center')
    ax.text(0, -32, info['License link'], ha='center',
            weight='bold', family=['DeJaVu Sans'])

    # save
    fig.savefig(prefix+'_bysa.png')
    plt.close(fig)


def bumper_disc(prefix, info):
    """Prepare disclaimer animation bumper."""

    # initialize figure
    fig, ax = bumper_init()

    # draw text
    ax.text(0, 0, info['Disclaimer'], ha='center', va='center',
            linespacing=3.0)

    # save
    fig.savefig(prefix+'_disc.png')
    plt.close(fig)


def bumper_refs(prefix, info):
    """Prepare references animation bumper."""

    # initialize figure
    fig, ax = bumper_init()

    # draw text
    col1 = ''
    col2 = ''
    col3 = ''
    for category, contents in info['References'].items():
        keys, _, refs = list(zip(*[item.partition('  ') for item in contents]))
        col1 += '\n' + category + ' :' + '\n'*len(contents)
        col2 += '\n' + '\n'.join(keys) + '\n'
        col3 += '\n' + '\n'.join(refs) + '\n'
    ax.text(-56, 0, col1, linespacing=1.5, va='center', ha='right')
    ax.text(-48, 0, col2, linespacing=1.5, va='center', ha='left')
    ax.text(+80, 0, col3, linespacing=1.5, va='center', ha='right')

    # save
    fig.savefig(prefix+'_refs.png')
    plt.close(fig)


def main():
    """Main program for command-line execution."""

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('metafile', help='YAML metadata filename')
    parser.add_argument('--height', default=1080, type=int,
                        help='animation vertical resolution')
    parser.add_argument('--subtitle', help='subfield containing subtitle')
    args = parser.parse_args()

    # set default font properties
    plt.rc('axes', grid=False)
    plt.rc('figure', dpi=args.height/108*25.4)
    plt.rc('font', size=12)
    plt.rc('text', color='0.75')

    # import text elements
    with open(args.metafile) as metafile:
        info = yaml.safe_load(metafile)

    # assemble bumpers
    prefix = args.metafile.replace('.yaml', '')
    bumper_main(prefix, info, subtitle=args.subtitle)
    bumper_bysa(prefix, info)
    bumper_disc(prefix, info)
    bumper_refs(prefix, info)


if __name__ == '__main__':
    main()
