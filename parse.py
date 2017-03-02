#!/usr/bin/python

import os
import urllib2
from urlparse import urlparse

import feedparser
from bs4 import BeautifulSoup

import xml.etree.ElementTree as ET

#--
params_file="settings.xml"
out_directory = "output"

if not os.path.exists(out_directory):
    os.makedirs(out_directory)

if not os.path.exists(out_directory+'/fr'):
    os.makedirs(out_directory+'/fr')

if not os.path.exists(out_directory+'/en'):
    os.makedirs(out_directory+'/en')

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
	#rss_domain= service.find('domain').text

	print("+ RSS : "+rss_name)
	if not os.path.exists(rss_dir):
		print "+- "+rss_dir+" created"
    		os.makedirs(rss_dir)

	#if hasattr(ssl, '_create_unverified_context'):
    	#	ssl._create_default_https_context = ssl._create_unverified_context
	feed = feedparser.parse(rss_url)

	print("+- "+ feed['feed']['title'] + " with "+ str(len(feed['entries'])) + " entries downloaded")
	#print "	Changes : "+ feed['feed']['updated'] 

	for post in feed.entries:
		
		#print "+-- " + post.title
		#print "+--- " + post.updated
		#print "+--- " + post.link 
		
		entry_parsed = urlparse(post.link)
		entry_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=entry_parsed)

		entry = post.link.replace(entry_domain,"").replace('/','-').strip("-")
		entry = entry+".txt"

		if not os.path.isfile(rss_dir+'/'+entry):
			web_page = urllib2.urlopen(post.link)
			soup = BeautifulSoup(web_page, "html.parser")
			
			out_text=""
			if ("The Verge" in rss_name) :
				for t in soup.find("div", class_="c-entry-content").find_all('p'):
					out_text=out_text+t.get_text()
			elif ("Presse Citron" in rss_name) :
				for t in soup.find("div", class_="post-content description").find_all('p'):
					out_text=out_text+t.get_text()
			elif ("Journal du Net" in rss_name) :
				for t in soup.find("div", class_="entry").find_all('p'):
					out_text=out_text+t.get_text()
			elif ("Siecle Digital" in rss_name) :
				for t in soup.find("div", class_="post-content description").find_all('p'):
					out_text=out_text+t.get_text()
			elif ("MacGeneration" in rss_name) :
				for t in soup.find("div", class_="field-item even").find_all('p'):
					out_text=out_text+t.get_text()
		
				
			
			# sanitize
			out_text=out_text.replace(r'\r','')

			file = open(rss_dir+'/'+entry, 'w+')
			file.write(out_text.encode('utf-8'))
			file.close()
			print(" "+entry+" created")
