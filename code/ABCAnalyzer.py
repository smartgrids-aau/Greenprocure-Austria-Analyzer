import math
import pandas as pd
from pandas import DataFrame
from CO2_Assigner import CO2_Assignment
from co2data import CO2Values
from tableConfig import TableRunConfig


def Analyze(runConfig : TableRunConfig):
    print("ABC analysis on", runConfig.outFileNameWithoutExtension)
    print(runConfig.df_split_fuels.head())
    print(runConfig.df_split_consumables.head())
    print(runConfig.df_split_resuables.head())
    runConfig.df_abc_fuels = __analyze(runConfig, runConfig.df_split_fuels)
    runConfig.df_abc_consumables = __analyze(runConfig, runConfig.df_split_consumables)
    runConfig.df_abc_usables = __analyze(runConfig, runConfig.df_split_resuables)
    
    co2Data : CO2Values = CO2Values(productColumnName=runConfig.jsonData['columns']['Products'])
    runConfig.df_abc_fuels = co2Data.ProcessValues(runConfig.df_abc_fuels, runConfig.outFileNameWithoutExtension)
    runConfig.df_abc_consumables = co2Data.ProcessValues(runConfig.df_abc_consumables, runConfig.outFileNameWithoutExtension)
    runConfig.df_abc_usables = co2Data.ProcessValues(runConfig.df_abc_usables, runConfig.outFileNameWithoutExtension)

def __analyze(runConfig : TableRunConfig, df : DataFrame):
    print("ABC analysis on", runConfig.outFileNameWithoutExtension )
    print(df.head())
    costStr = runConfig.jsonData['columns']['Cost']
    prodStr = runConfig.jsonData['columns']['Products']
    outputColumns = set(runConfig.jsonData['outputcolumns'])
    outputColumns.add(costStr)
    outputColumns.add(prodStr)
    df_sub = df.copy()
    
    df_sub = df_sub[df_sub[costStr] >= 0]

    df_sub = df_sub.groupby([prodStr]).sum(numeric_only=True)
    
    print(df_sub.head())
    
    # ABC by cumulative share of expenditure (see ABC_by_cumulative_share)
    df_sub = df_sub.sort_values(by=[costStr], ascending=False, kind="mergesort")
    df_sub['CostCumSum'] = df_sub[costStr].cumsum()
    df_sub["TotalCost"] = df_sub[costStr].sum()
    df_sub['Cost%'] = df_sub[costStr] / df_sub["TotalCost"]
    df_sub['CostCum%'] = df_sub['CostCumSum'] / df_sub["TotalCost"]
    df_sub['ABC_Cost_Rank'] = df_sub[costStr].rank(ascending=False, method="first").astype(int)
    df_sub['ABC_Cost'] = ABC_by_cumulative_share(df_sub[costStr])
    df_sub.reset_index(inplace=True)
    
    print("CO2 value ABC...")
    print(df_sub.head())
        
    co2valStr = "kgCO2Equivalent"
    df_sub = df_sub.sort_values(by=[co2valStr], ascending=False, kind="mergesort")
    df_sub['RunningCO2Cumulative'] = df_sub[co2valStr].cumsum()
    df_sub["totalCO2"] = df_sub[co2valStr].sum()
    df_sub['CO2%'] = df_sub[co2valStr] / df_sub["totalCO2"]
    df_sub['CO2Cumulative%'] = df_sub['RunningCO2Cumulative'] / df_sub["totalCO2"]
    df_sub['ABC_CO2_Rank'] = df_sub[co2valStr].rank(ascending=False, method="first").astype(int)
    df_sub['ABC_CO2'] = ABC_by_cumulative_share(df_sub[co2valStr])
    df_sub.reset_index(inplace=True)

    print(df_sub.head())
    
    return df_sub

# Golden-ratio split of the cumulative share (A : B = B : C, A + B + C = 1, A = 0.5)
ABC_SHARE_A = 0.5
ABC_SHARE_B = -ABC_SHARE_A / 2 + math.sqrt((ABC_SHARE_A / 2) ** 2 - ABC_SHARE_A ** 2 + ABC_SHARE_A)  # 0.309
ABC_SHARE_C = 1 - ABC_SHARE_A - ABC_SHARE_B                                                       # 0.191

def ABC_by_cumulative_share(values : pd.Series) -> pd.Series:
    """ABC class by cumulative share of the total.

    The values must already be sorted in descending order. A good gets the class in
    which its own contribution starts: A if the goods before it have accumulated less than
    ABC_SHARE_A of the total, B if less than ABC_SHARE_A + ABC_SHARE_B, otherwise C.
    The good that crosses a threshold therefore still belongs to the better class."""
    total = values.sum()
    if total <= 0:
        return pd.Series("C", index=values.index)
    share_before = (values.cumsum() - values) / total
    classes = pd.Series("C", index=values.index)
    classes[share_before < ABC_SHARE_A + ABC_SHARE_B] = "B"
    classes[share_before < ABC_SHARE_A] = "A"
    return classes

