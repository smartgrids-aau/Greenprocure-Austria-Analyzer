# Greenprocure-Austria-Analyzer

This repo contains the source code for the ABC/XYZ analysis of the CO2 equivalents (CO2e) of municipal procurement in two municipalities of the KEM Carnica Rosental, Austria (bookings 2018-2022). It accompanies the paper *Combining ABC and XYZ Analysis to Prioritise CO2 Reduction in Municipal Procurement: Concept and Initial Implementation in Two Austrian Municipalities* (reference to be added after publication).

The data is available in  a separate repository: [Greenprocure-Austria-Dataset](https://github.com/smartgrids-aau/Greenprocure-Austria-Dataset).

## Quick start

Requirements: Python 3, git and GNU make. Further python packages are documented in requirements.txt

```
pip install -r requirements.txt
make all
```

`make all` clones the dataset into `data/`, runs the tests and the five scenarios and writes the results to `Output/<scenario>/`. One scenario takes about 3 minutes; `make -j4 all` runs them in parallel.

| Target | What it does |
|---|---|
| `make data` | clone the dataset repository into `data/` |
| `make update-data` | pull the latest dataset version |
| `make test` | check the ABC and XYZ rules |
| `make mid` | reference run: mid emission factors, mass assumptions (see below) |
| `make low` / `make high` | low / high end of the emission factor ranges |
| `make mid_datamass` | mid factors, masses exactly as in the dataset |
| `make mid_keepmixed` | mid factors, mixed screw bookings kept in the group "Schrauben" (see below) |
| `make all` | `test` and all five scenarios |
| `make clean` / `make distclean` | remove `Output/` / also the cloned dataset |

Options: `DATA_DIR=<folder>` uses your own copy of the dataset repository (the folder that contains `Dataset/`), `DATA_REF=<tag or commit>` pins a dataset version, `DATA_REPO=<url>` changes the clone source.

## What the analysis does

1. Reads the bookings of each municipality and splits them into fuels, consumables and durable goods.
2. Takes the mass of each booking (from the dataset, plus the mass assumptions below) and multiplies it by an emission factor (g CO2e per kg, `code/CO2Data.xlsx`).
3. **ABC** by cumulative share of the CO2e: a good gets the class in which its contribution starts (share before it below 50 %: A, below 80.9 %: B, otherwise C; class shares 50 / 30.9 / 19.1 %).
4. **XYZ** by the coefficient of variation of the yearly CO2e (years without purchases count as 0, sample standard deviation): X up to 0.5, Y up to 1.0, otherwise Z.
5. Writes classification tables (xlsx), `coverage.txt` (share of expenditure with a mass and a factor) and the ABC/XYZ heatmaps.

## Emission factors (`code/CO2Data.xlsx`)

| Column | Meaning |
|---|---|
| `Material`, `Material_EN` | product group of the dataset and its English name |
| `gCO2Kg` | mid value, g CO2e per kg (cradle-to-gate) |
| `gCO2Kg_low`, `gCO2Kg_high` | range used by the scenarios `low` and `high`; equal to the mid value where no range was determined |
| `Source` | origin of the value, see below |

Values of `Source`:

- **ecoinvent 3.8**: computed with ecoinvent 3.8 (cut-off system model, IPCC 2013 GWP100, cradle-to-gate). Single-dataset rows (flocculant, de-icing salt, bags, EPS, steel) are direct dataset values. For goods without a dataset (tyres, meters, lamps, fire extinguishers) the factor is built from components (steel, brass, plastics, rubber, electronics); the composition shares are **expert assumptions** without manufacturer data, so these factors are estimates of the order of magnitude. ecoinvent is licensed and not part of this repository, only the resulting numbers.
- **assumption: ...**: generic factor of the assumed material (paper, steel, PE plastic, rubber, e-waste proxy, ...).
- **GEMIS 5.0**, **literature**, **estimate**: as stated.
- **empty**: origin not recorded.
- **no factor**: goods without a factor are not part of the CO2e analysis (see coverage).

## Structure

```
Makefile         targets listed above
code/            pipeline (run.py, scenario.py, ABC and XYZ analysis) and CO2Data.xlsx
tests/           checks of the classification rules
requirements.txt Python packages
data/            dataset repository, created by make data (not tracked)
Output/          results, created by make (not tracked)
```

## License

see LICENSE.txt
