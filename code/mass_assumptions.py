"""Mass assumptions for bookings of municipality A whose mass was estimated from the price with an unsuitable g/EUR ratio.
Switch off with environment variable GP_MASS=dataset (uses the masses of the published dataset unchanged)."""
import os
from pandas import DataFrame

SALT_G_PER_EUR = 6953      # observed in municipality B (bookings with tonnage in the text, about 0.14 EUR/kg)
FLOC_G_PER_EUR = 430       # container bookings of municipality A ("1 Container" = 1,050 kg, about 2.3 EUR/kg)
FLOC_SUSPECT_G_PER_EUR = 2000  # bookings above this ratio are treated as price-estimated bulk deliveries


def apply(runConfig, df: DataFrame) -> DataFrame:
    if os.environ.get("GP_MASS", "assumed") == "dataset":
        return df
    if "MunicipalityA" not in runConfig.outFileNameWithoutExtension:
        return df
    prod = runConfig.jsonData['columns']['Products']
    cost = runConfig.jsonData['columns']['Cost']
    mass = "Menge (in Gramm)"
    df = df.copy()
    salt = (df[prod] == "Auftausalz") & (df[cost] > 0)
    print("[mass assumption] de-icing salt: %d bookings, mass %.0f kg -> %.0f kg" % (salt.sum(), df.loc[salt, mass].sum() / 1000, df.loc[salt, cost].sum() * SALT_G_PER_EUR / 1000))
    df.loc[salt, mass] = df.loc[salt, cost] * SALT_G_PER_EUR
    fl = (df[prod] == "Flockungsmittel") & (df[cost] > 0) & (df[mass] / df[cost] > FLOC_SUSPECT_G_PER_EUR)
    print("[mass assumption] flocculants: %d bookings, mass %.0f kg -> %.0f kg" % (fl.sum(), df.loc[fl, mass].sum() / 1000, df.loc[fl, cost].sum() * FLOC_G_PER_EUR / 1000))
    df.loc[fl, mass] = df.loc[fl, cost] * FLOC_G_PER_EUR
    return df
