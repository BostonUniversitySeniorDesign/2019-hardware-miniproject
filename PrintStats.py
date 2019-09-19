#!/usr/bin/env python3
"""
Assuming that an HDF5 motion file and raw video correspond to each other give statistics.

For simplicity, we assume the filenames are path/motion.h5 and path/raw.h264
"""
from pathlib import Path
import h5py
import cv2
import numpy as np
import argparse
import sys

p = argparse.ArgumentParser()
p.add_argument("path", help="path to where motion.h5 and raw.h264 are")
p.add_argument("raw", help="optionally, specify location of motion.h5 and raw.h264 individually", nargs="?")
P = p.parse_args()

path = Path(P.path).expanduser()
if path.is_dir():
    h5fn = path / "motion.h5"
    rawfn = path / "raw.h264"
elif path.is_file():
    h5fn = path
    if P.raw:
        rawfn = Path(P.raw).expanduser()
    else:
        rawfn = None
else:
    raise FileNotFoundError(f"{path} is not a directory or file")

with h5py.File(h5fn) as f:
    dx = f["dx"][:]
    dy = f["dy"][:]

assert dx.shape[0] == dy.shape[0], "dx frames != dy frames"

motion_mag = np.hypot(dx, dy)

if motion_mag.max() == 0:
    print("ERROR: no motion at all was seen in", h5fn)

print("Average motion magnitude across all frames", motion_mag.mean())

if rawfn:
    hv = cv2.VideoCapture(str(rawfn))
    if hv is None:
        print("ERROR: OpenCV could not read", rawfn, file=sys.stderr)
    Nraw = 0
    imgs = []
    while True:
        ret, img = hv.read()
        if not ret:
            break
        imgs.append(img)
        Nraw += 1
    if Nraw != dx.shape[0]:
        print(
            f"WARNING: video length {Nraw} doesn't match motion length {dx.shape[0]}."
            f"Are these from the same experiment?  {rawfn}  {h5fn}",
            file=sys.stderr,
        )

    imgs = np.asarray(imgs)
    print("Average video brightness", imgs.mean())
