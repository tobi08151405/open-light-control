from GlobalVar import typ_to_func, typ_to_addr
import json

def mode_to_func(json_dic, mode):
    color = ''
    gobo = ''
    color_slots = ''
    gobo_slots = ''
    name = json_dic['name']
    typ_mode_name = "{0:s} {1:s}".format(name, mode['name'])
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
                        else:
                            continue
                    else:
                        continue
                    try:
                        color_slots.append(
                            {'name': slot_name, 'color': slot_color})
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
                    else:
                        continue
                    try:
                        gobo_slots.append(slot_name)
                    except:
                        pass

    if all(any(channel in i for i in mode['channels']) for channel in ['Red', 'Green', 'Blue']) or all(any(channel in i for i in mode['channels']) for channel in ['Cyan', 'Magenta', 'Yellow']):
        color += 'RGB'
        if 'Amber' in mode['channels']:
            color += 'A'
        if 'White' in mode['channels']:
            color += 'W'
    if any(channel in mode['channels'] for channel in ['Intensity', 'Dimmer']):
        dimmer = True
    else:
        dimmer = False
    if any('Pan' in i for i in mode['channels']):
        pan = True
    else:
        pan = False
    if any('Tilt' in i for i in mode['channels']):
        tilt = True
    else:
        tilt = False

    if not color:
        color = False
    if not gobo:
        gobo = False

    typ_to_func[typ_mode_name] = {"ChannelSpan": len(
        mode['channels']), "Dimmer": dimmer, "Color": color, "Gobo": gobo, "Pan": pan, "Tilt": tilt}
    if color_slots:
        typ_to_func[typ_mode_name]["ColorWheel"] = color_slots
    if gobo_slots:
        typ_to_func[typ_mode_name]["GoboWheel"] = gobo_slots


def typ_to_modes_func(json_dic):
    for mode in json_dic['modes']:
        mode_to_func(json_dic, mode)


def create_typ_to_func(json_names):
    for json_name in json_names:
        try:
            with open(json_name) as json_file:
                json_dic = json.load(json_file)
                typ_to_modes_func(json_dic)
        except FileNotFoundError:
            print("file {0:s} not found!".format(json_name))


def mode_to_addr(json_dic, mode):
    name = json_dic['name']
    typ_mode_name = "{0:s} {1:s}".format(name, mode['name'])
    typ_to_addr[typ_mode_name] = {}
    for channel_name in mode['channels']:
        try:
            channel = json_dic['availableChannels'][channel_name]
            channel_num = mode['channels'].index(channel_name)
            channel_mode = ''
            if 'capability' in channel:
                channel_mode = "normal"
            elif 'capabilities' in channel:
                channel_mode = "split"
                split_list = []
            if channel_name == "Intensity":
                channel_name = "Dimmer"
            typ_to_addr[typ_mode_name][channel_name] = {
                "Channel": channel_num, "Mode": channel_mode}
            if channel_mode == "split":
                typ_to_addr[typ_mode_name][channel_name]['Split'] = {
                    split_list}
        except KeyError:
            pass


def typ_to_modes_addr(json_dic):
    for mode in json_dic['modes']:
        mode_to_addr(json_dic, mode)


def create_typ_to_addr(json_names):
    for json_name in json_names:
        try:
            with open(json_name) as json_file:
                json_dic = json.load(json_file)
                typ_to_modes_addr(json_dic)
        except FileNotFoundError:
            print("file {0:s} not found!".format(json_name))

#create_typ_to_func(["../dev/ofl-json/mac-250-krypton.json","../dev/ofl-json/generic/drgb-fader.json","../dev/ofl-json/generic/cmy-fader.json","../dev/ofl-json/generic/drgb-fader.json"])
#create_typ_to_func(["../dev/ofl-json/tao-led.json","../dev/ofl-json/generic/desk-channel.json","../dev/ofl-json/michi.json"])
#create_typ_to_addr(["../dev/ofl-json/tao-led.json","../dev/ofl-json/generic/desk-channel.json","../dev/ofl-json/michi.json"])

#with open("typ_to_func.json", 'w') as json_out:
    #json.dump(typ_to_func, json_out)

#with open("typ_to_addr.json", 'w') as json_out:
    #json.dump(typ_to_addr, json_out)
