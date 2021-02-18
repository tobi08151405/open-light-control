serial_enable = False

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
nr_in_use = {}

in_use_programmer = {}

curr_page = 0
fader_map = [[], [], []]
for i in range(faders):
    fader_map[0].append(0)
    fader_map[1].append(0)
    fader_map[2].append(0)

cuelist_dict = {
    "papa_spot": {
        "options": {"warp_at_end": True},
        0: ["Spot On", 0, [11, 'Dimmer', 100]],
        1: ["Spot Off", 0, [11, 'Dimmer', 0]]
    }
    # "pub":{
    #     "options": {"warp_at_end": True},
    #     0: ["standard", 0, [1, 'Dimmer', 0],[2, 'Dimmer', 100],[20, 'Dimmer', 0],[21, 'Dimmer', 0],[10, 'Dimmer', 80],[11, 'Dimmer', 0]],
    #     1: ["standard + L", 1, [1, 'Dimmer', 100],[2, 'Dimmer', 100],[20, 'Dimmer', 0],[21, 'Dimmer', 0],[10, 'Dimmer', 80],[11, 'Dimmer', 0]],
    #     2: ["standard bar", 3, [1, 'Dimmer', 100],[2, 'Dimmer', 100],[20, 'Dimmer', 50],[21, 'Dimmer', 50],[10, 'Dimmer', 80],[11, 'Dimmer', 0]],
    #     3: ["Dark", 3, [1, 'Dimmer', 0],[2, 'Dimmer', 0],[20, 'Dimmer', 0],[21, 'Dimmer', 20],[10, 'Dimmer', 0],[11, 'Dimmer', 0]],
    #     4: ["back to normal", 40, [1, 'Dimmer', 100],[2, 'Dimmer', 100],[20, 'Dimmer', 50],[21, 'Dimmer', 50],[10, 'Dimmer', 80],[11, 'Dimmer', 0]],
    #     5: ["end before", 3, [1, 'Dimmer', 0],[2, 'Dimmer', 0],[20, 'Dimmer', 50],[21, 'Dimmer', 50],[10, 'Dimmer', 0],[11, 'Dimmer', 0]],
    #     6: ["+ red", 10, [1, 'Dimmer', 0],[2, 'Dimmer', 0],[20, 'Dimmer', 50],[21, 'Dimmer', 50],[10, 'Dimmer', 0],[11, 'Dimmer', 50]]
    # },
    # "bar_l":{
    #     "options": {"warp_at_end": True},
    #     0: ["off", 1, [20, 'Dimmer', 0]],
    #     1: ["off", 1, [20, 'Dimmer', 100]]
    # },
    # "bar_r":{
    #     "options": {"warp_at_end": True},
    #     0: ["off", 1, [21, 'Dimmer', 0]],
    #     1: ["off", 1, [21, 'Dimmer', 100]]
    # },
    # "led":{
    #     "options": {"warp_at_end": True},
    #     0: ["off", 1, [10, 'Dimmer', 0]],
    #     1: ["off", 1, [10, 'Dimmer', 100]]
    # },
    #"pub":{
    #"options": {"warp_at_end": True},
    #0: ["Pub On", 10, [10, 'Dimmer', 50],[19, 'Dimmer', 50],[7, 'Dimmer', 50]],
    #1: ["Pub On", 1, [10, 'Dimmer', 100],[19, 'Dimmer', 100],[7, 'Dimmer', 100]],
    #2: ["Pub On", 0, [10, 'Dimmer', 50],[19, 'Dimmer', 50],[7, 'Dimmer', 50]],
    #3: ["Pub Off", 5, [10, 'Dimmer', 0],[19, 'Dimmer', 0],[7, 'Dimmer', 0]]
    #}
}

key_mapping = {
    #key_num: ["type", "Text", direkt]
    #type = "pad", "command"
    "17": ["pad", "7", "7", True],
    "1": ["pad", "8", "8", True],
    # "2": ["pad", "9", "9", True],
    "3": ["pad", "4", "4", True],
    "4": ["pad", "5", "5", True],
    "5": ["pad", "6", "6", True],
    "6": ["pad", "1", "1", True],
    "7": ["pad", "2", "2", True],
    "8": ["pad", "3", "3", True],
    "9": ["pad", "*", "*", True],
    "10": ["pad", "0", "0", True],
    "11": ["pad", "Return", "Enter", False],
    "12": ["pad", "r", "cr", True],
    "13": ["pad", "g", "cg", True],
    "14": ["pad", "b", "cb", True],
    "15": ["pad", "w", "c(255,255,255)", True],
    "16": ["pad", "/", "/", True],
    "0": ["cuelist", "papa_spot", "go"],
    "2": ["command", "unset_pub"]
    # "2": ["command", "change_led"],
    # "0": ["cuelist", "pub", "go"],
    # "0": ["cuelist", "bar_l", "go"],
    # "1": ["cuelist", "led", "go"],
    # "2": ["cuelist", "bar_r", "go"]
}

fader_mapping = {
    "0": "back",
    "1": "grund",
    "2": "pub"
}

# fader_mapping = {
#     "0": "R",
#     "1": "L",
#     "2": "master"
# }

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
