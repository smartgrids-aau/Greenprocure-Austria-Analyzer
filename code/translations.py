"""
Translation module for converting German terms to English
"""
from config import Config

# Category translations
CATEGORIES = {
    "Treibstoffe": "Fuels",
    "Verbrauchsgüter": "Consumables",
    "Gebrauchsgüter": "Investment Goods",
}

# Column name translations
COLUMNS = {
    "Menge (in Gramm)": "Quantity (in Grams)",
    "Menge (in kg)": "Quantity (in kg)",
    "kgCO2Equivalent": "kg CO2 Equivalent",
    "kgCO2PerKGWare": "kg CO2 per kg Goods",
    "gCO2PerKGWare": "g CO2 per kg Goods",
    "ABC_Cost": "ABC Cost",
    "ABC_CO2": "ABC CO2",
    "XYZ_Cost": "XYZ Cost",
    "XYZ_CO2": "XYZ CO2",
}

# Label translations for plots
LABELS = {
    "Datum": "Date",
    "Kosten": "Cost",
    "CO2 Äquivalenz": "CO2 Equivalence",
    "Regelmäßigkeit": "Regularity",
    "Ausgaben": "Expenditures",
    "logarithmisch": "logarithmic",
    "Gruppe": "Group",
}

# File prefix translations
FILE_PREFIXES = {
    "Gebrauchsgüter": "Investment_Goods",
    "Verbrauchsgüter": "Consumables",
    "Treibstoffe": "Fuels",
}

# Municipality name translations (for file names)
MUNICIPALITY_NAMES = {
    "MunicipalityA": "MunicipalityA",  # Keep as is or customize
    "MunicipalityB": "MunicipalityB",  # Keep as is or customize
    "KM": "MunB",  # Shorthand used in existing files
    "FG": "MunA",  # Shorthand used in existing files
}


def translate_text(text: str) -> str:
    """
    Translate a German text to English if translation is enabled.
    Returns original text if translation is disabled or no translation exists.
    
    Args:
        text: German text to translate
        
    Returns:
        Translated text if EnableTranslation is True, otherwise original
    """
    if not Config.get("EnableTranslation", False):
        return text
    
    # Check in all translation dictionaries
    for trans_dict in [CATEGORIES, COLUMNS, LABELS, FILE_PREFIXES]:
        if text in trans_dict:
            return trans_dict[text]
    
    return text


def translate_category(category: str) -> str:
    """Translate category name (Treibstoffe, Verbrauchsgüter, Gebrauchsgüter)"""
    if not Config.get("EnableTranslation", False):
        return category
    return CATEGORIES.get(category, category)


def translate_column(column: str) -> str:
    """Translate column name"""
    if not Config.get("EnableTranslation", False):
        return column
    return COLUMNS.get(column, column)


def translate_file_prefix(prefix: str) -> str:
    """Translate file name prefix"""
    if not Config.get("EnableTranslation", False):
        return prefix
    return FILE_PREFIXES.get(prefix, prefix)


def get_municipality_code(name: str) -> str:
    """Get translated municipality code for file names"""
    if not Config.get("EnableTranslation", False):
        return name
    return MUNICIPALITY_NAMES.get(name, name)


# Product name translation happens via CO2Data.xlsx Material_EN column
# See co2data.py for implementation
