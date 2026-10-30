import re
from pandas import DataFrame
from co2data import CO2Values
from config import Config
from tableConfig import TableRunConfig
import TimeFilter
import mass_assumptions
import mixed_lines
import os
from TableFilePrinter import prepare_dataframe_for_export

def get_municipal_prefix(runConfig: TableRunConfig) -> str:
    """Get municipal prefix based on the table file name"""
    table_name = runConfig.outFileNameWithoutExtension
    if "MunicipalityA" in table_name:
        return "MunA_"
    elif "MunicipalityB" in table_name:
        return "MunB_"
    return ""

def PreProcess(runConfigs : list[TableRunConfig]):
    print("Preprocessing ...")
    
    for runConfig in runConfigs:
        print("\nFiltering table", runConfig.outFileNameWithoutExtension, "with", len(runConfig.tableData), "items\n")
        runConfig.tableData = TimeFilter.FilterTime(runConfig, runConfig.tableData)
    
    for config in runConfigs:
        print(len(config.tableData))
        mun_prefix = get_municipal_prefix(config)

        config.df_replaced = ReplaceToCommonTerms(config, config.tableData)
        config.df_replaced = mixed_lines.apply(config, config.tableData, config.df_replaced)
        config.df_replaced = mass_assumptions.apply(config, config.df_replaced)
        config.df_replaced["Num"] = 1
        
        prodStr = config.jsonData['columns']['Products']
        
        # Add translation column before exporting
        co2Data = CO2Values(productColumnName=prodStr)
        df_replaced_with_translation = co2Data.TranslateProductColumn(config.df_replaced.copy())
        
        df_export = prepare_dataframe_for_export(df_replaced_with_translation, prodStr)
        df_export.to_excel(config.output + mun_prefix + "all_wares_replaced.xlsx")
        
        df_empty = config.df_replaced[config.df_replaced["Menge (in Gramm)"].isna()].copy()
        print(df_empty.head())
        
        # Add translation column for unused wares
        df_empty_with_translation = co2Data.TranslateProductColumn(df_empty)
        
        df_export = prepare_dataframe_for_export(df_empty_with_translation, prodStr)
        df_export.to_excel(config.output + mun_prefix + "unused_wares.xlsx")
        
        if not co2Data.Valid():
            print("CO2Data.xlsx file empty")
            exit()
            
        config.df_replaced = co2Data.ProcessValues(config.df_replaced, config.outFileNameWithoutExtension)
        
        fuelitems : list[str] = config.jsonData["WarenTypen"]["Treibstoffe"]
        consumableItems : list[str] = config.jsonData["WarenTypen"]["Verbrauchsgüter"]
        reusableItems : list[str] = config.jsonData["WarenTypen"]["Gebrauchsgüter"]
        
        prodStr = config.jsonData['columns']['Products']
    
        df_replaced = config.df_replaced
        print("\nSplitting up tables...\n")
        config.df_split_fuels = df_replaced.loc[df_replaced[prodStr].isin(fuelitems)].copy()
        print(len(config.df_split_fuels))
        config.df_split_consumables = df_replaced.loc[df_replaced[prodStr].isin(consumableItems)].copy() 
        print(len(config.df_split_consumables))
        config.df_split_resuables = df_replaced.loc[df_replaced[prodStr].isin(reusableItems)].copy()
        print(len(config.df_split_resuables))
    
        print("\nDone!")

def ReplaceToCommonTerms(runConfig: TableRunConfig, df : DataFrame):
    print("\nReplacing common terms in", runConfig.outFileNameWithoutExtension, "with", len(runConfig.tableData), "items\n")
    data : DataFrame = df.copy()

    """Explanation for the regex:

    ^ is line start
    (space and plus, +) is one or more spaces
    | is or
    $ is line end.

    So it searches for leading (line start and spaces) and trailing (spaces and line end) spaces and replaces them with an empty string.
    """
    data.replace(r"^ +| +$", r"", regex=True, inplace=True)
    data.replace(r",$", r"", regex=True, inplace=True)
    
    replacements = runConfig.jsonData["replace"]
    if replacements != None :
        for column in replacements:
            print("Replacing items in column ", column)
            columndata = replacements[column]
            for replacement in columndata:
                print("replacing ", columndata[replacement], " with " , replacement)
                [data.replace(re.compile('.*' + replaced + '.*', re.IGNORECASE), replacement, inplace=True) for replaced in columndata[replacement]]
    print("done")                
    return data
