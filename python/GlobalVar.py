serial_enable = True

output_freeze = [False]

rows = 6
cols = 3
faders = 3
encoders = 1

universe_num = 4

uni_map = dict(zip(range(universe_num), range(universe_num)))
uni_map_ = {v: k for k, v in uni_map.items()}

error_log_global = []

typ_to_func = {}
typ_to_addr = {}

nr_to_typ = {}
nr_to_addr = {}
nr_in_use={}

in_use=[]

# curr_page=0
# fader_map = [[],[],[]]
# for i in range(faders):
#     fader_map[0].append(0)
#     fader_map[1].append(0)
#     fader_map[2].append(0)

cuelist_dict = {
    "papa_spot": {
        "options": {"warp_at_end": True},
        0: ["Spot On", [11, 'Dimmer', 100]],
        1: ["Spot Off", [11, 'Dimmer', 0]]
    }
}

key_mapping = {
    #key_num: ["type", "Text", direkt]
    #type = "pad", "command"
    "17": ["pad", "7", True],
    "1": ["pad", "8", True],
    "2": ["pad", "9", True],
    "3": ["pad", "4", True],
    "4": ["pad", "5", True],
    "5": ["pad", "6", True],
    "6": ["pad", "1", True],
    "7": ["pad", "2", True],
    "8": ["pad", "3", True],
    "9": ["pad", "*", True],
    "10": ["pad", "0", True],
    "11": ["pad", "Return", False],
    "12": ["pad", "r", True],
    "13": ["pad", "g", True],
    "14": ["pad", "b", True],
    "15": ["pad", "c", True],
    "16": ["pad", "/", True],
    "0": ["cuelist", "papa_spot", "go"]
}

fader_mapping = {
    "0": "back",
    "1": "grund",
    "2": "spot"
}

slider_stylesheet = """
.QSlider {
    min-width: 68px;
    max-width: 68px;
}

.QSlider::groove:vertical {
    border: 1px solid #262626;
    width: 5px;
    margin: 0 12px;
}

.QSlider::handle:vertical {
    background: #000000;
    border: 5px solid #000000;
    height: 23px;
    width: 100px;
    margin: -12px -12px;
}"""
