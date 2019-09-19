#!/usr/bin/env python3
"""
This script captures motion arrays from the PiCamera and saves them to an HDF5 file
"""
import picamera
import picamera.array
from pathlib import Path
import argparse
import typing
from datetime import datetime
import h5py


def capture(video_file: Path, duration_sec: float, resolution: typing.Tuple[int, int], fps: int) -> typing.Tuple[typing.Any, str]:
    """
    capture video from Picamera
    """
    # %% acquire video data
    with picamera.PiCamera() as camera:
        with picamera.array.PiMotionArray(camera) as stream:
            camera.resolution = resolution
            camera.framerate = fps
            time = datetime.now().isoformat()
            camera.start_recording(str(video_file), format="h264", motion_output=stream)
            camera.wait_recording(duration_sec)
            camera.stop_recording()
            # imgs is a 3-D Numpy array, Nframes x X x Y
            imgs = stream.array

    if imgs.shape[0] == 0:
        raise ValueError(f"Record duration {duration_sec} seconds may be too short")

    return imgs, time


def write_hdf5(imgs, time: str, motion_file: Path):
    # %% save to HDF5 file
    with h5py.File(motion_file, "w") as f:
        f.create_dataset("dx", data=imgs["x"], compression="gzip", compression_opts=1)
        f.create_dataset("dy", data=imgs["y"], compression="gzip", compression_opts=1)
        f["time"] = time


def main(outdir: Path, duration_sec: float, resolution: typing.Tuple[int, int], fps: int) -> Path:
    outdir = Path(outdir).expanduser() / datetime.now().isoformat()[:-10].replace(":", "")
    outdir.mkdir(parents=True, exist_ok=True)

    video_file = outdir / "raw.h264"
    print("writing motion vectors to", video_file)
    imgs, time = capture(video_file, duration_sec, resolution, fps)

    motion_file = outdir / "motion.h5"
    print("saving", imgs.shape, "motion data to", motion_file)
    write_hdf5(imgs, time, motion_file)

    return outdir


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("outdir", help="output directory")
    p.add_argument("duration", help="record time length (seconds)", type=float)
    p.add_argument("-r", "--resolution", nargs=2, type=int, default=(640, 480))
    p.add_argument("-fps", type=int, default=30)
    p = p.parse_args()

    main(p.outdir, p.duration, p.resolution, p.fps)
