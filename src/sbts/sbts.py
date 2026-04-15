from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import xlrd
from xlrd import XL_CELL_EMPTY, XL_CELL_NUMBER, XL_CELL_TEXT

_NULL_NUMERIC = {-9999.0}
_SVM_NULL = {-1.0}


@dataclass
class Sbts:
    wavelengths: list[float]
    spd: list[float]
    data: dict[str, Any]
    diode_time_ms: list[float] | None = None
    diode_values: list[float] | None = None
    instrument: str | None = None


def _is_empty_row(ws, row_idx: int) -> bool:
    return all(ws.cell_type(row_idx, col) == XL_CELL_EMPTY
               for col in range(ws.ncols))


def _is_separator_row(ws, row_idx: int) -> bool:
    if _is_empty_row(ws, row_idx):
        return True
    v = ws.cell_value(row_idx, 0)
    return isinstance(v, str) and v.strip() == ''


def _normalize_value(key: str, v: Any) -> Any:
    if isinstance(v, str) and v.strip() == '':
        return None
    if isinstance(v, float):
        if v in _NULL_NUMERIC:
            return None
        if key.strip() == 'SVM' and v in _SVM_NULL:
            return None
    return v


def _detect_instrument(data: dict, n_spd_points: int) -> str | None:
    if 'device type' in data:
        return 'S-BTS2048'
    if n_spd_points == 701:
        return 'S-BTS2048'
    if n_spd_points == 371:
        return 'S-BTS256'
    return None


def _parse_sheet(ws, col_idx: int) -> Sbts:
    data: dict[str, Any] = {}
    wavelengths: list[float] = []
    spd: list[float] = []
    diode_time_ms_list: list[float] = []
    diode_values_list: list[float] = []

    in_spd = False
    in_diode = False

    for row_idx in range(ws.nrows):
        if _is_separator_row(ws, row_idx):
            in_spd = False
            in_diode = False
            continue

        cell_type_0 = ws.cell_type(row_idx, 0)
        col0_val = ws.cell_value(row_idx, 0)

        if cell_type_0 == XL_CELL_NUMBER:
            if in_spd:
                wavelengths.append(float(col0_val))
                spd.append(float(ws.cell_value(row_idx, col_idx)))
            elif in_diode:
                diode_time_ms_list.append(float(col0_val))
                diode_values_list.append(float(ws.cell_value(row_idx, col_idx)))
            continue

        if cell_type_0 != XL_CELL_TEXT:
            continue

        key = col0_val.strip()
        if not key:
            in_spd = False
            in_diode = False
            continue

        if key == 'wavelength /nm':
            in_spd = True
            in_diode = False
            continue

        if key == 'time / ms':
            in_diode = True
            in_spd = False
            continue

        val = ws.cell_value(row_idx, col_idx)
        data[key] = _normalize_value(key, val)

    instrument = _detect_instrument(data, len(wavelengths))

    return Sbts(
        wavelengths=wavelengths,
        spd=spd,
        data=data,
        diode_time_ms=diode_time_ms_list if diode_time_ms_list else None,
        diode_values=diode_values_list if diode_values_list else None,
        instrument=instrument,
    )


def read(path: str | Path) -> list[Sbts]:
    """
    Parse un fichier .xls Gigahertz-Optik S-BTS2048 ou S-BTS256.

    Retourne toujours une list[Sbts] :
    - liste de 1 élément pour un fichier single-mesure
    - liste de N éléments pour un fichier multi-mesures (N colonnes de valeurs)

    Raises:
        FileNotFoundError: fichier introuvable
        ValueError: feuille 'Sheet3' absente ou fichier non parseable
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    wb = xlrd.open_workbook(str(path))

    if 'Sheet3' not in wb.sheet_names():
        raise ValueError(f"Feuille 'Sheet3' absente dans {path}")

    ws = wb.sheet_by_name('Sheet3')
    n_measures = ws.ncols - 1

    return [_parse_sheet(ws, col_idx) for col_idx in range(1, n_measures + 1)]
