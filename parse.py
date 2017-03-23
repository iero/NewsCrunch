import os
import socket
import re

import urllib3
import requests
import feedparser
import urllib.request

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from feedgen.feed import FeedGenerator
from datetime import datetime

import xml.etree.ElementTree as ET

from TwitterAPI import TwitterAPI
from pyshorteners import Shortener

#import elastic.export_to_es as es

def parseURLName(url) :
	entry_parsed = urlparse(post.link)
	entry_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=entry_parsed)
	entry = post.link.replace(entry_domain,"").replace('/','-').strip("-")
	entry = entry+".txt"
	return entry

def sanitizeText(text) :
	filtered_words=["adsbygoogle","toto"]
	if any(x in text for x in filtered_words):
		return ""
	else :
		return text

#--
debug = False
doTweet = True

# debug on local
if "digital-gf.local" in socket.gethostname() :
	print("Local testing...")
	debug= True
	doTweet=False

# Tweet sizes = add 1 for extra space
tweet_size = 140
tweet_link_size = 1+23

# Load Services Settings
params_file="settings.xml"
tree = ET.parse(params_file)
root = tree.getroot()
# Load security settings
auth_file="auth.xml"
auth_tree = ET.parse(auth_file)
auth_root = auth_tree.getroot()

print(datetime.now())

for service in auth_root.findall('service') :
    if service.get("name") == "bitly" :
        shortener = Shortener('Bitly', bitly_token=service.find("token").text)
    elif service.get("name") == "twitter" :
        twitterapi = TwitterAPI(consumer_key=service.find("consumer_key").text, consumer_secret=service.find("consumer_secret").text, access_token_key=service.find("access_token_key").text, access_token_secret=service.find("access_token_secret").text)

headers = {'User-Agent': root.find('settings').find('User-Agent').text}
out_directory = root.find('settings').find('output').text

# Create directory structure
if not os.path.exists(out_directory): os.makedirs(out_directory)
if not os.path.exists(out_directory+'/fr'): os.makedirs(out_directory+'/fr')
if not os.path.exists(out_directory+'/en'): os.makedirs(out_directory+'/en')

# Create RSS feed if needed
feed_atom_file=root.find('settings').find('feed_atom_file').text
feed_url=root.find('settings').find('feed_url').text

fg = FeedGenerator()
fg.id(feed_url) #TODO : mettre numero unique
fg.title('Veille Digitale')
fg.subtitle('Veille Digitale par G. Fabre, Digital Advisor for Total E&P¨')
fg.author( {'name':'Greg Fabre','email':'nomail@iero.org'} )
#fg.logo('http://ex.com/logo.jpg')
fg.link( href=feed_url, rel='self' )
fg.language('fr')

atomfeed = fg.atom_str(pretty=True) # Get the ATOM feed as string
fg.atom_file(feed_atom_file) # Write the ATOM feed to a file

# Parse rss services and apply
for service in root.findall('service'):
	rss_name = service.get('name')
	rss_url = service.find('url').text
	rss_twitter = ""
	if service.find('twitter_mention') is not None :
		rss_twitter = service.find('twitter_mention').text

	rss_parsed = urlparse(rss_url)
	rss_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=rss_parsed)

	rss_lang = service.get('lang')
	rss_dir = '{uri.netloc}'.format(uri=rss_parsed)
	rss_dir = out_directory + '/' + rss_lang +'/'+ rss_dir

	print("+ RSS : "+rss_name)

	if not os.path.exists(rss_dir):
		print("+- New feed "+rss_dir+" created")
		os.makedirs(rss_dir)
		doTweet = False

	feed = feedparser.parse(rss_url)

	for post in feed.entries:

		# Get pages from selected category
		filtered_post = False
		#if service.find('selection') is not None :
		#	filtered_post = True
		#	for sel in service.find('selection').findall("select") :
		#		sel_type = sel.get('type')
		#		sel_value = sel.text
		#		if (sel_type == "url") and (sel_value in post.link) :
		#			filtered_post = False

		link = post.link.rsplit('?', 1)[0]
		link = link.rsplit('#', 1)[0]
		entry=parseURLName(link)

		# Continue if new page and test redirection
		if not filtered_post and not os.path.isfile(rss_dir+'/'+entry):
			if debug : print("+-> " + link)
			if debug : print("+--> " + rss_dir+'/'+entry)

			# Sanitize page url and get redirection target if needed
			web_page = requests.get(link, headers=headers, allow_redirects=True)
			if web_page.history:
				link = web_page.url.rsplit('?', 1)[0]
				if debug : print("+--> " + link)
				web_page = requests.get(link, headers=headers)

			# Parse page
			if debug : print("+-> " + web_page.url)
			soup = BeautifulSoup(web_page.content, "html.parser")

			# Get pages from selected category
			if service.find('selection') is not None :
				filtered_post = True
				for sel in service.find('selection').findall("select") :
					sel_type = sel.get('type')
					sel_value = sel.get('value')
					sel_filter = sel.text
					if (sel_type == "url") and (sel_value in web_page.url) :
						filtered_post = False
					elif (sel_type == "div") :
						sel_section = sel.get('section')
						text_sec=soup.find(sel_type, class_=sel_value)
						#print(text_sec)
						if text_sec is not None :
							for t in text_sec.find_all(sel_section):
								if sel_filter in t :
									filtered_post = False
									if debug : print("+--> page allowed : "+sel_filter)

			# Sanitize title
			post_title = post.title
			if service.find('sanitize') is not None :
				for removedField in service.find('sanitize').findall("remove") :
					if removedField.get('type') == "title" :
						post_title = re.sub(removedField.text,'',post_title)
						#post_title = post_title.replace(removedField.text,"")

			# Remove ad post.. based on title
			if service.find('filters') is not None :
				for filter in service.find('filters').findall("filter") :
					filter_type = filter.get('type')
					filter_value = filter.text
					#print("test "+filter_value+" in "+post_title.lower())
					if filter_type == "title" and filter_value in post_title.lower() :
						print("Title filter matched on "+filter_value)
						filtered_post = True

			# Grab text
			rss_text_type = service.find('text').get('type')
			rss_text_name = service.find('text').get('name')
			rss_text_value = service.find('text').text
			rss_text_section = service.find('text').get('section')
			out_text=""
			text_sec=soup.find(rss_text_type, class_=rss_text_value)
			if text_sec is not None :
				for t in text_sec.find_all(rss_text_section):
					out_text=out_text+sanitizeText(t.get_text())

			# sanitize
			out_text=out_text.replace(r'\r','')

			file = open(rss_dir+'/'+entry, 'wb')
			file.write(out_text.encode('utf-8'))
			file.close()

			# Grab main image
			rss_img_type = service.find('image').get('type')
			rss_img_name = service.find('image').get('name')
			rss_img_value = service.find('image').text
			rss_img_section = service.find('image').get('section')
			rss_img_attribute = service.find('image').get('attribute')

			out_img=""
			img_sec=soup.find(rss_img_type, class_=rss_img_value)
			#print(img_sec)
			if img_sec is not None and img_sec.find(rss_img_section) is not None :
				out_img=img_sec.find(rss_img_section).get(rss_img_attribute)
				if debug : print(out_img)

				#for element in img_sec.findAll(rss_img_section):
				#	out_img=element.get(rss_img_attribute)
				#	if debug : print(out_img)

			#print(news_process.summary(out_text,35))
			#Filters title ?
			if service.find('filters') is not None :
				for filter in service.find('filters').findall("filter") :
					filter_type = filter.get('type')
					filter_value = filter.text
					filter_result = soup.find(filter_type, class_=filter_value)
					if filter_result is not None :
						print("Content filter matched on "+filter_value)
						filtered_post = True

			# Twitter
			if not filtered_post :
				tweet_text = post_title
				tweet_size_allowed = tweet_size - tweet_link_size

				# Shorten text if needed
				if (len(tweet_text) >= (tweet_size_allowed) ) :
					tweet_text = tweet_text[:tweet_size_allowed-1]
				# Add link
				try :
					bitly_article_url = shortener.short(web_page.url)
					tweet_text = tweet_text+" "+bitly_article_url
				except :
					tweet_text = tweet_text+" "+web_page.url

				# Add source if possible
				if (len(tweet_text) + len(rss_twitter) < tweet_size_allowed) :
						tweet_text = tweet_text+" "+rss_twitter
				# Add tags

				# Add Image & push tweet
				if out_img :
					if debug : print("+---> Image : " + out_img)
					if out_img.startswith("//") :
						out_img = "https:"+out_img
					elif out_img.startswith("/") :
						parsed_web_page = urlparse(web_page.url)
						dom =  '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_web_page)
						out_img = dom+out_img
					#print(out_img)
					try :
						response = requests.get(out_img, headers=headers, allow_redirects=True)
						data = response.content
						if doTweet : r = twitterapi.request('statuses/update_with_media', {'status':tweet_text}, {'media[]':data})
						if debug : print("tweet+picture : "+tweet_text)
					except :
						if doTweet : r = twitterapi.request('statuses/update', {'status':tweet_text})
						if debug : print("tweet (problem with pic): "+tweet_text)
				else :
					if doTweet : r = twitterapi.request('statuses/update', {'status':tweet_text})
					if debug : print("tweet : "+tweet_text)

				# Add to index
				#es.export_to_es_from_text(out_text,rss_name,post_title)

				# Add to rss
				if out_img is not None or not out_img:
					out_text="<img src=\""+out_img+"\"/><p>"+out_text+"</p>"
				fe = fg.add_entry()
				fe.id(entry)
				fe.title(post_title)
				fe.author(name=rss_name)
				#fe.updated(post.updated)
				fe.link(href=post.link)
				fe.content(src=out_text, type="raw")
				#fe.summary(src=out_text, type="raw")
				#fg.rss_file(feed_rss_file) # Write the RSS feed to a file
				fg.atom_file(feed_atom_file) # Write the RSS feed to a file


			print(" "+entry+" created")
