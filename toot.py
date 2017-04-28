import xml.etree.ElementTree as ET

from mastodon import Mastodon

from os.path import splitext, basename
from urllib.parse import urlparse
import urllib.request as request
import urllib

import kruncher.mastodon as kr_mastodon

import re

auth_file="auth.xml"
auth_tree = ET.parse(auth_file)
auth_root = auth_tree.getroot()

for service in auth_root.findall('service') :
    if service.get("name") == "mastodon" :
        mastodon = Mastodon(
            client_id = service.find("client_id").text,
            client_secret = service.find("client_secret").text,
            access_token = service.find("access_token").text,
            api_base_url = "https://mamot.fr")

#out_img="http://www.silicon.fr/wp-content/uploads/logos/tweety-©-Ricktop-Fotolia.com_.jpg"
out_img="https://img.macg.co/2017/4/macgpic-1493334927-221372969596171-sc-jpt.jpg"

kr_mastodon.tootImg(mastodon,"Test image jpg",out_img)

#medid = mastodon.media_post("/Users/greg/Downloads/test.jpg")
#print(medid)

# Register app - only once!
# '''
# Mastodon.create_app(
#      'pytooterapp',
#       to_file = 'pytooter_clientcred.secret'
# )
# '''

# Log in - either every time, or use persisted
# '''
# mastodon = Mastodon(client_id = 'pytooter_clientcred.secret')
# mastodon.log_in(
#     'my_login_email@example.com',
#     'incrediblygoodpassword',
#     to_file = 'pytooter_usercred.secret'
# )
# '''
