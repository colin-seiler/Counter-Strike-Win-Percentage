import json
import os
from src.constants import GRENADE_LIST, SECONDARY_LIST

def inventory_convert(inventory):
    items = {
        'knife': None,
        'secondary': None,
        'primary': None,
        'grenades': [],
        'zeus': False,
    }

    if not inventory:
        return json.dumps(items)
    
    else:
        items['knife'] = inventory.pop(0)
        while inventory:
            item = inventory.pop(0)
            if item in GRENADE_LIST:
                items['grenades'].append(item)
            elif item in SECONDARY_LIST:
                items['secondary'] = item
            elif item == 'Zeus x27':
                items['zeus'] = True
            else:
                items['primary'] = item
        
        return json.dumps(items)
    
def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        return True
    else:
        return False