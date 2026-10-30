import paths
import os.path
from pandas import DataFrame

class TableRunConfig:
    jsonFileName : str
    outFileExtension : str = ".xlsx"
    outFileName : str = "None"
    tableFileName : str
    tableFilePath : str
    config : dict
    tableData : DataFrame
    df_replaced : DataFrame = None
    saved : dict[str, DataFrame] = dict[str, DataFrame]
    currentDataType : str = ""
    
    df_split_fuels : DataFrame = None
    df_split_consumables : DataFrame = None
    df_split_resuables : DataFrame = None
    
    df_abc_all : DataFrame = None
    #split fuel
    df_abc_fuels : DataFrame = None
    
    #split gebrauchswaren
    df_abc_usables : DataFrame = None
    
    #split verbrauchswaren
    df_abc_consumables : DataFrame = None
    
    df_xyz_fuels : DataFrame = None
    df_xyz_consumables : DataFrame = None
    df_xyz_reusables : DataFrame = None
    
    df_xyz_co2_fuels : DataFrame = None
    df_xyz_co2_consumables : DataFrame = None
    df_xyz_co2_reusables : DataFrame = None
    
    df_aggregate_cost : DataFrame = None
    df_aggregate_cost_noneg : DataFrame = None    
    
    def __init__(self, jsonFileName, parsed_json):
        self.jsonFileName = jsonFileName
        self.tableFileName = parsed_json["table"]
        self.tableFilePath = paths.dataset(self.tableFileName)
        self.outFileNameWithoutExtension = self.tableFileName.removesuffix('.xlsx') 
        self.jsonData = parsed_json
        
    def isValid(self) -> bool:
        if not self.jsonFileName:
            print("TableRunConfig not valid : No given json file name")
            return False
        if not self.tableFileName or not self.tableFileName.endswith(".xlsx"):
            print("TableRunConfig not valid : Table file name empty or does not end with .xlsx : ", self.jsonFileName)
            return False
        if not os.path.exists(self.tableFilePath):
            print("TableRunConfig not valid : Table file does not exist ", self.tableFilePath)
            return False
        return True
        
        
        

        
