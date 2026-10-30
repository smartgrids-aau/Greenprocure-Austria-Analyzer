from pandas import DataFrame
from tableConfig import TableRunConfig
from datetime import datetime, timedelta
import pandas as pd
from config import Config

def FilterTime(runConfig: TableRunConfig, df : DataFrame):
    print("Filtering time for", runConfig.outFileNameWithoutExtension)
    yearColumn = runConfig.jsonData["columns"]["Year"]
    if(not yearColumn):
        print("no year column, skipping filtering dates")
        return df
    minYearInt : int = Config.get("MinYear", 2000)
    maxYearInt : int = Config.get("MaxYear", 3000)
    
    df = df[df[yearColumn] >= minYearInt]
    df = df[df[yearColumn] <= maxYearInt]
    
    from TableFilePrinter import prepare_dataframe_for_export
    from co2data import CO2Values
    prodStr = runConfig.jsonData['columns']['Products']
    
    # Add translation column before exporting
    co2Data = CO2Values(productColumnName=prodStr)
    df_with_translation = co2Data.TranslateProductColumn(df.copy())
    
    df_export = prepare_dataframe_for_export(df_with_translation, prodStr)
    df_export.to_excel(runConfig.output + "Timefiltered.xlsx")
    
    return df
