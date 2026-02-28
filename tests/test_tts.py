"""Tests for services/tts.py"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tts import _temp_files, _register_temp, cleanup_all, _MAX_TEMP_FILES


def test_register_temp_adds_file():
    _temp_files.clear()
    _register_temp("/tmp/test1.wav")
    assert "/tmp/test1.wav" in _temp_files
    _temp_files.clear()


def test_register_temp_evicts_oldest():
    _temp_files.clear()
    for i in range(_MAX_TEMP_FILES + 5):
        _register_temp(f"/tmp/test_{i}.wav")
    assert len(_temp_files) == _MAX_TEMP_FILES
    # Oldest should have been evicted
    assert "/tmp/test_0.wav" not in _temp_files
    assert f"/tmp/test_{_MAX_TEMP_FILES + 4}.wav" in _temp_files
    _temp_files.clear()


def test_cleanup_all():
    _temp_files.clear()
    _register_temp("/tmp/nonexistent_cleanup_test.wav")
    cleanup_all()
    assert len(_temp_files) == 0
