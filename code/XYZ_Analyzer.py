from matplotlib import pyplot as plt
from pandas import DataFrame
import pandas as pd
from tableConfig import TableRunConfig
import seaborn as sns
from TableFilePrinter import prepare_dataframe_for_export


# XYZ by the coefficient of variation (CV) of the yearly values, with fixed thresholds
XYZ_THRESHOLD_X = 0.5
XYZ_THRESHOLD_Y = 1.0

def yearly_xyz(runConfig: TableRunConfig, df_original : DataFrame, valueStr : str):
    """Return (classes, cv) as Series indexed by product.

    Yearly sums over every year of the time frame (years without purchases count as 0),
    CV = sample standard deviation / mean, X: CV <= 0.5, Y: CV <= 1.0, Z: otherwise."""
    from config import Config
    prodStr = runConfig.jsonData['columns']['Products']
    yearStr = runConfig.jsonData['columns']['Year']
    years = list(range(Config.get("MinYear"), Config.get("MaxYear") + 1))
    df = df_original[[prodStr, yearStr, valueStr]].copy()
    df[yearStr] = df[yearStr].astype(int)
    yearly = df.pivot_table(index=prodStr, columns=yearStr, values=valueStr, aggfunc="sum").reindex(columns=years).fillna(0.0)
    cv = yearly.std(axis=1, ddof=1) / yearly.mean(axis=1)
    cv = cv.fillna(float("inf"))
    classes = pd.Series("Z", index=cv.index)
    classes[cv <= XYZ_THRESHOLD_Y] = "Y"
    classes[cv <= XYZ_THRESHOLD_X] = "X"
    return classes, cv

def Analyze(runConfig: TableRunConfig):
    prodStr = runConfig.jsonData['columns']['Products']
    if not runConfig.df_abc_fuels.empty:
        runConfig.df_xyz_fuels = __analyze(runConfig, "Treibstoffe", runConfig.df_split_fuels, runConfig.df_abc_fuels)
        runConfig.df_xyz_co2_fuels = __analyze_CO2(runConfig, "Treibstoffe", runConfig.df_split_fuels, runConfig.df_abc_fuels)
    
    if not runConfig.df_abc_consumables.empty:
        runConfig.df_xyz_consumables = __analyze(runConfig, "Verbrauchsgüter", runConfig.df_split_consumables, runConfig.df_abc_consumables)
        runConfig.df_xyz_co2_consumables = __analyze_CO2(runConfig, "Verbrauchsgüter", runConfig.df_split_consumables, runConfig.df_abc_consumables)
    
    if not runConfig.df_abc_usables.empty:    
        runConfig.df_xyz_reusables = __analyze(runConfig, "Gebrauchsgüter", runConfig.df_split_resuables, runConfig.df_abc_usables)
        runConfig.df_xyz_co2_reusables = __analyze_CO2(runConfig, "Gebrauchsgüter", runConfig.df_split_resuables, runConfig.df_abc_usables)
    
    
def __analyze(runConfig: TableRunConfig, prefixStr : str, df_original : DataFrame, df_abc : DataFrame):
    print("running Cost XYZ on ", prefixStr)
    costStr = runConfig.jsonData['columns']['Cost']
    prodStr = runConfig.jsonData['columns']['Products']
    dateStr = runConfig.jsonData['columns']['Date']
    dateFormat = runConfig.jsonData['dateformat']
    
    As = df_abc.nlargest(500, costStr)
    df_orig_filtered = df_original[df_original[prodStr].isin(As[prodStr])].copy()
    
    df_orig_filtered[dateStr] = pd.to_datetime(df_orig_filtered[dateStr], format=dateFormat).dt.date
    
    df_12m = df_orig_filtered.assign(cost_date = pd.to_datetime(df_orig_filtered[dateStr]).dt.strftime("%Y-%m"))

    df_12m_units = df_12m.groupby([prodStr,'cost_date'])[costStr].sum().to_frame().reset_index()
    
    df_12m_units = df_12m_units.pivot(index=prodStr, columns='cost_date', values=costStr)\
                           .reset_index().fillna(0)

    df_12m_units['std_cost'] = df_12m_units[df_12m_units.columns.difference([prodStr, 'cost_date'])].std(axis=1)

    df_12_units_months = df_12m_units.columns.difference([prodStr, 'cost_date', 'std_cost'])
    df_12m_units['total_cost'] = df_12m_units[df_12_units_months].sum(numeric_only=True, axis=1)

    df_12m_units = df_12m_units.assign(avg_monthly_cost = df_12m_units['total_cost'] / len(df_12_units_months) )

    df_12m_units['cov_cost'] = df_12m_units['std_cost'] / df_12m_units['avg_monthly_cost']
    
    classes, cv = yearly_xyz(runConfig, df_orig_filtered, costStr)
    df_12m_units['cv_yearly'] = df_12m_units[prodStr].map(cv)
    df_12m_units['XYZ_Cost'] = df_12m_units[prodStr].map(classes)
    
    prodStr = runConfig.jsonData['columns']['Products']
    
    # Re-add translation column if translation is enabled
    from co2data import CO2Values
    from config import Config
    if Config.get("EnableTranslation", False):
        co2Data = CO2Values(productColumnName=prodStr)
        df_12m_units = co2Data.TranslateProductColumn(df_12m_units)
    
    df_export = prepare_dataframe_for_export(df_12m_units, prodStr)
    df_export.to_excel(runConfig.output + prefixStr + "XYZ_Cost_Timeline.xlsx")
    
    df_12m_units.sort_values(prodStr, inplace=True, ascending=False)
    # assign by product name (not by index position)
    df_abc["XYZ_Cost"] = df_abc[prodStr].map(classes)
    
    return df_12m_units

def __analyze_CO2(runConfig: TableRunConfig, prefixStr : str, df_original : DataFrame, df_abc : DataFrame):
    print("running CO2 XYZ on ", prefixStr)
    costStr = "kgCO2Equivalent"
    prodStr = runConfig.jsonData['columns']['Products']
    dateStr = runConfig.jsonData['columns']['Date']
    dateFormat = runConfig.jsonData['dateformat']
    
    As = df_abc.nlargest(500, costStr)
    df_orig_filtered = df_original[df_original[prodStr].isin(As[prodStr])].copy()
    
    df_orig_filtered[dateStr] = pd.to_datetime(df_orig_filtered[dateStr], format=dateFormat).dt.date
    
    df_12m = df_orig_filtered.assign(date = pd.to_datetime(df_orig_filtered[dateStr]).dt.strftime("%Y-%m"))

    df_12m_units = df_12m.groupby([prodStr,'date'])[costStr].sum().to_frame().reset_index()
    
    df_12m_units = df_12m_units.pivot(index=prodStr, columns='date', values=costStr)\
                           .reset_index().fillna(0)

    df_12m_units['std_co2'] = df_12m_units[df_12m_units.columns.difference([prodStr, 'date'])].std(axis=1)

    df_12_units_months = df_12m_units.columns.difference([prodStr, 'date', 'std_co2'])
    df_12m_units['total_co2'] = df_12m_units[df_12_units_months].sum(numeric_only=True, axis=1)

    df_12m_units = df_12m_units.assign(avg_monthly_co2 = df_12m_units['total_co2'] / len(df_12_units_months) )

    df_12m_units['cov_co2'] = df_12m_units['std_co2'] / df_12m_units['avg_monthly_co2']
    
    classes, cv = yearly_xyz(runConfig, df_orig_filtered, costStr)
    df_12m_units['cv_yearly'] = df_12m_units[prodStr].map(cv)
    df_12m_units['XYZ_CO2'] = df_12m_units[prodStr].map(classes)
    
    # Re-add translation column if translation is enabled
    from co2data import CO2Values
    from config import Config
    if Config.get("EnableTranslation", False):
        co2Data = CO2Values(productColumnName=prodStr)
        df_12m_units = co2Data.TranslateProductColumn(df_12m_units)
    
    df_export = prepare_dataframe_for_export(df_12m_units, prodStr)
    df_export.to_excel(runConfig.output + prefixStr + "XYZ_CO2_Timeline.xlsx")
    
    df_12m_units.sort_values(prodStr, inplace=True, ascending=False)
    # assign by product name (not by index position)
    df_abc["XYZ_CO2"] = df_abc[prodStr].map(classes)
    
    return df_12m_units

def XYZ_Assignment(cov):
    """Apply an XYZ classification to each product based on 
    its coefficient of variation in order quantity.

    :param cov: Coefficient of variation in order quantity for SKU
    :return: XYZ inventory classification class
    """

    if cov <= 0.5:
        return 'X'
    elif cov > 0.5 and cov <= 1.0:
        return 'Y'
    else:
        return 'Z'
