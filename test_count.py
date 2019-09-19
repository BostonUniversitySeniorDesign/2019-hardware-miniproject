#!/usr/bin/env python3
import pytest
from CountMotion import counter, get_param
from pathlib import Path

R = Path(__file__).parent
car_fn = R / "data" / "motion.h5"
configfn = R / "config.ini"


def test_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        counter(tmp_path, "foo")

    with pytest.raises(KeyError):
        counter(car_fn, "foo")


@pytest.mark.parametrize(
    "filename, key, total", [(car_fn, "dxdy", 115), (str(car_fn), "dxdy", 115), (R / "data/motion_hand.h5", ["dx", "dy"], 3)]
)
def test_counter(filename, key, total):
    count, time = counter(filename, key)

    assert count.size == time.size
    assert count.sum() == total


@pytest.mark.parametrize("filename", [configfn, str(configfn)])
def test_get_param(filename):
    params = get_param(filename)
    assert isinstance(params, dict)


if __name__ == "__main__":
    pytest.main([__file__])
