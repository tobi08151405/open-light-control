import json

from GlobalVar import nr_to_typ, nr_to_addr, typ_to_func, typ_to_addr

generic_num = 100
generic_name = 'Desk Channel 8 bit'
led_start=110
led_num = 6
led_name = 'TaO LED 8 bit'
#led_span = typ_to_func[led_name]['ChannelSpan']
led_span = 10

def create():
    for num in range(generic_num):
        nr_to_typ[num+1] = generic_name
        nr_to_addr[num+1] = [0, num]
    
    nr_to_typ[100] = 'Michi LED 8 bit'
    nr_to_addr[100] = [0, 99]
    
    for num in range(led_num):
        nr_to_typ[led_start+num+1] = led_name
        nr_to_addr[led_start+num+1] = [0, led_start+num*led_span]
    
    #with open("typ_to_addr.json") as file1:
        #for k, v in json.load(file1).items():
            #typ_to_addr[k] = v
    #with open("typ_to_func.json") as file2:
        #for k, v in json.load(file2).items():
            #typ_to_func[k] = v