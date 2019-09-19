#!/usr/bin/env python3
import h5py
from argparse import ArgumentParser
from pathlib import Path
import configparser
import numpy as np
import typing
import sys

config_fn = Path(__file__).parent / "config.ini"
MAX_LANES = 4


def main(
    infn: Path, variable_name: typing.Sequence[str], istart: int = 0, outfn: Path = None, doplot: bool = True, saveplot: str = None
):
    # %% main loop
    CarCount, time = counter(h5fn=infn, key=variable_name, start=istart, doplot=doplot, saveplot=saveplot)
    # %% write car counts to disk
    if outfn is not None:
        outfn = Path(outfn).expanduser()
        with h5py.File(outfn, "w") as f:
            f["time"] = time
            f["count"] = CarCount

    if not doplot:
        print("Per frame car count", CarCount)
        print("Total car count", CarCount.sum())


def counter(
    h5fn: Path, key: typing.Sequence[str], start: int = 0, doplot: bool = False, saveplot: str = None
) -> typing.Tuple[np.ndarray, np.ndarray]:

    h5fn = Path(h5fn).expanduser()
    param = get_param(config_fn)

    frame_count_interval = int(param["video_fps"] * param["count_interval_seconds"])

    if not h5fn.is_file():
        raise FileNotFoundError(h5fn)
    with h5py.File(h5fn, "r") as f:
        if isinstance(key, str):
            mot = np.rot90(abs(f[key][start:]).astype(np.uint8), axes=(1, 2))
        elif isinstance(key, (tuple, list)) and len(key) == 1:
            mot = np.rot90(abs(f[key[0]][start:]).astype(np.uint8), axes=(1, 2))
        elif isinstance(key, (tuple, list)) and len(key) == 2:
            mot = np.rot90(np.hypot(f[key[0]][start:], f[key[1]][start:]).astype(np.uint8), axes=(1, 2))
        else:
            raise ValueError(f"not sure what variable {key} you are trying to get in {h5fn}")
    # %% approximate elapsed time
    time = np.arange(0, mot.shape[0] / param["video_fps"] + param["count_interval_seconds"], param["count_interval_seconds"])
    # %% create figure
    CarCount = np.zeros(time.size, dtype=int)
    j = 0
    L = mot.shape[-1]
    param["iLPF"] = (int(L * 4 / 9), int(L * 5.2 / 9))
    h: typing.Dict[str, typing.Any] = {}
    if doplot:
        try:
            from matplotlib.pyplot import pause

            h = fig_create(doplot, mot[0], param, time, CarCount)
        except Exception as exc:
            doplot = False
            print(f"Matplotlib not available, skipping plots  {exc}", file=sys.stderr)
    # %% main program loop over each frame of motion data
    for i, m in enumerate(mot):
        # %% process each lane
        N = 0
        for k in range(MAX_LANES):
            if f"lane{k:d}" in param:
                N += spatial_discrim(
                    m, param[f"lane{k:d}"], param["iLPF"], param["detect_min"], param["detect_max"], h=h.get(f"h2{k}")
                )
        # %% update cumulative count
        if i % frame_count_interval == 0:
            j += 1
            CarCount[j] = N
            if doplot:
                h["h3"].set_ydata(np.cumsum(CarCount))
        # %% save plots
        if doplot:
            h["t1"].set_text(f"h.264 difference frames: index {i}, elapsed seconds {time[j]}")
            h["h1"].set_data(m)
            h["fg"].canvas.draw()
            h["fg"].canvas.flush_events()
            pause(0.001)
            if saveplot:
                h["fg"].savefig(saveplot + f"{i:05d}.png", bbox_inches="tight", dpi=100)

    return CarCount, time


def get_param(fn: Path) -> typing.Dict[str, typing.Any]:
    fn = Path(fn).expanduser()
    C = configparser.ConfigParser()
    C.read_string(fn.read_text(), source=str(fn))
    param: typing.Dict[str, typing.Any] = {
        "detect_max": C.getfloat("filter", "detect_max"),
        "detect_min": C.getfloat("filter", "detect_min"),
        "count_interval_seconds": C.getfloat("filter", "count_interval_seconds"),
        "video_fps": C.getfloat("video", "video_fps"),
        "max_cumulative": C.getint("plot", "max_cumulative", fallback=None),
        "max_psd": C.getfloat("plot", "max_psd", fallback=None),
    }

    for k in range(1, MAX_LANES + 1):
        lane = C.get("lanes", f"lane{k}", fallback=None)
        if lane:
            param[f"lane{k}"] = list(map(int, lane.split(",")))

    return param


def spatial_discrim(
    mot: np.ndarray, ilane: typing.Tuple[int, int], iLPF: typing.Tuple[int, int], detect_min: float, detect_max: float, h=None
) -> int:
    """
    implement spatial LPF for two lanes of traffic
    """
    # %% define two spatial lanes of traffic
    lane = mot[ilane[0]: ilane[1], :].sum(axis=0)
    # %% motion PSD
    Flane = np.fft.fftshift(abs(np.fft.fft(lane)) ** 2)
    # %% motion detected within magnitude limits
    N = int(detect_min <= Flane[iLPF[0]: iLPF[1]].sum() <= detect_max)
    # %% plot
    if h is not None:
        h.set_ydata(Flane)

    return N


def fig_create(
    doplot: bool, img: np.ndarray, p: typing.Dict[str, typing.Any], time: typing.Sequence[float], CarCount: typing.Sequence[int]
) -> dict:

    if not doplot:
        return {}

    from matplotlib.pyplot import figure

    L = img.shape[-1]
    fx = np.arange(-L // 2, L // 2)

    fg = figure(figsize=(8, 10))
    ax1, ax2, ax3 = fg.subplots(3, 1)
    fg.suptitle("spatial FFT car counting")

    h = {"fg": fg, "h1": ax1.imshow(img, origin="upper", vmin=0, vmax=90), "t1": ax1.set_title("")}
    # plot lanes
    colors = ("cyan", "orange", "white", "yellow")
    for k in range(MAX_LANES):
        if f"lane{k:d}" in p:
            ax1.axhline(p[f"lane{k:d}"][0], color=colors[k], linestyle="--")
            ax1.axhline(p[f"lane{k:d}"][1], color=colors[k], linestyle="--")
            h[f"h2{k}"], = ax2.plot(fx, [0] * fx.size)

    ax2.set_title("Spatial frequency")
    ax2.set_ylim(0, p["max_psd"])
    ax2.set_xlabel("Spatial Frequency bin (arbitrary units)")
    ax2.set_ylabel("magnitude$^2$")
    # %% setup rectangular spatial LPF for each lane -- cars are big
    ax2.axvline(p["iLPF"][0] - L // 2, color="red", linestyle="--")
    ax2.axvline(p["iLPF"][1] - L // 2, color="red", linestyle="--")
    ax2.axhline(p["detect_min"], linestyle="--")
    ax2.axhline(p["detect_max"], linestyle="--")

    ax3.set_title("cumulative car count")
    ax3.set_xlabel("elapsed time (seconds)")
    ax3.set_ylabel("count")
    ax3.grid(True)
    ax3.set_ylim(0, p["max_cumulative"])
    h["h3"], = ax3.plot(time, CarCount)

    fg.tight_layout()
    fg.canvas.draw()

    return h


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("infn", help="HDF5 motion file to analyze")
    p.add_argument("variable_name", help="HDF5 variable name with motion data (e.g. dx or dy)", nargs="+")
    p.add_argument("-i", "--start", help="starting frame of video to process", type=int, default=0)
    p.add_argument("-o", "--outfn", help="write car counts to disk")
    p.add_argument("-q", "--noplot", help="do not make plots (save CPU)", action="store_false")
    p.add_argument("-s", "--saveplot", help="preview save name")
    p = p.parse_args()

    main(p.infn, p.variable_name, istart=p.start, outfn=p.outfn, doplot=p.noplot, saveplot=p.saveplot)
