#!/usr/bin/env python
import h5py
from argparse import ArgumentParser
from pathlib import Path
import configparser
import numpy as np
import typing

try:
    from matplotlib.pyplot import figure, pause
except ImportError:
    figure = None

config_fn = Path(__file__).parent / "config.ini"

# %% user parameters, depend on camera perspective vs. lanes of traffic.
# these are for mostly horizontal traffic flow near bottom of image
# use plots to empirically adjust
ilanes = [(25, 27), (35, 40)]
max_cumulative = 100
max_psd = 1000


def main():
    p = ArgumentParser()
    p.add_argument("infn", help="HDF5 motion file to analyze")
    p.add_argument("key", help="HDF5 variable name with motion data")
    p.add_argument("-i", "--start", help="starting frame of video to process", type=int, default=0)
    p.add_argument("-o", "--outfn", help="write car counts to disk")
    p.add_argument("-q", "--noplot", help="do not make plots (save CPU)", action="store_false")
    p.add_argument("-s", "--saveplot", help="preview save name")
    p = p.parse_args()

    doplot = p.noplot and figure is not None

    fn = Path(p.infn).expanduser()
    # %% read user parameter
    C = configparser.ConfigParser()
    C.read_string(config_fn.read_text(), source=str(config_fn))
    detect_max = C.getfloat("DEFAULT", "detect_max")
    detect_min = C.getfloat("DEFAULT", "detect_min")
    noise_min = C.getfloat("DEFAULT", "noise_min")
    count_interval_seconds = C.getfloat("DEFAULT", "count_interval_seconds")
    video_fps = C.getfloat("DEFAULT", "video_fps")

    frame_count_interval = int(video_fps * count_interval_seconds)

    with h5py.File(fn, "r") as f:
        mot = np.rot90(f[p.key][p.start:].astype(np.uint8), axes=(1, 2))
    # %% approximate elapsed time
    time = np.arange(0, mot.shape[0] / video_fps, count_interval_seconds)
    # %% discard background motion "noise"
    bmot = mot > noise_min
    # %% create figure
    CarCount = np.zeros(time.size, dtype=int)
    j = 0
    L = mot.shape[-1]
    iLPF = (int(L * 4 / 9), int(L * 5.2 / 9))
    h = fig_create(doplot, mot[0], iLPF, detect_min, detect_max, time, CarCount)
    # %% main program loop over each frame of motion data
    for i, m in enumerate(bmot):
        # %% process each frame
        N = spatial_discrim(m, iLPF, detect_min, detect_max, h)
        if i % frame_count_interval == 0:
            j += 1
            CarCount[j] = N
            if doplot:
                h["h3"].set_ydata(np.cumsum(CarCount))
        # %% save plots
        if doplot:
            h["t1"].set_text(f"h.264 difference frames: index {i}, elapsed seconds {time[j]}")
            h["h1"].set_data(mot[i])
            h["fg"].canvas.draw()
            h["fg"].canvas.flush_events()
            pause(0.001)
            if p.saveplot:
                h["fg"].savefig(p.saveplot + f"{i:05d}.png", bbox_inches="tight", dpi=100)
    # %% write car counts to disk
    if p.outfn is not None:
        outfn = Path(p.outfn).expanduser()
        with h5py.File(outfn, "w") as f:
            f["time"] = time
            f["count"] = CarCount


def spatial_discrim(mot: np.ndarray, iLPF: typing.Tuple[int, int],
                    detect_min: float, detect_max: float, h: dict) -> int:
    """
    implement spatial LPF for two lanes of traffic
    """
    # %% define two spatial lanes of traffic
    lane1 = mot[ilanes[0][0]:ilanes[0][1], :].sum(axis=0)
    lane2 = mot[ilanes[1][0]:ilanes[1][1], :].sum(axis=0)
    # %% motion PSD
    Flane1 = np.fft.fftshift(abs(np.fft.fft(lane1)) ** 2)
    Flane2 = np.fft.fftshift(abs(np.fft.fft(lane2)) ** 2)
    # %% motion detected within magnitude limits
    N1 = int(detect_min <= Flane1[iLPF[0]: iLPF[1]].sum() <= detect_max)
    N2 = int(detect_min <= Flane2[iLPF[0]: iLPF[1]].sum() <= detect_max)
    # %% plot
    h["h21"].set_ydata(Flane1)
    h["h22"].set_ydata(Flane2)

    return N1 + N2


def fig_create(doplot: bool, img: np.ndarray,
               iLPF: typing.Tuple[int, int],
               detect_min: float, detect_max: float,
               time: typing.Sequence[float],
               CarCount: typing.Sequence[int]) -> dict:

    if not doplot:
        return {}

    fg = figure(figsize=(8, 10))
    ax1, ax2, ax3 = fg.subplots(3, 1)
    fg.suptitle("spatial FFT car counting")

    h = {"fg": fg,
         "h1": ax1.imshow(img, origin="upper"),
         "t1": ax1.set_title("")}
    # plot lanes
    ax1.axhline(ilanes[0][0], color="cyan", linestyle="--")
    ax1.axhline(ilanes[0][1], color="cyan", linestyle="--")
    ax1.axhline(ilanes[1][0], color="orange", linestyle="--")
    ax1.axhline(ilanes[1][1], color="orange", linestyle="--")

    L = img.shape[-1]
    fx = np.arange(-L // 2, L // 2)
    h["h21"], = ax2.plot(fx, [0]*fx.size)
    h["h22"], = ax2.plot(fx, [0]*fx.size)
    ax2.set_title("Spatial frequency")
    ax2.set_ylim(0, max_psd)
    ax2.set_xlabel("Spatial Frequency bin (arbitrary units)")
    ax2.set_ylabel("magnitude$^2$")
    # %% setup rectangular spatial LPF for each lane -- cars are big
    ax2.axvline(iLPF[0] - L // 2, color="red", linestyle="--")
    ax2.axvline(iLPF[1] - L // 2, color="red", linestyle="--")
    ax2.axhline(detect_min, linestyle="--")
    ax2.axhline(detect_max, linestyle="--")

    ax3.set_title("cumulative car count")
    ax3.set_xlabel("elapsed time (seconds)")
    ax3.set_ylabel("count")
    ax3.grid(True)
    ax3.set_ylim(0, max_cumulative)
    h["h3"], = ax3.plot(time, CarCount)

    fg.tight_layout()
    fg.canvas.draw()

    return h


if __name__ == "__main__":
    main()
