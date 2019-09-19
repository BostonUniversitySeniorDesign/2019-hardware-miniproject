#!/usr/bin/env python3
import pytest
from CountMotion import counter, get_param
from pathlib import Path

R = Path(__file__).parent
h5fn = R / "data" / "motion.h5"
configfn = R / "config.ini"


def test_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        counter(tmp_path, "foo")

    with pytest.raises(KeyError):
        counter(h5fn, "foo")


@pytest.mark.parametrize("filename", [h5fn, str(h5fn)])
def test_counter(filename):
    count, time = counter(filename, "dxdy")

    assert count.size == time.size
    assert count.sum() == 115


@pytest.mark.parametrize("filename", [configfn, str(configfn)])
def test_get_param(filename):
    params = get_param(filename)
    assert isinstance(params, dict)


if __name__ == "__main__":
    pytest.main([__file__])
