import paths
from matplotlib import pyplot as plt
from pandas import DataFrame
import seaborn as sns
from tableConfig import TableRunConfig


def Plot_Data(runConfig: TableRunConfig, savePrefix : str, df : DataFrame):
    costStr = runConfig.jsonData['columns']['Cost']
    dateStr = runConfig.jsonData['columns']['Date']
    prodStr = runConfig.jsonData['columns']['Products']
    print("plotting " + savePrefix + "\n")
    #barplot
    
    df_total_abc_cost = df.groupby("ABC_Cost").sum(numeric_only=True)
    df_total_abc_cost.reset_index(inplace=True)
    sns.barplot(x = "ABC_Cost", y = costStr ,data = df_total_abc_cost, color="Red_d", hue="ABC_Cost")
    plt.savefig(paths.output() + savePrefix + '_abc_' + runConfig.tableFileName.removesuffix('.xlsx') + '.png')
    #plt.show(block = False)
    plt.clf()
    #lines
    As = df.query("ABC_Cost == 'A'").nlargest(5, costStr)
    As = As.nlargest(5, "Cost%")

    legend_values = []
    df_grouped = runConfig.tableData.loc[:, [prodStr, dateStr, costStr]]
    
    df_grouped = df_grouped[df_grouped[prodStr].isin(As[prodStr])]
        
    grouped = df_grouped.groupby([prodStr])
    for group, value in grouped:
        plt.plot(value[dateStr], value[costStr], '--')
        legend_values.append(group)
    plt.legend(legend_values)   
    plt.savefig(paths.output() + savePrefix + '_abc_graph' + runConfig.outFileNameWithoutExtension + '.png')
    #plt.show(block = False)
    plt.clf()
    
    print(df.head())
    grouped_ABC_Heat_Count = df.groupby(['ABC_Cost', 'ABC_CO2']).count()
    result = grouped_ABC_Heat_Count.pivot_table(index = 'ABC_Cost', columns= 'ABC_CO2', values= prodStr)
    sns.heatmap(result, annot = True, fmt = '', cmap = 'Blues')
    plt.savefig(paths.output() + savePrefix + '_heatmap_' + runConfig.outFileNameWithoutExtension + '.png')
    plt.clf()
