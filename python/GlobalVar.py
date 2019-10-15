serial_enable = False

rows = 4
cols = 3
faders = 3
encoders = 1

universe_num = 4

uni_map = dict(zip(range(universe_num), range(universe_num)))
uni_map_ = {v: k for k, v in uni_map.items()}

typ_to_func = {}
typ_to_addr = {}
nr_to_typ = {6: 'Mac 250 Krypton'}
nr_to_addr = {6: [2, 40]}