import paths
import pandas as pd
from pandas import DataFrame
import tblanalyzer as analyzer
import co2data
import os
import importlib
from tableConfig import TableRunConfig
import sys
import json
from co2data import CO2Values

sys.dont_write_bytecode = True

def co2value(key : str):
    return co2data.co2Values.get(key, 0)

all_files = os.listdir(paths.dataset())    

json_files = list(filter(lambda f: f.endswith('.json'), all_files))

runConfigs : list[TableRunConfig] = list[TableRunConfig]()
for jsonfileName in json_files:
    with open(paths.dataset(jsonfileName),encoding='UTF-8') as jason_file:
        file_contents = jason_file.read()
        parsed_json = json.loads(file_contents)
        tableName = parsed_json["table"]
    
        if tableName == None:
            print("Could not find table config for config ", jsonfileName)        
            continue
        runConfigs.append(TableRunConfig(jsonfileName, parsed_json))

analyzer.analyze(runConfigs)
