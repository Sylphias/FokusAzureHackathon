import pyscreenshot as ImageGrab
import datetime
import time
import json
import keys
import getpass
from azure.storage.blob import ContentSettings
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
import computer_vision as cv
def uploadToBlob(container,filename,object_type="image", blobname="", username="", timestamp="" ):
    block_blob_service = BlockBlobService(account_name=keys.blob_acct_name, account_key=keys.blob_key)
    block_blob_service.create_container(container, public_access=PublicAccess.Container)
    if object_type == "image":
        block_blob_service.create_blob_from_path(
            container,
            blobname,
            filename,
            content_settings=ContentSettings(content_type= 'image/png')
                    )
    elif object_type == "text":
        block_blob_service.create_blob_from_text(
            container,
            blobname,
            filename
                )
if __name__ == '__main__':
    im = ImageGrab.grab(bbox=(0, 0, 1440, 200))  # X1,Y1,X2,Y2
    im.save("curr_screen.png")
    username = getpass.getuser()
    uploadToBlob('sscontainer','curr_screen.png',blobname=username)
    response  = cv.analyzeImages(keys.blob_endpoint+"/"+username)

    timestamp = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S'))
    uploadToBlob('ocrcontainer',json.dumps(response),object_type='text',blobname=username+timestamp+'.txt')




