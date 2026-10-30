from pandas import DataFrame
from tableConfig import TableRunConfig
from config import Config

COLUMN_TRANSLATIONS = {
    "Text": "Product",
    "USt-%": "VAT-%",
    "Soll Brutto": "Gross Amount",
    "Soll Netto": "Net Amount",
    "Jahr": "Year",
    "Periode": "Period",
    "Hinweis": "Note",
    "Menge (in Gramm)": "Quantity (in Grams)",
    "Menge (in kg)": "Quantity (in kg)",
    "gCO2PerKGWare": "gCO2PerKGProduct",
    "kgCO2PerKGWare": "kgCO2PerKGProduct",
    "kgCO2Equivalent": "kgCO2Equivalent",
    "Buchungsdatum": "Booking Date",
    "Postbezeichnung": "Post Description",
    "ABC_Cost_Rank": "ABC_Cost_Rank",
    "RunningCO2Cumulative": "RunningCO2Cumulative",
    "totalCO2": "totalCO2",
    "CO2%": "CO2%",
    "CO2Cumulative%": "CO2Cumulative%",
    "ABC_CO2_Rank": "ABC_CO2_Rank",
    "CostCumSum": "CostCumSum",
    "TotalCost": "TotalCost",
    "Cost%": "Cost%",
    "CostCum%": "CostCum%",
    "Num": "Count",
    "num": "Count",
}

def get_municipal_prefix(runConfig: TableRunConfig) -> str:
    """Get municipal prefix based on the table file name"""
    table_name = runConfig.outFileNameWithoutExtension
    if "MunicipalityA" in table_name:
        return "MunA_"
    elif "MunicipalityB" in table_name:
        return "MunB_"
    return ""

def prepare_dataframe_for_export(df: DataFrame, prodStr: str) -> DataFrame:
    df_export = df.copy()
    
    if Config.get("EnableTranslation", False):
        text_en_col = prodStr + "_EN"
        if text_en_col in df_export.columns:
            df_export[prodStr] = df_export[text_en_col]
            df_export = df_export.drop(columns=[text_en_col])
        
        new_columns = {}
        for col in df_export.columns:
            if col in COLUMN_TRANSLATIONS:
                new_columns[col] = COLUMN_TRANSLATIONS[col]
            else:
                new_columns[col] = col
        
        df_export.rename(columns=new_columns, inplace=True)
    
    return df_export

def PrintTables(runConfigs : list[TableRunConfig]):
    
    for runConfig in runConfigs:
        mun_prefix = get_municipal_prefix(runConfig)
        prodStr = runConfig.jsonData['columns']['Products']
        
        df_usables = prepare_dataframe_for_export(runConfig.df_abc_usables, prodStr)
        df_usables.set_index("index", inplace=True)
        df_usables.reset_index(drop=True,inplace=True)
        df_usables.to_excel(runConfig.output + mun_prefix + '_abc_gebrauch.xlsx')
        
        df_consumables = prepare_dataframe_for_export(runConfig.df_abc_consumables, prodStr)
        df_consumables.set_index("index", inplace=True)
        df_consumables.reset_index(drop=True,inplace=True)
        df_consumables.to_excel(runConfig.output + mun_prefix + '_abc_verbrauch.xlsx')
        Print_Counts(runConfig)


def Print_Counts(runConfig : TableRunConfig):
    costStr = runConfig.jsonData['columns']['Cost']
    prodStr = runConfig.jsonData['columns']['Products']
    dateStr = runConfig.jsonData['columns']['Date']
    mun_prefix = get_municipal_prefix(runConfig)
    
    def l(runConfig : TableRunConfig, suffix : str, df: DataFrame) :
        df_counts = df.copy()
        df_counts['num'] = 1
        df_counts = df_counts.groupby(prodStr).sum(numeric_only=True)
        df_counts.sort_values(by=['num'], ascending = False, inplace=True )
        df_counts.reset_index(inplace=True)
        
        df_counts = prepare_dataframe_for_export(df_counts, prodStr)
        df_counts.reset_index(drop=True, inplace=True)
        df_counts.to_excel(runConfig.output + mun_prefix + suffix + '_Num.xlsx')
    
    l(runConfig, "Treibstoff", runConfig.df_split_fuels)
    l(runConfig, "Verbrauch", runConfig.df_split_consumables)
    l(runConfig, "Gebrauch", runConfig.df_split_resuables)
