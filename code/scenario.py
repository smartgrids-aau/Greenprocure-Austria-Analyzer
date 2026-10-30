"""Run one scenario of the analysis and write the results to Output/<scenario>/.

  mid           reference: mid emission factors, mass assumptions for municipality A
  low           low end of the emission factor ranges
  high          high end of the emission factor ranges
  mid_datamass  mid factors, masses exactly as in the dataset (no mass assumptions)
  mid_keepmixed mid factors, mixed screw bookings kept in the group "Schrauben" (no split-off to "Diverses")

Usage:  python code/scenario.py <scenario> [dataset_dir]
dataset_dir is the folder with MunicipalityA/B.json/.xlsx (default: data/Dataset). Normally started by "make".
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCENARIOS = {
    "mid":           ("mid",  "assumed", "split"),
    "low":           ("low",  "assumed", "split"),
    "high":          ("high", "assumed", "split"),
    "mid_datamass":  ("mid",  "dataset", "split"),
    "mid_keepmixed": ("mid",  "assumed", "keep"),
}

if len(sys.argv) < 2 or sys.argv[1] not in SCENARIOS:
    sys.exit("usage: python code/scenario.py {%s} [dataset_dir]" % "|".join(SCENARIOS))

name = sys.argv[1]
data = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data", "Dataset"))
factors, mass, mixed = SCENARIOS[name]
out = os.path.join(ROOT, "Output", name)
os.makedirs(out, exist_ok=True)

env = dict(os.environ, GP_DATASET_DIR=data, GP_OUTPUT_DIR=out, GP_FACTORS=factors, GP_MASS=mass, GP_MIXED=mixed)
print("scenario %s: factors=%s, masses=%s, mixed=%s, dataset=%s" % (name, factors, mass, mixed, data), flush=True)
with open(os.path.join(out, "run.log"), "w") as log:
    subprocess.run([sys.executable, "run.py"], cwd=os.path.join(ROOT, "code"),
                   env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
print("results in %s" % out)
