#!/usr/bin/env python
"""
HDF5 is a convenient, performant way to store raw data to disk for later processing.
For preview purposes, it can be convenient to convert the HDF5 data to AVI using this program.
To make the side-by-side video as show at: https://www.youtube.com/watch?v=IjHmZZMT9O4

./hdf2avi.py motion.h5 motion    # creates motion.avi from motion.h5

ffmpeg -i motion.avi -vf scale=640:480 -c:v ffv1 motion640.avi

ffmpeg -i motion640.avi -i raw.mp4 -filter_complex hstack out.avi
"""
import h5py
import imageio
import numpy as np
from pathlib import Path
from argparse import ArgumentParser


def main():
    p = ArgumentParser()
    p.add_argument('infn', help='HDF5 file to convert')
    p.add_argument('key', help='HDF5 variable to convert (3D)')
    p.add_argument('-o', '--outfn', help='output filename (ending in .avi)')
    p.add_argument('-fps', help='frames/second', type=int, default=25)
    p = p.parse_args()

    infn = Path(p.infn).expanduser()
    if p.outfn:
        outfn = Path(p.outfn).expanduser()
    else:
        outfn = infn.with_suffix('.avi')

    with h5py.File(infn, 'r') as f:
        dat = f[p.key][:]

    print('writing', dat.shape, outfn)
    imageio.mimwrite(outfn, dat.astype(np.uint8), codec='ffv1', fps=p.fps)


if __name__ == '__main__':
    main()
