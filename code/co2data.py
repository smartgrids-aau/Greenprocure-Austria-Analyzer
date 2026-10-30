import paths
from pandas import DataFrame
import pandas as pd
from config import Config
from tableConfig import TableRunConfig

class CO2Values:
    co2df : DataFrame
    prodStr : str
    co2ValuesColName : str = paths.FACTOR_COLUMN
    translationColName : str = "Material_EN"
    
    def __init__(self, productColumnName : str) -> None:
        self.prodStr = productColumnName
        self.co2df : DataFrame = pd.read_excel(paths.CO2_FILE)
    
    def Valid(self) -> bool:
        return self.prodStr != None and not self.co2df.empty
    
    def GetValueFor(self, product : str) -> float:
        """Get CO2 value for a product"""
        co2df = self.co2df
        df_l = co2df.loc[co2df["Material"] == product, self.co2ValuesColName]
        if not df_l.empty :
            return df_l.item()        
        return None
    
    def GetTranslation(self, product : str) -> str:
        """
        Get English translation for a product name from CO2Data.xlsx
        Returns original if translation not available or translation disabled
        """
        if not Config.get("EnableTranslation", False):
            return product
            
        co2df = self.co2df
        
        if self.translationColName not in co2df.columns:
            print(f"Warning: {self.translationColName} column not found in CO2Data.xlsx")
            return product
        
        df_l = co2df.loc[co2df["Material"] == product, self.translationColName]
        if not df_l.empty and pd.notna(df_l.item()):
            return df_l.item()
        
        return product
    
    def TranslateProductColumn(self, df: DataFrame) -> DataFrame:
        """
        Add translated product column to dataframe if translation is enabled
        """
        if not Config.get("EnableTranslation", False):
            return df
        
        df[self.prodStr + "_EN"] = df[self.prodStr].apply(self.GetTranslation)
        
        return df
    
    def ProcessValues(self, df : DataFrame, tblName : str):
        """Process CO2 values and optionally add translations"""
        print("Assigning CO2 values for table ", tblName)
        print(df.head())
        print(len(df))
        
        df = df[df["Menge (in Gramm)"].notna()].copy()
        df["Menge (in kg)"] = df["Menge (in Gramm)"] / 1000
        print(df.head())
        print(len(df))
        df["gCO2PerKGWare"] = df[self.prodStr].apply(self.GetValueFor)
        
        df = df[df["gCO2PerKGWare"].notna()].copy()
        df["kgCO2PerKGWare"] = df["gCO2PerKGWare"] / 1000
        print(df.head())
        df["kgCO2Equivalent"] = df["kgCO2PerKGWare"] * df["Menge (in kg)"]
        print(len(df))
        print(df.head())
        
        df = self.TranslateProductColumn(df)
        
        return df


co2Values = {
    "Kopierpapier" : 0.75,
    "Toilettenpapier" : 0.4,
    "Müllsäcke" : 0.5376,
    "Blumen" : 0.1,
    "Splitt" : 0.0851,
    "Flockungsmittel" : 0.47,
    "Diesel" : 16.81,
    "Treibstoff" : 16.81
}
