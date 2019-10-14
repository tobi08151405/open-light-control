import json

from GlobalVar import typ_to_func, typ_to_addr

def create_typ_to_func(json_names):
    for json_name in json_names:
        with open(json_name) as json_file:
            json_dic = json.load(json_file)
        name = json_dic['name']
        if 'wheels' in json_dic.keys():
            if any('Color' in i for i in list(json_dic['wheels'].keys())):
                color = 'Wheel'
                for i in list(json_dic['wheels'].keys()):
                    if 'Color' in i:
                        wheelpos = i
                color_slots = []
                for slot in json_dic['wheels']['Color Wheel']['slots']:
                    if slot['type'] == 'Open':
                        slot_name = 'Open'
                        slot_color = '#ffffff'
                    elif slot['type'] == 'Color':
                        if 'colorTemperature' in slot.keys():
                            slot_name = slot['colorTemperature']
                            slot_color = '#ffffff'
                        elif 'colors' in slot.keys():
                            if 'name' in slot.keys():
                                slot_name = slot['name']
                            else:
                                slot_name = 'Color'
                            slot_color = slot['colors'][0]
                    try:
                        color_slots.append({'name':slot_name,'color':slot_color})
            if any('Gobo' in i for i in list(json_dic['wheels'].keys())):
                gobo = 'Wheel'
        if all(i in list(json_dic['availableChannels'].keys()) for i in ['Red', 'Green', 'Blue']):
            if 'White' in json_dic['availableChannels'].keys():
                color = 'RGBW'
            else:
                color = 'RGB'
        if any(i in list(json_dic['availableChannels'].keys()) for i in ['Intensity', 'Dimmer']):
            inten = True
        
        print(name,color,gobo,inten,sep="; ")
        

create_typ_to_func(["../dev/ofl-json/mac-250-krypton.json"])
