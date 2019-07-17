#!/usr/bin/env python
"""
It's useful to write files periodically, so that a crash or power loss doesn't wipe out all collected data
"""
import h5py
from pathlib import Path
from datetime import datetime


def main():

    for i, img in enumerate(imgs):
        if i and not i % 10:
            countfn = PATH / ('count' + datetime.now().isoformat()[:-7] + '.h5')
            with h5py.File(countfn, 'w') as f:
                f['count'] = Ncount
                f['index'] = i
            Ncount = []
