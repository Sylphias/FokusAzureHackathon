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
import ddist

queueTimestamps =[]
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

def getJustText(jsonText):
    dictified = json.loads(jsonText)
    reformedString = ""
    for key,value in dictified.iteritems():
        reformedString += ' '.join(x+" " for x in value)
    return reformedString

def retrieveFromBlob(container,blobname):
    block_blob_service = BlockBlobService(account_name=keys.blob_acct_name, account_key=keys.blob_key)
    block_blob_service.create_container(container, public_access=PublicAccess.Container)
    block_blob_service.get_blob_to_path(container, blobname, blobname)

def getListOfBlobs(container):
    block_blob_service = BlockBlobService(account_name=keys.blob_acct_name, account_key=keys.blob_key)
    block_blob_service.create_container(container, public_access=PublicAccess.Container)
    return block_blob_service.list_blobs(container)

class Screenshotter:
    def __init__(self):
        queueTimestamps = []
    def start(self):
        self.run = True
        p = Process(target=self.sansfin, args=(1000,))
        p.start()
        p.join()

    def stop(self):
        self.run = False
    def run_script(self):
        im = ImageGrab.grab(bbox=(0, 0, 1440, 500))  # X1,Y1,X2,Y2
        im.save("curr_screen.png")
        username = getpass.getuser()
        uploadToBlob('sscontainer', 'curr_screen.png', blobname=username)
        response = cv.analyzeImages(keys.blob_endpoint + "/" + username)
        timestamp = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S'))
        self.queueTimestamps.append(timestamp)
        textJson = json.dumps(response)
        uploadToBlob('ocrcontainer', textJson, object_type='text', blobname=username + timestamp + '.txt')
        blobs = getListOfBlobs('ocrcontainer')
        retrieveFromBlob('ocrcontainer', username + self.queueTimestamps[0] + '.txt')
        model = open(username + self.queueTimestamps[0] + '.txt', "r")
        current_data = getJustText(textJson)
        model_data = getJustText(model.read())
        ddist.similarity_score(model_data, current_data)

# if __name__ == '__main__':
while(True):
    time.sleep(5)
    im = ImageGrab.grab(bbox=(0, 0, 1440, 900),childprocess= True,backend='mac_screencapture')  # X1,Y1,X2,Y2
    im.save("curr_screen.png")
    username = getpass.getuser()
    uploadToBlob('sscontainer', 'curr_screen.png', blobname=username)
    response = cv.analyzeImages(keys.blob_endpoint + "/" + username)
    timestamp = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S'))
    queueTimestamps.append(timestamp)
    textJson = json.dumps(response)
    uploadToBlob('ocrcontainer', textJson, object_type='text', blobname=username + timestamp + '.txt')
    blobs = getListOfBlobs('ocrcontainer')
    retrieveFromBlob('ocrcontainer', username + queueTimestamps[0] + '.txt')
    model = open(username + queueTimestamps[0] + '.txt', "r")
    current_data = getJustText(textJson)
    model_data = getJustText(model.read())
    ddist.similarity_score(model_data, current_data)





