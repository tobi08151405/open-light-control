from subprocess import getoutput
from time import sleep

def important_print(message):
    print("\n###################################################\n")
    if bool(message):
        print(str(message))
    print("\n###################################################\n")
    
def ask_print(message):
    if bool(message):
        print(str(message))
    input("Press Return when ready")
    

def get_all():
    usb = getoutput('grep "usb " /var/log/syslog')
    u = usb.split('\n')[-2]
    u_num = u.find("usb ")
    num = u[u_num+4:u_num+7]

    dmesg = getoutput('dmesg | grep "usb '+num+'"')
    d = dmesg.split('\n')
    vendor = []
    product = []
    serial = []
    for i in d:
        if "idVendor" in i:
            vendor.append(i[i.find("idVendor")+9:i.find("idVendor")+13])
            product.append(i[i.find("idProduct")+10:i.find("idProduct")+14])
        elif "SerialNumber" in i:
            serial.append(i[i.find("SerialNumber")+14:])
    return 'SUBSYSTEM=="tty", ATTRS{idVendor}=="'+vendor[-1]+'", ATTRS{idProduct}=="'+product[-1]+'", ATTRS{serial}=="'+serial[-1]+'", SYMLINK+="'

important_print("Please remove all Arduinos from your device")
ask_print(None)
ask_print("\nPlease connect the arduino resposible for controling the faders and keys.\n")
sleep(2)
first_line = get_all()+'faderkeys"\n'
#ask_print("\nPlease connect the secound arduino.\n")
#sleep(2)
#secound_line = get_all()+'leds"\n'

try:
    output = open("/etc/udev/rules.d/99-usb-serial-openlight.rules", 'w')
    sudo = True
except PermissionError:
    output = open("99-usb-serial-openlight.rules", 'w')
    sudo = False

output.write(first_line)
#output.write(secound_line)
output.close()

if sudo:
    getoutput("sudo udevadm control --reload-rules")
else:
    important_print("Please move the file '99-usb-serial-openlight.rules' into /etc/udev/rules.d/\nRun the command 'sudo udevadm control --reload-rules' (without quotation marks)\n\nOR rerun this script with root priviliges (sudo)")
