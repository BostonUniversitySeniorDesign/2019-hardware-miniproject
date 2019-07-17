#!/usr/bin/env python
"""
from a collection of files written over time (with sequentially named files), gather and plot their data
"""
import h5py
from pathlib import Path
import numpy as np
from matplotlib.pyplot import figure, show


def main():
    path = Path(path).expanduser()
    flist = sorted(path.glob('count*.h5'))

    N = []
    i = []
    for fn in flist:
        with h5py.File(fn, 'r') as f:
            N.extend(f['count'][:])
            i.append(f['index'].value)

    ax = figure().gca()
    ax.plot(N)

    show()


if __name__ == '__main__':
    main()
