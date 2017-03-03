import os
import urllib3
import requests
import feedparser

from bs4 import BeautifulSoup
from urllib.parse import urlparse

import xml.etree.ElementTree as ET

def parseURLName(url) :
	entry_parsed = urlparse(post.link)
	entry_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=entry_parsed)
	entry = post.link.replace(entry_domain,"").replace('/','-').strip("-")
	entry = entry+".txt"
	return entry
#--

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
params_file="settings.xml"
out_directory = "output"

if not os.path.exists(out_directory):
    os.makedirs(out_directory)

if not os.path.exists(out_directory+'/fr'):
    os.makedirs(out_directory+'/fr')

if not os.path.exists(out_directory+'/en'):
    os.makedirs(out_directory+'/en')

http = urllib3.PoolManager()

tree = ET.parse(params_file)
root = tree.getroot()

# Parse rss services and apply
for service in root.findall('service'):
	rss_name = service.get('name')
	rss_url = service.find('url').text

	rss_parsed = urlparse(rss_url)
	rss_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=rss_parsed)

	rss_lang = service.find('lang').text
	rss_dir = '{uri.netloc}'.format(uri=rss_parsed)
	rss_dir = out_directory + '/' + rss_lang +'/'+ rss_dir
	rss_class= service.find('class').text

	print("+ RSS : "+rss_name)
	if not os.path.exists(rss_dir):
		print("+- "+rss_dir+" created")
		os.makedirs(rss_dir)

	feed = feedparser.parse(rss_url)

	#print("+- "+ feed['feed']['title'] + " with "+ len(feed['entries']) + " entries downloaded")
	#print "	Changes : "+ feed['feed']['updated'] 

	for post in feed.entries:
		#print "+-- " + post.title
		#print "+--- " + post.updated
		print("+--- " + post.link) 
	
		entry=parseURLName(post.link)	


		if not os.path.isfile(rss_dir+'/'+entry):
			web_page = requests.get(post.link, headers=headers, allow_redirects=True)
			if web_page.history:
				link = web_page.url.rsplit('?', 1)[0]
				print("+--- Redirection to :" + link)
				web_page = requests.get(link, headers=headers)
				print(web_page.content)
				file = open(rss_dir+'/'+entry+".raw", 'wb')
				file.write(web_page.content.encode('utf-8'))
				file.close()
				
			soup = BeautifulSoup(web_page.content, "html.parser")
			out_text=""
			for t in soup.find("div", class_=rss_class).find_all('p'):
				out_text=out_text+t.get_text()
				
			# sanitize
			out_text=out_text.replace(r'\r','')

			file = open(rss_dir+'/'+entry, 'wb')
			file.write(out_text.encode('utf-8'))
			file.close()
			print(" "+entry+" created")
