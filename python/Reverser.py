import json

import pdb

from GlobalVar import typ_to_func, typ_to_addr

def create_typ_to_func(json_names):
    for json_name in json_names:
        with open(json_name) as json_file:
            json_dic = json.load(json_file)
        color_slots = ''
        gobo_slots = ''
        name = json_dic['name']
        print("########################################")
        print(name)
        for mode in json_dic['modes']:
            color = ''
            gobo = ''
            color_slots = ''
            gobo_slots = ''
            if 'wheels' in json_dic.keys():
                for wheel in list(json_dic['wheels'].keys()):
                    if 'Color' in wheel:
                        color += 'Wheel'
                        color_slots = []
                        for slot in json_dic['wheels'][wheel]['slots']:
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
                            except:
                                pass
                    if 'Gobo' in wheel:
                        gobo = 'Wheel'
                        gobo_slots = []
                        for slot in json_dic['wheels'][wheel]['slots']:
                            if slot['type'] == 'Open':
                                slot_name = 'Open'
                            elif slot['type'] == 'Gobo':
                                slot_name = slot['name']
                            try:
                                gobo_slots.append(slot_name)
                            except:
                                pass
                        
            if all(channel in ['channels'] for channel in ['Red', 'Green', 'Blue']):
                color += 'RGB'
                if 'Amber' in mode['channels']:
                    color += 'A'
                if 'White' in mode['channels']:
                    color += 'W'
            if any(channel in mode['channels'] for channel in ['Intensity', 'Dimmer']):
                inten = True
            
            print("########################################")
            print("name: {0:s}".format(mode['name']))
            print("color: {0:s}".format(color))
            if color_slots:
                for i in color_slots:
                    print("\t{0:s}".format(str(i)))
            print("gobo: {0:s}".format(gobo))
            if gobo_slots:
                for i in gobo_slots:
                    print("\t{0:s}".format(i))
            print("inten: {0:b}".format(inten))
            print("########################################\n")

create_typ_to_func(["../dev/ofl-json/mac-250-krypton.json","../dev/ofl-json/generic/rgba-fader.json"])
