#!/usr/bin/env python
"""
play a movie of data within Python, here, using an HDF5 file's data  (Nimg x X x Y)
"""
import h5py
from argparse import ArgumentParser
from pathlib import Path
from matplotlib.pyplot import figure, draw, pause


def main():
    p = ArgumentParser()
    p.add_argument("infn", help="HDF5 file to analyze")
    p.add_argument("key", help="HDF5 variable to access")
    p = p.parse_args()

    fn = Path(p.infn).expanduser()

    with h5py.File(fn, "r") as f:
        imgs = f[p.key]

        ax = figure().gca()
        h = ax.imshow(imgs[0])
        for img in imgs:
            h.set_data(img)
            draw()
            pause(0.05)


if __name__ == "__main__":
    main()
