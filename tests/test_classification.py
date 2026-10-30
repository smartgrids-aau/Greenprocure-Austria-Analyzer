"""Checks for the ABC and XYZ classification. Run from code/:  python ../tests/test_classification.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
import pandas as pd
import ABCAnalyzer as abc
from config import Config

def test_abc_cumulative_share():
    # shares 60 / 20 / 10 / 5 / 5 percent: A holds the first 50 %, B the next 30.9 %, C the rest
    v = pd.Series([60, 20, 10, 5, 5], index=list("abcde"), dtype=float)
    c = abc.ABC_by_cumulative_share(v)
    assert list(c) == ["A", "B", "B", "C", "C"], list(c)
    # ten equal goods of 10 percent: a good is A if the goods before it hold < 50 %, B if < 80.9 %, else C
    v = pd.Series([10.0] * 10)
    assert list(abc.ABC_by_cumulative_share(v)) == ["A"] * 5 + ["B"] * 4 + ["C"] * 1
    # the rank-based rule of the old code would have given A to the top 20 % of the goods, i.e. 2 goods here
    assert abc.ABC_SHARE_A + abc.ABC_SHARE_B + abc.ABC_SHARE_C == 1
    assert abs(abc.ABC_SHARE_B - 0.309) < 1e-3 and abs(abc.ABC_SHARE_C - 0.191) < 1e-3

def test_xyz_yearly_fixed_thresholds():
    import XYZ_Analyzer as xyz
    class Cfg:  # minimal stand-in for TableRunConfig
        jsonData = {"columns": {"Products": "p", "Year": "y"}}
    Config.update({"MinYear": 2018, "MaxYear": 2022}) if hasattr(Config, "update") else None
    rows = []
    for y in range(2018, 2023): rows.append(("steady", y, 100.0))            # CV = 0     -> X
    for y, v in zip(range(2018, 2023), [100, 140, 60, 120, 80]): rows.append(("noisy", y, float(v)))  # CV ~ 0.28 -> X
    for y, v in zip(range(2018, 2023), [150, 100, 100, 50, 0]): rows.append(("irregular", y, float(v)))  # CV 0.71 -> Y
    rows.append(("once", 2020, 500.0))                                         # CV 2.24 -> Z (years without purchases count as 0)
    df = pd.DataFrame(rows, columns=["p", "y", "v"])
    classes, cv = xyz.yearly_xyz(Cfg, df, "v")
    assert classes["steady"] == "X" and classes["noisy"] == "X"
    assert classes["irregular"] == "Y", cv["irregular"]
    assert classes["once"] == "Z", cv["once"]

def test_mixed_lines():
    import mixed_lines
    text = pd.Series(["Lärchenholz, Schrauben", "Schrauben,Muttern,U-Scheiben", "Schrauben u. Dübel", "Schrauben, ",
                      "Spanplattenschrauben", 'Verschraubung1/2"', "Blindnieten Alu/Flachkopf",
                      "Schraubendreher, Bits", None])
    group = pd.Series(["Schrauben"] * 7 + ["Schraubdreher", "Schrauben"])
    m = list(mixed_lines.mixed_mask(text, group))
    # mixed bookings of the group are split off; a trailing comma, a slash and other groups are not
    assert m == [True, True, True, False, False, False, False, False, False], m

if __name__ == "__main__":
    test_abc_cumulative_share(); test_xyz_yearly_fixed_thresholds(); test_mixed_lines(); print("all tests passed")
