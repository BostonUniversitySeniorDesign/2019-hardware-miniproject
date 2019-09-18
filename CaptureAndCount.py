#!/usr/bin/env python3
"""
Convenience program that:

1. captures a video clip using CaptureMotion.py
2. processes that video clip using CountMotion.py

The original data files are saved so you can look at them on your laptop for debugging.
"""
import argparse
from CaptureMotion import main as capture_main
from CountMotion import main as count_main


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("outdir", help="output directory")
    p.add_argument("duration", help="record time length (seconds)", type=float)
    p.add_argument("-r", "--resolution", nargs=2, type=int, default=(640, 480))
    p.add_argument("-fps", type=int, default=30)
    p = p.parse_args()

    outdir = capture_main(p.outdir, p.duration, p.resolution, p.fps)

    motion_fn = outdir / "motion.h5"
    count_fn = outdir / "count.h5"
    count_main(motion_fn, variable_name=["dx", "dy"], outfn=count_fn, doplot=False, saveplot=None)
