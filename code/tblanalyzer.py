import paths
import os
import pandas as pd
from pandas import DataFrame
import ABCAnalyzer
import DataVisualizer
from TablePlotter import Plot_Data
import TablePreprocessor
import TimeFilter
import XYZ_Analyzer
from co2data import CO2Values
from config import Config
from tableConfig import TableRunConfig
import matplotlib.pyplot as plt
import seaborn as sns
import ValAggr
from pandas import DataFrame
import TableFilePrinter

def analyze(runConfigs : list[TableRunConfig]):
       
    runConfigs = [item for item in runConfigs if item.isValid()]
    
    for runConfig in runConfigs:
        print(runConfig.tableFilePath)
        runConfig.tableData = pd.read_excel(runConfig.tableFilePath)
        
        runConfig.output = paths.output('{gemeinde}_{yearmin}_{yearmax}/').format(gemeinde=runConfig.outFileNameWithoutExtension, yearmin=str(Config.get("MinYear")), yearmax=str(Config.get("MaxYear")))
        if not os.path.exists(runConfig.output):
            os.makedirs(runConfig.output)
        
    TablePreprocessor.PreProcess(runConfigs)
    
    for runConfig in runConfigs:
        report_coverage(runConfig)
    
    for runConfig in runConfigs:
        analyze_single(runConfig)
    
    TableFilePrinter.PrintTables(runConfigs)    
        
    DataVisualizer.Visualize(runConfigs)
      
def analyze_single(runConfig : TableRunConfig):
    ValAggr.Aggregate_Numbers_Analysis(runConfig)
   
    ABCAnalyzer.Analyze(runConfig)
    
    XYZ_Analyzer.Analyze(runConfig)


def report_coverage(runConfig : TableRunConfig):
    """Share of the (positive) expenditure of the time frame that carries a CO2 estimate, per category."""
    costStr = runConfig.jsonData['columns']['Cost']
    df_all = runConfig.tableData
    total = df_all.loc[df_all[costStr] > 0, costStr].sum()
    lines = ["Coverage of expenditure by CO2 estimates, %s (%d-%d)" % (runConfig.outFileNameWithoutExtension, Config.get("MinYear"), Config.get("MaxYear")),
             "rows in time frame: %d, positive expenditure: %.2f" % (len(df_all), total)]
    covered = 0.0
    for name, d in (("fuels", runConfig.df_split_fuels), ("consumables", runConfig.df_split_consumables), ("durables", runConfig.df_split_resuables)):
        v = d.loc[d[costStr] > 0, costStr].sum()
        covered += v
        lines.append("%-12s rows %5d  expenditure %12.2f  (%.1f%% of total)" % (name, len(d), v, 100 * v / total))
    lines.append("covered total: %.2f (%.1f%% of total)" % (covered, 100 * covered / total))
    text = "\n".join(lines)
    print(text)
    with open(runConfig.output + "coverage.txt", "w", encoding="utf-8") as f:
        f.write(text + "\n")
