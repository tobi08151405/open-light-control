serial_enable = False

output_freeze = [False]

rows = 4
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

curr_page=0
fader_map = [[],[],[]]
for i in range(faders):
    fader_map[0].append(0)
    fader_map[1].append(0)
    fader_map[2].append(0)

key_mapping = {
    #key_num: ["Text", direkt]
    "0": ["7", True],
    "1": ["8", True],
    "2": ["9", True],
    "3": ["4", True],
    "4": ["5", True],
    "5": ["6", True],
    "6": ["1", True],
    "7": ["2", True],
    "8": ["3", True],
    "9": ["*", True],
    "10": ["0", True],
    "11": ["Return", False],
    "12": ["c", True]
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
