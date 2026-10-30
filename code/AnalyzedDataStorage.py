from pandas import DataFrame
from tableConfig import TableRunConfig


class AnalyzedDataPack:
    runConfig : TableRunConfig
    df : DataFrame

class AnalyzedDataStorage:
    #contains data for ABC cost analysis
    # All, [AnalyzedData...]
    # Treibstoffe, [AnalyzedData...]
    # Verbrauchsgüter, [AnalyzedData...]
    # Gebrauchsgüter, [AnalyzedData...]
    abcCost : dict[str, list[AnalyzedDataPack]]
    #contains data for ABC cost analysis
    # All, [AnalyzedData...]
    # Treibstoffe, [AnalyzedData...]
    # Verbrauchsgüter, [AnalyzedData...]
    # Gebrauchsgüter, [AnalyzedData...]
    abcCO2 : dict[str, list[AnalyzedDataPack]]
    
    abcCO2Data : dict[str, list[AnalyzedDataPack]]
    aggregateCost : list[AnalyzedDataPack]
