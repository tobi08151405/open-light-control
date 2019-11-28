serial_enable = True

rows = 4
cols = 3
faders = 3
encoders = 1

universe_num = 4

uni_map = dict(zip(range(universe_num), range(universe_num)))
uni_map_ = {v: k for k, v in uni_map.items()}

typ_to_func = {}
typ_to_addr = {}
#nr_to_typ = {6: 'Mac 250 Krypton'}
nr_to_typ = {}
nr_to_addr = {}
nr_in_use={}

curr_page=0
fader_map = [[],[],[]]
for i in range(faders):
    fader_map[0].append(0)
    fader_map[1].append(0)
    fader_map[2].append(0)
