import json
import glob
import os
import pandas as pd
from src.constants import SECONDARY_LIST, GRENADE_MAP

def inventory_convert(inventory):
    if not inventory or pd.isna(inventory):
        return False
    
    items = {
        'primary': None,
        'secondary': None,
        'smoke': 0,
        'flash': 0,
        'molotov': 0,
        'incend': 0,
        'decoy': 0,
        'has_zeus': 0
    }
    
    _ = inventory.pop(0)
    while inventory:
        item = inventory.pop(0)
        if item in GRENADE_MAP:
            items[GRENADE_MAP[item]] += 1
        elif item in SECONDARY_LIST:
            items['secondary'] = item
        elif item == 'Zeus x27':
            items['has_zeus'] = True
        else:
            items['primary'] = item
    
def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        return True
    else:
        return False

def clear_demos(demo_path='data/demos/'):
    print('Clearing old and corrupt demos')
    for old_demo in glob.glob(os.path.join(demo_path, '*.dem')):
        print(f'Deleted {old_demo}')
        os.remove(old_demo)