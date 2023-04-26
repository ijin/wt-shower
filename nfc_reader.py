import nfc
import binascii
import time
import requests

clf = nfc.ContactlessFrontend('usb')

URL='http://localhost:5000/api/nfc'

def process_IDm():
    global idm
    try:
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        idm = binascii.hexlify(tag.identifier).upper()
        idm = idm.decode()
        print(idm)
        r = requests.get(f"{URL}/{idm}")

    except Exception as e:
        print("error: {}".format(e))

print("Reading NFC tags")
while True:
    process_IDm()
    time.sleep(3)
