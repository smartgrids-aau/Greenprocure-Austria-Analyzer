import paths
from config import Config
from tableConfig import TableRunConfig
from matplotlib import pyplot as plt
from pandas import DataFrame
import seaborn as sns
import pandas as pd

# Import translation module (minimal change for translation support)
try:
    from translations import translate_file_prefix
    TRANSLATIONS_AVAILABLE = True
except ImportError:
    TRANSLATIONS_AVAILABLE = False

bounds = [1, 2, 4, 7, 8]

# Translation helper functions (minimal addition for translation support)
def get_text(german_text: str, english_text: str) -> str:
    """Return English text if translation enabled, otherwise German"""
    if Config.get("EnableTranslation", False):
        return english_text
    return german_text

def get_filename_prefix(category: str) -> str:
    """Get translated filename prefix for category"""
    if Config.get("EnableTranslation", False) and TRANSLATIONS_AVAILABLE:
        return translate_file_prefix(category)
    return category

def get_municipal_prefix(runConfig: TableRunConfig) -> str:
    """Get municipal prefix based on the table file name"""
    table_name = runConfig.outFileNameWithoutExtension
    if "MunicipalityA" in table_name:
        return "MunA_"
    elif "MunicipalityB" in table_name:
        return "MunB_"
    return ""

def Visualize(runConfigs : list[TableRunConfig]):
    """
    1. TableRunConfig.Analyzed -> Dict(str, df)... "ABC_Verbrauch", "ABC_Gebrauch", "XYZ_Gebrauch_Cost", "XYZ_Gebrauch_CO2"
    2. For each tableRunConfig :
        - Visualize data alone
    3. Visualize together
    2. For each str in dict :
        Plot together
    """
    __visualize(runConfigs)
    """    
    if len(runConfigs) > 1 : 
        for config in runConfigs:
            __visualize([config])
    """

def __visualize(runConfigs : list[TableRunConfig]):
    __visualize_aggregates(runConfigs)
    #sns.set(font_scale=1.0)
    for runConfig in runConfigs:

        __visualize_abc(runConfig, runConfig.df_abc_consumables, "Verbrauchsgüter")
        __visualize_abc(runConfig, runConfig.df_abc_usables, "Gebrauchsgüter")
        __visualize_abc(runConfig, runConfig.df_abc_fuels, "Treibstoffe")
        
        __visualize_xyz(runConfig,runConfig.df_xyz_fuels, "Treibstoffe")
        __visualize_xyz(runConfig,runConfig.df_xyz_consumables, "Verbrauchsgüter")
        __visualize_xyz(runConfig,runConfig.df_xyz_reusables, "Gebrauchsgüter")
        
        __visualize_abc_xyz(runConfig, runConfig.df_abc_consumables, "Verbrauchsgüter")
        __visualize_abc_xyz(runConfig, runConfig.df_abc_usables, "Gebrauchsgüter")
        
        __plot_timeline(runConfig, runConfig.df_split_resuables, runConfig.df_abc_usables, "Gebrauchsgüter")
        __plot_timeline(runConfig, runConfig.df_split_consumables, runConfig.df_abc_consumables, "Verbrauchsgüter")
        __plot_timeline(runConfig, runConfig.df_split_fuels, runConfig.df_abc_fuels, "Treibstoffe")
        
def __visualize_abc(runConfig: TableRunConfig, df : DataFrame, tableCategory : str):
    print("visualizing ABC for table ", runConfig.outFileNameWithoutExtension)
    
    plt.clf()
    plt.cla()
    plt.close()
    
    #sns.set(font_scale=1.0)
    
    if df.empty:
        print("Can't visualize ABC for", tableCategory, ", dataframe is empty")
        return
        
    costStr = runConfig.jsonData['columns']['Cost']
    dateStr = runConfig.jsonData['columns']['Date']
    prodStr = runConfig.jsonData['columns']['Products']

    # Get filename prefix (translated if needed)
    file_prefix = get_filename_prefix(tableCategory)
    # Get municipal prefix
    mun_prefix = get_municipal_prefix(runConfig)

    #barplot
    print("ABC cost barplot...")
    df_total_abc_cost = df.groupby("ABC_Cost").sum(numeric_only=True)
    df_total_abc_cost.reset_index(inplace=True)
    print("printing head...")
    print(df_total_abc_cost.head())
    print("ABC cost barplot...")
    f, ax = plt.subplots(figsize=(20, 8))
    p = sns.barplot(
        x = "ABC_Cost", 
        y = costStr,
        data = df_total_abc_cost
    )
    p.set(title=get_text("Ausgaben, ABC Gruppierung", "Expenditures, ABC Classification"))
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_Cost.png')
    #plt.show(block = False)
    plt.clf()
    plt.cla()
    plt.close()
    
    print("ABC CO2 barplot...")
    df_total_abc_co2 = df.groupby("ABC_CO2").sum(numeric_only=True)
    df_total_abc_co2.reset_index(inplace=True)
    
    f, ax = plt.subplots(figsize=(20, 8))
    p = sns.barplot(
        x = "ABC_CO2", 
        y = "gCO2PerKGWare",
        data = df_total_abc_co2
    )
    p.set(title=get_text("CO2 Äquivalenz, ABC Gruppierung", "CO2 Equivalence, ABC Classification"))
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_CO2.png')
    plt.clf()
    plt.cla()
    plt.close()    
    
    #sns.set(font_scale=2.0)
    
    grouped_ABC_Heat_Count = df.groupby(['ABC_Cost', 'ABC_CO2']).count()
    result = grouped_ABC_Heat_Count.pivot_table(index = 'ABC_Cost', columns= 'ABC_CO2', values= prodStr)
    f, left = plt.subplots(1,1,figsize=(10, 8))
    ax = sns.heatmap(result, annot = True, fmt = '.0f', cmap = 'coolwarm', ax=left, annot_kws={"fontsize":22}, cbar_kws={'label': get_text(get_text("Anzahl Güterkategorien", "Number of Goods Categories"), "Number of Goods Categories"), 'ticks':range(1, int(result.max().max()) + 1)})
    ax.collections[0].colorbar.set_label(get_text(get_text("Anzahl Güterkategorien", "Number of Goods Categories"), "Number of Goods Categories"), fontsize=24, labelpad=10)
    cax = ax.figure.axes[-1]
    cax.tick_params(labelsize=18)
    plt.xticks(rotation=0, fontsize=20)
    plt.yticks(rotation=0, fontsize=20)
    plt.xlabel(get_text(get_text("CO2 Äquivalenz", "CO2 Equivalence"), "CO2 Equivalence"),fontsize=24)
    plt.ylabel(get_text(get_text("Ausgaben", "Expenditures"), "Expenditures"), rotation=90, ha="center",fontsize=24)
    
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_Heatmap.png')
    plt.clf()
    plt.cla()
    plt.close() 
    
    
    grouped_ABC_Heat_Count = df.groupby(['ABC_CO2', 'XYZ_CO2']).count()
    result = grouped_ABC_Heat_Count.pivot_table(index = 'ABC_CO2', columns= 'XYZ_CO2', values= prodStr)
    f, left = plt.subplots(1,1,figsize=(10, 8))
    ax = sns.heatmap(result, annot = True, fmt = '.0f', cmap = 'coolwarm',ax=left, annot_kws={"fontsize":22}, cbar_kws={'label': get_text("Anzahl Güterkategorien", "Number of Goods Categories"), 'ticks':range(1, int(result.max().max()) + 1)})
    ax.collections[0].colorbar.set_label(get_text("Anzahl Güterkategorien", "Number of Goods Categories"), fontsize=24, labelpad=10)
    cax = ax.figure.axes[-1]
    cax.tick_params(labelsize=18)
    plt.xticks(rotation=0, fontsize=20)
    plt.yticks(rotation=0, fontsize=20)
    plt.xlabel(get_text("Regelmäßigkeit (XYZ)", "Regularity (XYZ)"),fontsize=24)
    plt.ylabel(get_text("CO2 Äquivalenz", "CO2 Equivalence"), rotation=90, ha="center",fontsize=24)
    
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_XYZ_CO2_Heatmap.png')
    plt.clf()
    plt.cla()
    plt.close()  
    
    #sns.set(font_scale=1.0)
    
    print("done")

def __visualize_xyz(runConfig: TableRunConfig, df_xyz : DataFrame, tableCategory : str):
    print("Viszalizing xyz")
    if df_xyz.empty:
        print("Can't visualize XYZ for", tableCategory, ", dataframe is empty")
        return
    
    # Get filename prefix (translated if needed)
    file_prefix = get_filename_prefix(tableCategory)
    # Get municipal prefix
    mun_prefix = get_municipal_prefix(runConfig)
    # Get translated category name for titles
    cat_name = file_prefix if Config.get("EnableTranslation", False) else tableCategory
    
    df_xyz_onlymonths = df_xyz.drop(axis="columns", labels=["std_cost", "cov_cost", "total_cost", "avg_monthly_cost", "cv_yearly"])
    print(df_xyz_onlymonths.head())
    
    print("transposing")

    df_x = df_xyz_onlymonths.set_index("Text", drop=True)
    print(df_x.head())
    df_x = df_x[df_x["XYZ_Cost"] == "X"]
    print(df_x.head())
    df_x.drop(["XYZ_Cost"],axis=1, inplace=True)
    print(df_x.head())
    df_x = df_x.T
    print(df_x.head())
    #df_x_transposed = df_x.set_index("Text", inplace=False, drop=True).T
    
   
    print("normal")
    df_monthly = df_xyz_onlymonths.groupby('XYZ_Cost').sum(numeric_only=True)
    print(df_monthly.head())
    
    print("Viszalizing xyz unstacked")
    df_monthly_unstacked = df_monthly.unstack('XYZ_Cost').to_frame()
    df_monthly_unstacked = df_monthly_unstacked.reset_index().rename(columns={'level_0': 'date', 0: 'cost'})
    print(df_monthly_unstacked.head())
    plt.clf()
    plt.cla()
    plt.close()
    
    #sns.set(font_scale=1.0)
    
    df_m_u_x = df_monthly_unstacked[df_monthly_unstacked['XYZ_Cost']=='X']
    if not df_m_u_x.empty:
        f = plt.figure(figsize=(20, 8))
        f, ax = plt.subplots(figsize=(15, 6))
        ax = sns.barplot(x="cost_date", 
            y="cost", 
            data=df_monthly_unstacked[df_monthly_unstacked['XYZ_Cost']=='X'],
            hue="cost_date",
            palette="Blues_d",
            legend=False)\
            .set_title(cat_name + " " + get_text("X Klasse Kosten pro Monat", "X class cost by month"),fontsize=15)
        plt.xticks(rotation=45)
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_X_Cost.png')
        plt.clf()
        plt.cla()
        plt.close()
    
    df_m_u_y = df_monthly_unstacked[df_monthly_unstacked['XYZ_Cost']=='Y']
    if not df_m_u_y.empty:    
        f = plt.figure(figsize=(20, 8))
        f, ax = plt.subplots(figsize=(15, 6))
        ax = sns.barplot(x="cost_date", 
            y="cost", 
            data=df_m_u_y,
            hue="cost_date",
            palette="Blues_d",
            legend=False)\
            .set_title(cat_name + " " + get_text("Y Klasse Kosten pro Monat", "Y class cost by month"),fontsize=15)
        plt.xticks(rotation=45)
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_Y_Cost.png')
        plt.clf()
        plt.cla()
        plt.close()
    
    df_m_u_z = df_monthly_unstacked[df_monthly_unstacked['XYZ_Cost']=='Z']
    if not df_m_u_z.empty :    
        f = plt.figure(figsize=(20, 8))
        f, ax = plt.subplots(figsize=(15, 6))
        ax = sns.barplot(x="cost_date", 
            y="cost", 
            data=df_m_u_z,
            hue="cost_date",
            palette="Blues_d",
            legend=False)\
            .set_title(cat_name + " " + get_text("Y Klasse Kosten pro Monat", "Y class cost by month"),fontsize=15)
        plt.xticks(rotation=45)
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_Z_Cost.png')
        plt.clf()
        plt.cla()
        plt.close()
    
    return
"""
    costStr = 'total_cost'
    dateStr = runConfig.jsonData['columns']['Date']
    prodStr = runConfig.jsonData['columns']['Products']
    #lines
    #As = df.query("ABC_Cost == 'A'")#.nlargest(5, costStr)
    print(df.head())
    df_xyz = df.nlargest(10, costStr)
    print(df.head())
    df_xyz.set_index("Text")
    print(df.head())
    df_xyz = df_xyz.select_dtypes(include="datetime64")
    print(df_xyz.head())
    
    sns.lineplot(data = df_xyz, x = df_xyz.columns, y=df_xyz.index)
    plt.show()
    return
    
    legend_values = []
    df_grouped = df_xyz.loc[:, [prodStr, dateStr, costStr]]
    
    
    grouped = df_grouped.groupby([prodStr])
    for group, value in grouped:
        plt.plot(value[dateStr], value[costStr], '--')
        legend_values.append(group)
    plt.legend(legend_values)   
    plt.savefig(paths.output() + runConfig.outFileNameWithoutExtension + tableCategory + '_ABC_Cost_Graph_.png')
    #plt.show(block = False)
    plt.clf()
    
    
    print(df_12m.head())
    f, ax = plt.subplots(figsize=(30, 12))
    plt.xticks(rotation = 90)
    g1 = sns.barplot(x="date", 
                 y=costStr, 
                 data=df_12m,
                 hue=prodStr,
                 palette="Reds_d")
    #plt.show())
    g1.set(title="Cost by month")
    g1.set(xticklabels=[])
    g1.set(xlabel=None)
    #plt.show()
    plt.clf()
""" 

def __visualize_abc_xyz(runConfig: TableRunConfig, df_abc : DataFrame, tableCategory : str):
    
    # Get filename prefix (translated if needed)
    file_prefix = get_filename_prefix(tableCategory)
    # Get municipal prefix
    mun_prefix = get_municipal_prefix(runConfig)
    
    #sns.set(font_scale=2.0)
    prodStr = runConfig.jsonData['columns']['Products']
    grouped_ABC_Heat_Count = df_abc.groupby(['ABC_Cost', 'XYZ_CO2']).count()
    result = grouped_ABC_Heat_Count.pivot_table(index = 'ABC_Cost', columns= 'XYZ_CO2', values= prodStr)
    f, left = plt.subplots(1,1,figsize=(10, 8))
    ax = sns.heatmap(result, annot = True, fmt = '.0f', cmap = 'coolwarm',ax=left, annot_kws={"fontsize":22}, cbar_kws={'label': get_text("Anzahl Güterkategorien", "Number of Goods Categories"), 'ticks':range(1, int(result.max().max()) + 1)})
    ax.collections[0].colorbar.set_label(get_text("Anzahl Güterkategorien", "Number of Goods Categories"), fontsize=24, labelpad=10)
    cax = ax.figure.axes[-1]
    cax.tick_params(labelsize=18)
    plt.xticks(rotation=0, fontsize=20)
    plt.yticks(rotation=0, fontsize=20)
    plt.xlabel(get_text("Regelmäßigkeit (XYZ)", "Regularity (XYZ)"),fontsize=24)
    plt.ylabel(get_text("Ausgaben", "Expenditures"), rotation=90, ha="right",fontsize=24)

    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABCCost_XYZCO2_Heatmap.png')    
    #plt.savefig('../Output/' + runConfig.outFileNameWithoutExtension + tableCategory + '_ABCCost_XYZCO2_Heatmap.png')
    plt.clf()
    plt.cla()
    plt.close() 
        
    grouped_ABC_Heat_Count = df_abc.groupby(['ABC_CO2', 'XYZ_CO2']).count()
    result = grouped_ABC_Heat_Count.pivot_table(index = 'ABC_CO2', columns= 'XYZ_CO2', values= prodStr)
    f, left = plt.subplots(1,1,figsize=(10, 8))
    ax = sns.heatmap(result, annot = True, fmt = '.0f', cmap = 'coolwarm',ax=left, annot_kws={"fontsize":22}, cbar_kws={'label': get_text("Anzahl Güterkategorien", "Number of Goods Categories"), 'ticks':range(1, int(result.max().max()) + 1)})
    ax.collections[0].colorbar.set_label(get_text("Anzahl Güterkategorien", "Number of Goods Categories"), fontsize=24, labelpad=10)
    cax = ax.figure.axes[-1]
    cax.tick_params(labelsize=18)
    plt.xticks(rotation=0, fontsize=20)
    plt.yticks(rotation=0, fontsize=20)
    plt.xlabel(get_text("Regelmäßigkeit (XYZ)", "Regularity (XYZ)"),fontsize=24)
    plt.ylabel(get_text("CO2 Äquivalenz", "CO2 Equivalence"), rotation=90, ha="center",fontsize=24)
    
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABCCO2_XYZCO2_Heatmap.png')    
    #plt.savefig('../Output/' + runConfig.outFileNameWithoutExtension + tableCategory + '_ABCCO2_XYZCO2_Heatmap.png')
    plt.clf()
    plt.cla()
    plt.close() 
    
    grouped_ABC_Heat_Count = df_abc.groupby(['ABC_CO2', 'XYZ_Cost']).count()
    result = grouped_ABC_Heat_Count.pivot_table(index = 'ABC_CO2', columns= 'XYZ_Cost', values= prodStr)
    f, left = plt.subplots(1,1,figsize=(10, 8))
    ax = sns.heatmap(result, annot = True, fmt = '.0f', cmap = 'coolwarm',ax=left, annot_kws={"fontsize":22}, cbar_kws={'label': get_text("Anzahl Güterkategorien", "Number of Goods Categories"), 'ticks':range(1, int(result.max().max()) + 1)})
    ax.collections[0].colorbar.set_label(get_text("Anzahl Güterkategorien", "Number of Goods Categories"), fontsize=24, labelpad=10)
    cax = ax.figure.axes[-1]
    cax.tick_params(labelsize=18)
    plt.xticks(rotation=0, fontsize=20)
    plt.yticks(rotation=0, fontsize=20)
    plt.xlabel(get_text("Regelmäßigkeit (XYZ)", "Regularity (XYZ)"),fontsize=24)
    plt.ylabel(get_text("CO2 Äquivalenz", "CO2 Equivalence"), rotation=90, ha="center",fontsize=24)
    
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABCCO2_XYZCost_Heatmap.png')    
    #plt.savefig('../Output/' + runConfig.outFileNameWithoutExtension + tableCategory + '_ABCCO2_XYZCost_Heatmap.png')
    plt.clf()
    plt.cla()
    plt.close() 
    
    #sns.set(font_scale=1.0)


def __visualize_aggregates(runConfigs: list[TableRunConfig]):
    
    if len(runConfigs) < 1:
        return
    plt.clf()
    plt.cla()
    plt.close()
    

    #sns.set(font_scale=1.0)

    # normal barplot
    for runConfig in runConfigs:
        # Get municipal prefix
        mun_prefix = get_municipal_prefix(runConfig)
        
        f = plt.figure(figsize=(20, 8))
        plt.tick_params(bottom = False)
        xaxis = runConfig.jsonData["columns"]["Products"]
        yaxis = runConfig.jsonData["columns"]["Cost"]
        g1 = sns.barplot(
            x = xaxis, 
            y = yaxis,
            width=1,
            data = runConfig.tableData,
            hue = xaxis,
            palette= runConfig.jsonData["visualizepalette"],
            errorbar=None,
            legend=False
        )
        g1.set(title="Ausgaben über Zeit")
        g1.set(xticklabels=[])
        g1.set(xlabel=None)   
        plt.yticks(fontsize=16)     
        plt.savefig(runConfig.output + mun_prefix + 'CostOverview.png')
        #plt.savefig('../Output/' + runConfigs[0].outFileNameWithoutExtension + '_CostOverview.png')       
        plt.clf()
        plt.cla()
        plt.close()
    
    # sorted barplot

    for runConfig in runConfigs:
        # Get municipal prefix (re-declare in this loop as well)
        mun_prefix = get_municipal_prefix(runConfig)
        
        f = plt.figure(figsize=(20, 8))
        plt.tick_params(bottom = False)
        xaxis = runConfig.jsonData["columns"]["Products"]
        yaxis = runConfig.jsonData["columns"]["Cost"]
        df = runConfig.tableData.sort_values(yaxis, ascending=False)
        g1 = sns.barplot(
            x = xaxis, 
            y = yaxis,
            width=1,
            data = df,
            hue = xaxis,
            palette= runConfig.jsonData["visualizepalette"],
            errorbar=None,
            legend=False
        )
        g1.set(title=get_text("Ausgaben geordnet", "Expenditures Sorted"))
        plt.title(get_text("Ausgaben geordnet", "Expenditures Sorted"), fontsize=22)
        g1.set(xticklabels=[])
        g1.set(xlabel=None)        
        
        plt.ylabel(get_text("Ausgaben Betrag", "Expenditure Amount"), fontsize=22)
        plt.savefig(runConfig.output + mun_prefix + 'CostSorted.png')
        plt.clf()
        plt.cla()
        plt.close()
    #plt.savefig('../Output/' + runConfigs[0].outFileNameWithoutExtension + '_CostSorted.png')       
    #plt.savefig('../Output/' + saveNamePrefix + "_" + runConfig.tableFileName.removesuffix('.xlsx') + '.png')

        
    # sorted logarithmic scatterplot (using scatter instead of barplot to fix scale issues)
    for runConfig in runConfigs:
        # Get municipal prefix (re-declare in this loop as well)
        mun_prefix = get_municipal_prefix(runConfig)
        
        xaxis = runConfig.jsonData["columns"]["Products"]
        yaxis = runConfig.jsonData["columns"]["Cost"]
        df = runConfig.tableData.sort_values(yaxis, ascending=False).reset_index(drop=True)
        df["rowindex"] = df.index
        
        f = plt.figure(figsize=(20, 8))
        plt.scatter(df["rowindex"], df[yaxis])
        plt.yscale('log')
        plt.title(get_text("Ausgaben geordnet, logarithmisch", "Expenditures Sorted, logarithmic"), fontsize=22)
        plt.ylabel(get_text("Ausgaben Betrag", "Expenditure Amount"), fontsize=22)
        plt.yticks(fontsize=18)  
        plt.savefig(runConfig.output + mun_prefix + '_CostSortedLog.png')
        #plt.savefig('../Output/' + runConfigs[0].outFileNameWithoutExtension + '_CostSortedLog.png')               
        #plt.savefig('../Output/' + saveNamePrefix + "_log_" + runConfig.tableFileName.removesuffix('.xlsx') + '.png')
        #plt.show()
        plt.clf()
        plt.cla()
        plt.close()
    return

def __plot_timeline(runConfig: TableRunConfig, df_split : DataFrame, df_abc : DataFrame, savePrefix : str):
    if df_split.empty or df_abc.empty:
        return
    costStr = runConfig.jsonData['columns']['Cost']
    dateStr = runConfig.jsonData['columns']['Date']
    prodStr = runConfig.jsonData['columns']['Products']
    co2Str = "kgCO2Equivalent"
    print("plotting " + savePrefix + "\n")
    
    # Get filename prefix (translated if needed)
    file_prefix = get_filename_prefix(savePrefix)
    # Get municipal prefix
    mun_prefix = get_municipal_prefix(runConfig)
    
    # Get filename prefix (translated if needed)
    file_prefix = get_filename_prefix(savePrefix)
    
    # Check if translated product column exists (minimal change for translation)
    prod_display = prodStr
    if Config.get("EnableTranslation", False) and (prodStr + "_EN") in df_split.columns:
        prod_display = prodStr + "_EN"
    
    df_split = df_split.copy()
    df_split[dateStr] = pd.to_datetime(df_split[dateStr]).dt.strftime('%Y-%m')
    
    #barplot
    #plt.show(block = False)
    plt.clf()
    plt.cla()
    plt.close()
    
    print(df_abc.head())
    
    #sns.set(font_scale=1.0)
    
    # A group cost lines
    As = df_abc.query("ABC_Cost == 'A'").nlargest(10, costStr)

    legend_values = []
    # Include prod_display column if it exists and is different from prodStr
    cols_to_select = [prodStr, dateStr, costStr]
    if prod_display != prodStr and prod_display in df_split.columns:
        cols_to_select.append(prod_display)
    df_grouped = df_split.loc[:, cols_to_select]
    
    df_grouped = df_grouped[df_grouped[prodStr].isin(As[prodStr])]
    df_grouped = df_grouped.sort_values(dateStr)
    
    f = plt.figure(figsize=(20, 12))
    
    #plt.bar(value[dateStr], value[costStr], data=value)
    p = sns.barplot(data=df_grouped, x=dateStr, y=costStr, hue=prod_display,errorbar=None)
    p.set(title=get_text("Güter Ausgaben Gruppe A", "Goods Expenditures Group A"))
    # Remove legend title (don't show column name like "Text_EN")
    legend = plt.legend()
    legend.set_title('')
    plt.xticks(rotation=45, fontsize=16)
    plt.yticks(rotation=0)
    
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_Cost_A_Timeline_graph.png')
    plt.yscale('log')
    p.set(title=get_text("Güter Ausgaben Gruppe A, logarithmisch", "Goods Expenditures Group A, logarithmic"))
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_CO2_A_Log_Timeline_graph.png')
    plt.clf()
    plt.cla()
    plt.close()
    
    # A group CO2 lines
    As = df_abc.query("ABC_CO2 == 'A'").nlargest(10, co2Str)
    
    legend_values = []
    df_grouped = df_split.copy()
    
    df_grouped = df_grouped[df_grouped[prodStr].isin(As[prodStr])]
    df_grouped = df_grouped.sort_values(dateStr)
    
    #df_grouped.to_excel(runConfig.output + file_prefix + 'test.xlsx')
    f = plt.figure(figsize=(20, 12))

    
    #plt.bar(value[dateStr], value[costStr], data=value)
    p = sns.barplot(data=df_grouped, x=dateStr, y="kgCO2Equivalent", hue=prod_display,errorbar=None,dodge=True)
    plt.title(get_text("CO2 Äquivalenz Gruppe A", "CO2 Equivalence Group A"), fontsize=22)
    plt.xticks(rotation=45, fontsize=16)
    plt.yticks(rotation=0, fontsize=22)
    # Remove legend title
    legend = plt.legend(fontsize=20)
    legend.set_title('')
    plt.xlabel(get_text("Buchungsdatum", "Booking Date"), rotation=0, fontsize=22)
    plt.ylabel(get_text("Kg CO2 Äquivalenz", "Kg CO2 Equivalent"), rotation=90, fontsize=22)
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_CO2_A_Timeline_graph.png')
    plt.yscale('log')

    plt.title(get_text("CO2 Äquivalenz Gruppe A, logarithmisch", "CO2 Equivalence Group A, logarithmic"), fontsize=32)
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_CO2_A_Log_Timeline_graph.png')
    plt.clf()
    plt.cla()
    plt.close()    
    
    # B group CO2 lines
    Bs = df_abc.query("ABC_CO2 == 'B'").nlargest(10, co2Str)
    if not Bs.empty:
        legend_values = []
        df_grouped = df_split.copy()
        
        df_grouped = df_grouped[df_grouped[prodStr].isin(Bs[prodStr])]
        df_grouped = df_grouped.sort_values(dateStr)
        
        #df_grouped.to_excel(runConfig.output + file_prefix + 'test.xlsx')
        f = plt.figure(figsize=(20, 12))
        
        #plt.bar(value[dateStr], value[costStr], data=value)
        p = sns.barplot(data=df_grouped, x=dateStr, y="kgCO2Equivalent", hue=prod_display,errorbar=None,dodge=True)
        plt.xticks(rotation=45, fontsize=16)
        plt.yticks(rotation=0, fontsize=22)
        # Remove legend title
        legend = plt.legend(fontsize=20)
        legend.set_title('')
        plt.title(get_text("CO2 Äquivalenz Gruppe B", "CO2 Equivalence Group B"), fontsize=32)
        plt.xlabel(get_text("Buchungsdatum", "Booking Date"), rotation=0, fontsize=22)
        plt.ylabel(get_text("Kg CO2 Äquivalenz", "Kg CO2 Equivalent"), rotation=90, fontsize=22)
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_CO2_B_Timeline_graph.png')

        plt.title(get_text("CO2 Äquivalenz Gruppe B, logarithmisch", "CO2 Equivalence Group B, logarithmic"), fontsize=32)
        plt.yscale('log')
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_CO2_B_Log_Timeline_graph.png')
        plt.clf()
        plt.cla()
        plt.close()  
        
        # B group CO2 lines
    Cs = df_abc.query("ABC_CO2 == 'C'").nlargest(10, co2Str)
    if not Cs.empty:
        legend_values = []
        df_grouped = df_split.copy()
        
        df_grouped = df_grouped[df_grouped[prodStr].isin(Cs[prodStr])]
        df_grouped = df_grouped.sort_values(dateStr)
        
        #df_grouped.to_excel(runConfig.output + file_prefix + 'test.xlsx')
        f = plt.figure(figsize=(20, 12))
        
        #plt.bar(value[dateStr], value[costStr], data=value)
        p = sns.barplot(data=df_grouped, x=dateStr, y="kgCO2Equivalent", hue=prod_display,errorbar=None,dodge=True)
        plt.title(get_text("CO2 Äquivalenz Gruppe C", "CO2 Equivalence Group C"), fontsize=32)
        plt.xticks(rotation=45, fontsize=16)
        plt.yticks(rotation=0, fontsize=22)
        # Remove legend title
        legend = plt.legend(fontsize=20)
        legend.set_title('')
        plt.xlabel(get_text("Buchungsdatum", "Booking Date"), rotation=0, fontsize=22)
        plt.ylabel(get_text("Kg CO2 Äquivalenz", "Kg CO2 Equivalent"), rotation=90, fontsize=22)
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_CO2_C_Timeline_graph.png')
        
        plt.title(get_text("CO2 Äquivalenz Gruppe C, logarithmisch", "CO2 Equivalence Group C, logarithmic"), fontsize=32)
        plt.yscale('log')
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_ABC_CO2_C_Log_Timeline_graph.png')
        plt.clf()
        plt.cla()
        plt.close()  
        
    Xs = df_abc.query("XYZ_CO2 == 'X'").nlargest(10, co2Str)
    if not Xs.empty:
        legend_values = []
        df_grouped = df_split.copy()
        
        df_grouped = df_grouped[df_grouped[prodStr].isin(Xs[prodStr])]
        df_grouped = df_grouped.sort_values(dateStr)
        
        #df_grouped.to_excel(runConfig.output + file_prefix + 'test.xlsx')
        f = plt.figure(figsize=(20, 8))
        
        #plt.bar(value[dateStr], value[costStr], data=value)
        p = sns.barplot(data=df_grouped, x=dateStr, y=co2Str, hue=prod_display,errorbar=None,dodge=True)
        p.set(title=get_text("CO2 Äquivalenz Gruppe X", "CO2 Equivalence Group X"))
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_XYZ_CO2_X_Timeline_graph.png')
        
        p.set(title=get_text("CO2 Äquivalenz Gruppe X, logarithmisch", "CO2 Equivalence Group X, logarithmic"))
        plt.yscale('log')
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_XYZ_CO2_X_Log_Timeline_graph.png')
        plt.clf()
        plt.cla()
        plt.close()  
        
    Ys = df_abc.query("XYZ_CO2 == 'Y'").nlargest(10, co2Str)
    if not Ys.empty:
        legend_values = []
        df_grouped = df_split.copy()
        
        df_grouped = df_grouped[df_grouped[prodStr].isin(Ys[prodStr])]
        df_grouped = df_grouped.sort_values(dateStr)
        
        #df_grouped.to_excel(runConfig.output + file_prefix + 'test.xlsx')
        f = plt.figure(figsize=(20, 8))
        
        #plt.bar(value[dateStr], value[costStr], data=value)
        p = sns.barplot(data=df_grouped, x=dateStr, y=co2Str, hue=prod_display,errorbar=None,dodge=True)
        p.set(title=get_text("CO2 Äquivalenz Gruppe Y", "CO2 Equivalence Group Y"))
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_XYZ_CO2_Y_Timeline_graph.png')
        plt.yscale('log')
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_XYZ_CO2_Y_Log_Timeline_graph.png')
        plt.clf()
        plt.cla()
        plt.close()  
        
    Zs = df_abc.query("XYZ_CO2 == 'Z'").nlargest(10, co2Str)
    if not Zs.empty:
        legend_values = []
        df_grouped = df_split.copy()
        
        df_grouped = df_grouped[df_grouped[prodStr].isin(Zs[prodStr])]
        df_grouped = df_grouped.sort_values(dateStr)
        
        #df_grouped.to_excel(runConfig.output + file_prefix + 'test.xlsx')
        f = plt.figure(figsize=(20, 8))
        
        #plt.bar(value[dateStr], value[costStr], data=value)
        p = sns.barplot(data=df_grouped, x=dateStr, y=co2Str, hue=prod_display,errorbar=None,dodge=True)
        p.set(title=get_text("CO2 Äquivalenz Gruppe Z", "CO2 Equivalence Group Z"))
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_XYZ_CO2_Z_Timeline_graph.png')
        plt.yscale('log')
        plt.savefig(runConfig.output + mun_prefix + file_prefix + '_XYZ_CO2_Z_Log_Timeline_graph.png')
        plt.clf()
        plt.cla()
        plt.close()  
        
    # X group cost lines
    As = df_abc.query("XYZ_Cost == 'X'").nlargest(10, costStr)

    legend_values = []
    df_grouped = df_split.loc[:, [prodStr, dateStr, costStr]]
    
    # If translation enabled, include translated column
    if prod_display != prodStr and prod_display in df_split.columns:
        df_grouped = df_split.loc[:, [prodStr, dateStr, costStr, prod_display]].copy()
    
    df_grouped = df_grouped[df_grouped[prodStr].isin(As[prodStr])]
    # Sort by date to prevent erroneous lines going back and forth
    df_grouped = df_grouped.sort_values(dateStr)
        
    grouped = df_grouped.groupby([prodStr])
    f = plt.figure(figsize=(20, 8))
    for group, value in grouped:
        # Ensure each group is sorted by date
        value = value.sort_values(dateStr)
        plt.plot(value[dateStr], value[costStr], '--')
        # Use translated name if available, otherwise use German name
        if prod_display != prodStr and prod_display in value.columns and not value.empty:
            legend_name = value[prod_display].iloc[0]
        else:
            legend_name = group
        legend_values.append(legend_name)
    plt.legend(legend_values,loc='upper left')
    plt.xticks(rotation=45)
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_X_Cost_graph.png')
    plt.clf()
    plt.cla()
    plt.close()
    # Y group cost lines
    As = df_abc.query("XYZ_Cost == 'Y'").nlargest(10, costStr)

    legend_values = []
    df_grouped = df_split.loc[:, [prodStr, dateStr, costStr]]
    
    # If translation enabled, include translated column
    if prod_display != prodStr and prod_display in df_split.columns:
        df_grouped = df_split.loc[:, [prodStr, dateStr, costStr, prod_display]].copy()
    
    df_grouped = df_grouped[df_grouped[prodStr].isin(As[prodStr])]
    # Sort by date to prevent erroneous lines going back and forth
    df_grouped = df_grouped.sort_values(dateStr)
        
    grouped = df_grouped.groupby([prodStr])
    f = plt.figure(figsize=(20, 8))
    for group, value in grouped:
        # Ensure each group is sorted by date
        value = value.sort_values(dateStr)
        plt.plot(value[dateStr], value[costStr], '--')
        # Use translated name if available, otherwise use German name
        if prod_display != prodStr and prod_display in value.columns and not value.empty:
            legend_name = value[prod_display].iloc[0]
        else:
            legend_name = group
        legend_values.append(legend_name)
    plt.legend(legend_values, loc='upper left')
    plt.xticks(rotation=45)
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_Y_Cost_graph.png')
    plt.clf()
    plt.cla()
    plt.close()
    # Z group cost lines
    As = df_abc.query("XYZ_Cost == 'Z'").nlargest(10, costStr)

    legend_values = []
    df_grouped = df_split.loc[:, [prodStr, dateStr, costStr]]
    
    # If translation enabled, include translated column
    if prod_display != prodStr and prod_display in df_split.columns:
        df_grouped = df_split.loc[:, [prodStr, dateStr, costStr, prod_display]].copy()
    
    df_grouped = df_grouped[df_grouped[prodStr].isin(As[prodStr])]
    # Sort by date to prevent erroneous lines going back and forth
    df_grouped = df_grouped.sort_values(dateStr)
        
    grouped = df_grouped.groupby([prodStr])
    f = plt.figure(figsize=(20, 8))
    for group, value in grouped:
        # Ensure each group is sorted by date
        value = value.sort_values(dateStr)
        plt.plot(value[dateStr], value[costStr], '--')
        # Use translated name if available, otherwise use German name
        if prod_display != prodStr and prod_display in value.columns and not value.empty:
            legend_name = value[prod_display].iloc[0]
        else:
            legend_name = group
        legend_values.append(legend_name)
    plt.legend(legend_values,loc='upper left')
    plt.xticks(rotation=45)
    plt.savefig(runConfig.output + mun_prefix + file_prefix + '_Z_Cost_graph.png')
    plt.clf()
    plt.cla()
    plt.close()
