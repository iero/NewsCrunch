import os
import urllib.request as request

from PIL import Image
from urllib.parse import urlparse
from os.path import splitext, basename

def tootImg(m,text,url) :
    disassembled = urlparse(url)
    img_name, img_ext = splitext(basename(disassembled.path))
    img_local = ("/tmp/"+img_name+img_ext)
    try :
        request.urlretrieve(url, img_local)

        if "png" not in img_ext :
            img = Image.open(img_local)
            img_local = ("/tmp/"+img_name+".png")
            img.save("/tmp/"+img_name+".png",'png')
            os.remove("/tmp/"+img_name+img_ext)

        media_id = m.media_post(img_local)
        #print(media_id)

        m.status_post(text,in_reply_to_id=None,media_ids=[media_id])
        if os.path.exists(img_local) : os.remove(img_local)
    except :
        m.toot(text)
