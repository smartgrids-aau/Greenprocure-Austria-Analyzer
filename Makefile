# Greenprocure-Austria-Analyzer
# Works with GNU make on Linux and on Windows (cmd.exe).
# Requires Python 3 with the packages from requirements.txt and git on your PATH.

ifeq ($(OS),Windows_NT)
    PYTHON  = python
    RMDIR   = rmdir /Q /S
    dirsep  = \\
    devnull = nul
    Q       =
    BLANK   = echo.
else
    PYTHON  = python3
    RMDIR   = rm -rf
    dirsep  = /
    devnull = /dev/null
    Q       = "
    BLANK   = echo
endif

# Dataset repository (cloned into DATA_DIR). Use your own copy with
#   make all DATA_DIR=path/to/dataset-repo      (folder that contains Dataset/)
# and pin an exact dataset version with DATA_REF=<tag or commit>.
DATA_REPO ?= https://github.com/smartgrids-aau/Greenprocure-Austria-Dataset.git
DATA_DIR  ?= data
DATA_REF  ?=
DATA_FILE  = $(DATA_DIR)/Dataset/MunicipalityA.json

SCENARIOS = mid low high mid_datamass mid_keepmixed

.DEFAULT_GOAL := help
.PHONY: help all test data update-data $(SCENARIOS) clean distclean

help:
	@echo $(Q)Targets:$(Q)
	@echo $(Q)  make data          - clone the dataset repository into DATA_DIR$(Q)
	@echo $(Q)  make update-data   - pull the latest dataset version$(Q)
	@echo $(Q)  make test          - run the checks of the ABC/XYZ rules$(Q)
	@echo $(Q)  make mid           - reference run: mid factors, mass assumptions$(Q)
	@echo $(Q)  make low           - low end of the factor ranges$(Q)
	@echo $(Q)  make high          - high end of the factor ranges$(Q)
	@echo $(Q)  make mid_datamass  - mid factors, masses as in the dataset$(Q)
	@echo $(Q)  make mid_keepmixed - mid factors, mixed screw bookings kept in group Schrauben$(Q)
	@echo $(Q)  make all           - test and all five scenarios, results in Output/$(Q)
	@echo $(Q)  make clean         - remove Output/$(Q)
	@echo $(Q)  make distclean     - remove Output/ and the cloned dataset in data/$(Q)
	@$(BLANK)
	@echo $(Q)One scenario takes about 3 minutes. Use make -j4 all to run them in parallel.$(Q)

all: test $(SCENARIOS)

data: $(DATA_FILE)

$(DATA_FILE):
	git clone $(DATA_REPO) $(DATA_DIR)
ifneq ($(DATA_REF),)
	git -C $(DATA_DIR) checkout $(DATA_REF)
endif

update-data: $(DATA_FILE)
	git -C $(DATA_DIR) pull

test:
	cd code && $(PYTHON) ../tests/test_classification.py

$(SCENARIOS): $(DATA_FILE)
	$(PYTHON) code/scenario.py $@ $(DATA_DIR)/Dataset

clean:
	-$(RMDIR) Output >$(devnull) 2>&1
	@echo Done!

distclean: clean
	-$(RMDIR) data >$(devnull) 2>&1
	@echo Done!
