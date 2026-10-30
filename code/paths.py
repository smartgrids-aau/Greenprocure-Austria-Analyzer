"""Input and output locations. Run the pipeline from this folder (python run.py); "make" does this for you.

GP_DATASET_DIR  folder with MunicipalityA.json/.xlsx etc.  (default: ../data/Dataset,
                i.e. the dataset repository cloned by "make data")
GP_OUTPUT_DIR   folder for tables and figures             (default: ../Output)
GP_CO2_FILE     emission factor table                      (default: ./CO2Data.xlsx)
GP_FACTORS      "mid" (default), "low" or "high": column of CO2Data.xlsx (gCO2Kg, gCO2Kg_low, gCO2Kg_high)
GP_MASS         "assumed" (default) or "dataset": mass assumptions for municipality A on or off
GP_MIXED        "split" (default) or "keep": mixed bookings of screws ("Lärchenholz, Schrauben") moved to "Diverses" or kept
"""
import os

DATASET_DIR = os.environ.get("GP_DATASET_DIR", "../data/Dataset")
OUTPUT_DIR = os.environ.get("GP_OUTPUT_DIR", "../Output")

def dataset(name=""):
    return os.path.join(DATASET_DIR, name)

def output(name=""):
    return os.path.join(OUTPUT_DIR, name)

# table with the emission factors (g CO2e per kg) and the factor range used
CO2_FILE = os.environ.get("GP_CO2_FILE", "./CO2Data.xlsx")
FACTOR_COLUMN = {"mid": "gCO2Kg", "low": "gCO2Kg_low", "high": "gCO2Kg_high"}[os.environ.get("GP_FACTORS", "mid")]
