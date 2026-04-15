# sbts-py

[![PyPI version](https://img.shields.io/pypi/v/sbts-py)](https://pypi.org/project/sbts-py/)
[![License](https://img.shields.io/pypi/l/sbts-py)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/sbts-py)](https://pypi.org/project/sbts-py/)

Parser for spectral data files exported by **Gigahertz-Optik S-BTS2048** and **S-BTS256** spectroradiometers (`.xls` BIFF8 format).

## Installation

```bash
pip install sbts-py
```

## Usage

```python
from sbts import read

# Single measurement
measurements = read('measurement.xls')
s = measurements[0]

print(s.instrument)               # 'S-BTS2048' or 'S-BTS256'
print(s.wavelengths[0])           # 350.0  (nm)
print(len(s.spd))                 # 701 (S-BTS2048) or 371 (S-BTS256)

print(s.data.get('CCT'))          # 4043.16
print(s.data.get('CRI: Ra'))      # 82.45
print(s.data.get('date'))         # '23.06.2025'

# Multi-measurement file
measurements = read('multi.xls')
for m in measurements:
    print(m.data.get('CCT'), m.data.get('samplenumber'))

# S-BTS256 — diode progression
s = read('S-BTS256.xls')[0]
print(s.diode_time_ms)            # [0.0, 0.02, ...] or None
print(s.data.get('Pst'))          # flicker Pst
```

## Returned object

`read()` always returns `list[Sbts]` — a list of one element for a single-measurement file, N elements for a multi-measurement file.

```python
@dataclass
class Sbts:
    wavelengths: list[float]        # wavelengths in nm
    spd: list[float]                # spectral irradiance (W/m²)/nm
    data: dict[str, Any]            # all scalar key/value pairs from the file
    diode_time_ms: list[float] | None
    diode_values: list[float] | None
    instrument: str | None          # 'S-BTS2048' | 'S-BTS256' | None
```

All missing or unavailable values (`-9999.0` convention) are normalized to `None`.

## License

MIT
