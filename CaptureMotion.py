#!/usr/bin/env python
"""
This script captures motion arrays from the PiCamera and saves them to an HDF5 file
"""
import picamera
import picamera.array
from pathlib import Path
import argparse
from datetime import datetime
import h5py


def main():
    p = argparse.ArgumentParser()
    p.add_argument("odir", help="output directory")
    p.add_argument("duration", help="record time length (seconds)", type=float)
    p.add_argument("-r", "--resolution", nargs=2, type=int, default=(640, 480))
    p.add_argument("-fps", type=int, default=30)
    p = p.parse_args()

    outdir = Path(p.odir).expanduser() / datetime.now().isoformat()[:-10]
    vidfn = outdir / "raw.mp4"
    motfn = outdir / "motion.h5"
    outdir.mkdir(parents=True, exist_ok=True)

    res = p.resolution

    with picamera.PiCamera() as camera:
        with picamera.array.PiMotionArray(camera) as stream:
            camera.resolution = res
            camera.framerate = p.fps
            camera.start_recording(str(vidfn), format="h264", motion_output=stream)
            camera.wait_recording(p.duration)
            camera.stop_recording()
            # convert image stack to 3-D Numpy array (Nimg x Y x X)
            imgs = stream.array

            if imgs.shape[0] == 0:
                raise ValueError(f"Record duration {p.duration} seconds may be too short")

            print("saving", imgs.shape, "motion to", outdir)

            with h5py.File(motfn, "w") as f:
                f.create_dataset("dx", data=imgs["x"], compression="gzip", compression_opts=1)
                f.create_dataset("dy", data=imgs["y"], compression="gzip", compression_opts=1)
                f["time"] = datetime.now().isoformat()


if __name__ == "__main__":
    main()
