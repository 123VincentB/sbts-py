import pytest
from sbts import read

FIXTURE_2048 = 'tests/fixtures/S_BTS2048_single.xls'
FIXTURE_2048_MULTI = 'tests/fixtures/S_BTS2048_multi.xls'
FIXTURE_256 = 'tests/fixtures/S_BTS256_single.xls'


def test_read_returns_list():
    result = read(FIXTURE_2048)
    assert isinstance(result, list)
    assert len(result) == 1


def test_multi_returns_multiple():
    result = read(FIXTURE_2048_MULTI)
    assert isinstance(result, list)
    assert len(result) == 3


def test_instrument_detection_2048():
    s = read(FIXTURE_2048)[0]
    assert s.instrument == 'S-BTS2048'


def test_instrument_detection_256():
    s = read(FIXTURE_256)[0]
    assert s.instrument == 'S-BTS256'


def test_spd_2048():
    s = read(FIXTURE_2048)[0]
    assert len(s.wavelengths) == 701
    assert len(s.spd) == len(s.wavelengths)
    assert s.wavelengths[0] == 350.0
    assert s.wavelengths[-1] == 1050.0


def test_spd_256():
    s = read(FIXTURE_256)[0]
    assert len(s.wavelengths) == 371
    assert len(s.spd) == len(s.wavelengths)
    assert s.wavelengths[0] == 380.0
    assert s.wavelengths[-1] == 750.0


def test_data_contains_scalar_keys():
    s = read(FIXTURE_2048)[0]
    assert 'CCT' in s.data
    assert 'CRI: Ra' in s.data
    assert 'date' in s.data
    assert 'serial number' in s.data


def test_minus9999_becomes_none():
    s = read(FIXTURE_256)[0]
    assert s.data.get('saturation') is None
    assert s.data.get('temperature') is None


def test_svm_minus1_becomes_none():
    s = read(FIXTURE_256)[0]
    assert s.data.get('SVM') is None


def test_photometric_values_present():
    s = read(FIXTURE_2048)[0]
    assert s.data.get('photopic') is not None
    assert s.data.get('photometric unit') == 'lx'


def test_diode_progression_256():
    s = read(FIXTURE_256)[0]
    assert s.diode_time_ms is not None
    assert s.diode_values is not None
    assert len(s.diode_time_ms) == len(s.diode_values)
    assert s.diode_time_ms[0] == 0.0


def test_diode_progression_2048_absent():
    s = read(FIXTURE_2048)[0]
    assert s.diode_time_ms is None
    assert s.diode_values is None


def test_key_stripping():
    s = read(FIXTURE_2048)[0]
    assert 'Blue Light Hazard [350 nm - 700 nm]' in s.data
    assert 'ACGIH(skin & eye) [350 nm - 400 nm]' in s.data


def test_multi_independent_measurements():
    measurements = read(FIXTURE_2048_MULTI)
    ccts = [m.data.get('CCT') for m in measurements]
    assert len(set(ccts)) > 1
