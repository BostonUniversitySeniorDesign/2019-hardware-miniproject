#!/usr/bin/env python3
import pytest
from CountMotion import counter
from pathlib import Path

R = Path(__file__).parent
h5fn = R / "data" / "motion.h5"


def test_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        counter(tmp_path, "foo")

    with pytest.raises(KeyError):
        counter(h5fn, "foo")


def test_counter():
    count, time = counter(h5fn, "dxdy")

    assert count.size == time.size
    assert count.sum() == 113


if __name__ == "__main__":
    pytest.main([__file__])
