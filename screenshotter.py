import pyscreenshot as ImageGrab
import time
import requests
import operator
import numpy as np
import keys
import getpass
from azure.storage.blob import ContentSettings
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
import computer_vision as cv

if __name__ == '__main__':

    im = ImageGrab.grab(bbox=(0, 0, 1440, 200))  # X1,Y1,X2,Y2
    im.save("curr_screen.png")
    username = getpass.getuser()
    block_blob_service = BlockBlobService(account_name=keys.blob_acct_name, account_key=keys.blob_key)
    block_blob_service.create_container('sscontainer', public_access=PublicAccess.Container)
    block_blob_service.create_blob_from_path(
        'sscontainer',
        username,
        'curr_screen.png',
        content_settings=ContentSettings(content_type='image/png')
                )
    response  = cv.analyzeImages(keys.blob_endpoint+"/"+username)


