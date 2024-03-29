from GlobalVar import nr_to_typ, nr_to_addr, nr_in_use


def create():
    generic_num = 100
    generic_name = 'Desk Channel 8 bit'
    led_start = 110
    led_num = 6
    led_name = 'TaO LED 8 bit'
    #led_span = typ_to_func[led_name]['ChannelSpan']
    led_span = 10

    for num in range(generic_num):
        nr_to_typ[num+1] = generic_name
        nr_to_addr[num+1] = [0, num]
        nr_in_use[num+1] = 0

    #nr_to_typ[100] = 'Michi LED 8 bit'
    #nr_to_addr[100] = [0, 99]
    #nr_in_use[100] = 0

    for num in range(led_num):
        nr_to_typ[led_start+num] = led_name
        nr_to_addr[led_start+num] = [0, led_start+num*led_span-1]
        nr_in_use[led_start+num] = 0

    #with open("typ_to_addr.json") as file1:
        #for k, v in json.load(file1).items():
        #typ_to_addr[k] = v
    #with open("typ_to_func.json") as file2:
        #for k, v in json.load(file2).items():
        #typ_to_func[k] = v


def _create():
    nr_to_typ[100] = 'Sola Wash normal'
    nr_to_addr[100] = [0, 370]
    nr_in_use[100] = 0

    nr_to_typ[200] = 'RGB Fader 8 bit'
    nr_to_addr[200] = [0, 412]
    nr_in_use[200] = 0


def __create():
    generic_name = 'Desk Channel 8 bit'
    for num in range(2):
        nr_to_typ[num+1] = generic_name
        nr_to_addr[num+1] = [0, num]
        nr_in_use[num+1] = 0

    led_name = "Stockwerk LED 8 bit"
    nr_to_typ[10] = led_name
    nr_to_typ[11] = led_name
    nr_to_addr[10] = [0, 32]
    nr_to_addr[11] = [0, 59]
    nr_in_use[10] = 0
    nr_in_use[11] = 0

    led_name = "Stockwerk Bar 8 bit"
    nr_to_typ[20] = led_name
    nr_to_typ[21] = led_name
    nr_to_addr[20] = [0, 16]
    nr_to_addr[21] = [0, 112]
    nr_in_use[20] = 0
    nr_in_use[21] = 0
