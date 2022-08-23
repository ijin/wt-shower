import nfc
import binascii
import time
import requests

clf = nfc.ContactlessFrontend('usb')

def process_IDm():
    global idm
    try:
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        idm = binascii.hexlify(tag.identifier).upper()
        idm = idm.decode()
        print(idm)
        requests.get('http://localhost:5000/ping2')

    except AttributeError:
        print("error")

while True:
    process_IDm()
    time.sleep(3)
