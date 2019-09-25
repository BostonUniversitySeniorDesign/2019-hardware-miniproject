#!/usr/bin/env python3
"""
Prints HDF5 variable names. Also works for Matlab 7.3 .mat files
"""
import h5py
import argparse
from pathlib import Path


p = argparse.ArgumentParser(description="print all variable names in an HDF5 file.")
p.add_argument("filename", help="HDF5 filename")
P = p.parse_args()


def print_key(name: str, obj):
    if obj.file.filename.endswith(".mat"):
        if "#refs#" in obj.name:
            return
    try:
        print(name, obj.dtype, obj.shape)
    except AttributeError:
        pass


with h5py.File(Path(P.filename).expanduser()) as f:
    f.visititems(print_key)
