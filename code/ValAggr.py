from matplotlib import pyplot as plt
from pandas import DataFrame
from tableConfig import TableRunConfig
import seaborn as sns

def Aggregate_Numbers_Analysis(runConfig: TableRunConfig):
    df = runConfig.tableData
    costStr = runConfig.jsonData['columns']['Cost']
    df_cost_sorted = df.sort_values(costStr, ascending=False)
    df_cost_sorted.reset_index(drop=True,inplace=True)
    runConfig.df_aggregate_cost = df_cost_sorted
    runConfig.df_aggregate_cost_noneg = df_cost_sorted[df_cost_sorted[costStr] > 0]
