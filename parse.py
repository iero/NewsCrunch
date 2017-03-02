#!/usr/bin/python

import os
import urllib3
from urlparse import urlparse

import feedparser
from bs4 import BeautifulSoup

import xml.etree.ElementTree as ET

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
#--

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

	#if hasattr(ssl, '_create_unverified_context'):
    	#	ssl._create_default_https_context = ssl._create_unverified_context
	feed = feedparser.parse(rss_url)

	print("+- "+ feed['feed']['title'] + " with "+ str(len(feed['entries'])) + " entries downloaded")
	#print "	Changes : "+ feed['feed']['updated'] 

	for post in feed.entries:
		
		#print "+-- " + post.title
		#print "+--- " + post.updated
		print("+--- " + post.link) 
		
		entry_parsed = urlparse(post.link)
		entry_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=entry_parsed)

		entry = post.link.replace(entry_domain,"").replace('/','-').strip("-")
		entry = entry+".txt"

		if not os.path.isfile(rss_dir+'/'+entry):
			web_page = http.request('GET', post.link)
			soup = BeautifulSoup(web_page.data, "html.parser")
			
			out_text=""
			for t in soup.find("div", class_=rss_class).find_all('p'):
				out_text=out_text+t.get_text()
				
			
			# sanitize
			out_text=out_text.replace(r'\r','')

			file = open(rss_dir+'/'+entry, 'w+')
			file.write(out_text.encode('utf-8'))
			file.close()
			print(" "+entry+" created")
