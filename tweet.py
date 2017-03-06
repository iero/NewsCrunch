from TwitterAPI import TwitterAPI
from pyshorteners import Shortener
import xml.etree.ElementTree as ET
import urllib.request

# Twitter :
size_url=23
size_img=24

auth_file="auth.xml"
auth_tree = ET.parse(auth_file)
auth_root = auth_tree.getroot()

for service in auth_root.findall('service') :
    if service.get("name") == "bitly" :
        shortener = Shortener('Bitly', bitly_token=service.find("token").text)
    elif service.get("name") == "twitter" :
        twitterapi = TwitterAPI(consumer_key=service.find("consumer_key").text, consumer_secret=service.find("consumer_secret").text, access_token_key=service.find("access_token_key").text, access_token_secret=service.find("access_token_secret").text)

article_url="https://www.sciencesetavenir.fr/high-tech/data/le-mystere-amazon-go-quelles-technologies-pour-le-supermarche-du-futur_110932"

bitly_article_url = shortener.short(article_url)

picture_url = 'https://www.sciencesetavenir.fr/redaction/infographies/JPG/amazon_mieux.jpg'
#bitly_picture_url=shortener.short(picture_url)

text="Technologies d'Amazon Go "+bitly_article_url+" @sciences_avenir "

response = urllib.request.urlopen(picture_url)
data = response.read()
r = twitterapi.request('statuses/update_with_media', {'status':text}, {'media[]':data})
