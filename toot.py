import xml.etree.ElementTree as ET

from mastodon import Mastodon

from os.path import splitext, basename
from urllib.parse import urlparse
import urllib.request as request
import urllib

import re

def urlEncodeNonAscii(b):
    #return b.decode('utf-8')
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts=urlparse(iri)
    return urllib.parse.urlunparse([urlEncodeNonAscii(part.encode('u‌​tf-8')) for part in parts])

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


#p = mastodon.timeline(timeline='home', max_id=None, since_id=None, limit=None)
#print(p)
# Create actual instance
#mastodon.toot('Tooting from python!')

#out_img="https://sd-cdn.fr/wp-content/uploads/2017/04/img-5655e-1.jpg"
out_img="http://www.silicon.fr/wp-content/uploads/logos/tweety-©-Ricktop-Fotolia.com_.jpg"
out_img=urlEncodeNonAscii(out_img)
disassembled = urlparse(out_img)
img_name, img_ext = splitext(basename(disassembled.path))
img_local = "/tmp/"+img_name+img_ext
img_local = "/tmp/toot"+img_ext
# pattern = re.compile('[\W_]+', re.UNICODE)
# img_local = pattern.sub('', img_local)
print(img_local)
request.urlretrieve(out_img, img_local)
media_id = mastodon.media_post(img_local)
print(media_id['id'])

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
