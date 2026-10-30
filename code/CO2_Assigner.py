import random
from co2data import co2Values

def CO2_Assignment(product):
    if product in co2Values:
        return co2Values[product]
    else:
        return 0.0
