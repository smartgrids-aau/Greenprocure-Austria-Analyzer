"""Mixed bookings ("Lärchenholz, Schrauben") that would be assigned to a single goods group.

The grouping (TablePreprocessor.ReplaceToCommonTerms) replaces the whole booking text by the name of the first
matching group. A booking that lists several goods therefore carries the mass and emission factor of one of
them. For screws this matters: the mass of such bookings was derived from the price (about 0.6 EUR/kg, while
screws cost 6-15 EUR/kg), so they dominated the screw group (about 15 t of 18.5 t in municipality A).

Rule: a booking whose group is in GROUPS and whose original text consists of several parts (separated by
comma, plus, semicolon, "u." or "und") is moved to the group TARGET. TARGET has no emission factor and is not
listed in WarenTypen, so these bookings are not part of the CO2 analysis (an underestimate, reported in the
paper) and count as not covered in coverage.txt. The grouping rules themselves are not changed.

Switch off with environment variable GP_MIXED=keep (scenario mid_keepmixed).
"""
import os
import re
from pandas import DataFrame

GROUPS = ("Schrauben",)        # groups whose mixed bookings are split off
TARGET = "Diverses"            # group without emission factor
SEPARATORS = r"[,+;]|\bu\.|\bund\b"   # no slash: "Verschraubung1/2"" and "Blindnieten Alu/Flachkopf" are single goods


def mixed_mask(original_text, group):
    """True for bookings of one of GROUPS whose original text lists several goods."""
    text = original_text.fillna("").astype(str).str.strip().str.rstrip(",")
    return group.isin(GROUPS) & text.str.contains(SEPARATORS, flags=re.IGNORECASE, regex=True)


def apply(runConfig, df_original: DataFrame, df_replaced: DataFrame) -> DataFrame:
    """df_original: booking table before the grouping, df_replaced: after it (same index)."""
    if os.environ.get("GP_MIXED", "split") == "keep":
        return df_replaced
    prod = runConfig.jsonData['columns']['Products']
    cost = runConfig.jsonData['columns']['Cost']
    mass = "Menge (in Gramm)"
    mask = mixed_mask(df_original[prod], df_replaced[prod])
    in_groups = df_replaced[prod].isin(GROUPS)
    print("[mixed lines] %s: %d of %d bookings of %s are mixed, mass %.0f kg of %.0f kg, expenditure %.0f EUR -> '%s'" % (
        runConfig.outFileNameWithoutExtension, mask.sum(), in_groups.sum(), ", ".join(GROUPS),
        df_replaced.loc[mask, mass].sum() / 1000, df_replaced.loc[in_groups, mass].sum() / 1000,
        df_replaced.loc[mask & (df_replaced[cost] > 0), cost].sum(), TARGET))
    df_replaced = df_replaced.copy()
    df_replaced.loc[mask, prod] = TARGET
    return df_replaced
