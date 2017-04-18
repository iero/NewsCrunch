# -*-coding:utf-8 -*

import os
import socket
import re
import time
import json

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

import kruncher.utils as utils
import elastic.similarity_greg as similarity

# Utils
current_milli_time = lambda: int(round(time.time() * 1000))

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

# Debug

debug = False
doTweet = True
# debug on local
print("Running on "+socket.gethostname())
if "digital-gf.local" in socket.gethostname() :
	print("Local testing...")
	debug = True
	doTweet = False

# Tweet sizes = add 1 for extra space
tweet_size = 140
tweet_link_size = 1+23

# Load Services Settings
root = utils.loadxml("settings.xml")
# Load security settings
auth_root = utils.loadxml("auth.xml")

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

# Create JSON feed
feed_json_file=root.find('settings').find('feed_json_file').text
json_data = utils.loadjson(feed_json_file)

# Keep last hundred messages
if debug : print("+ JSON size : "+str(len(json_data)))
while len(json_data) > 100 :
	m = min(json_data)
	if debug : print("Removed "+m)
	del json_data[m]

# create dictionnary for similarity
token_dict = []
for news in json_data :
	for t in json_data[news] :
		token_dict.append(t['title'])

if debug : print("+ JSON size : "+str(len(json_data)))

# Create RSS feed
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
	service_name = service.get('name')
	rss_url = service.find('url').text
	rss_twitter = ""
	if service.find('twitter_mention') is not None :
		rss_twitter = service.find('twitter_mention').text

	rss_parsed = urlparse(rss_url)
	rss_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=rss_parsed)

	rss_lang = service.get('lang')
	rss_dir = '{uri.netloc}'.format(uri=rss_parsed)
	rss_dir = out_directory + '/' + rss_lang +'/'+ rss_dir
	print("+ RSS : "+service_name)

	if not os.path.exists(rss_dir):
		print("+- New feed "+rss_dir+" created")
		os.makedirs(rss_dir)
		doTweet = False

	feed = feedparser.parse(rss_url)

	for post in feed.entries:

		filtered_post = False

		# Grab service tags
		post_tags= []
		if service.find('hashtags') is not None :
			for t in service.find('hashtags').findall("tag") :
				post_tags.append(t.text)

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
			#if debug : print("+-> " + web_page.url)
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

			# Remove ad post..
			if service.find('filters') is not None :
				for filter in service.find('filters').findall("filter") :
					filter_type = filter.get('type')
					filter_value = filter.text
					#print("test "+filter_value+" in "+post_title.lower())
					# based on title
					if filter_type == "title" and filter_value in post_title.lower() :
						print("+--x Title filter matched on "+filter_value)
						filtered_post = True
					# based on content
					if filter_type == "class" :
						filter_name = filter.get('name')
						filter_section = filter.get('section')
						#print(filter_name)
						f=soup.find(filter_section, class_=filter_name)
						if f is not None and filter_value in f.get_text().lower() :
							print("+--x Content filter matched on "+filter_value)
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

			# Grab tags
			if service.find('tags') is not None :
				tags_type = service.find('tags').get('type')
				tags_section = service.find('tags').get('section')
				tags_value = service.find('tags').text
				tags_sec=soup.find(tags_type, class_=tags_value)
				if tags_sec is not None and tags_sec.find_all(tags_section) is not None :
					for t in tags_sec.find_all(tags_section):
						tag = t.get_text().lower()
						if " " not in tag : post_tags.append(tag)
					if post_tags and debug :
						print("+--> Tags : "+str(post_tags))
					# Replace words by tags in title
					tweet_size_allowed = tweet_size - tweet_link_size
					for t in post_tags :
						if t in post_title and len(post_title)+len(t) < tweet_size_allowed :
							post_title = re.sub(t,"#"+t,post_title)

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
				if debug : print("+--> Image : "+ out_img)

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

			if not filtered_post :
				# Test similarity
				token_dict.append(post_title)
				sim_results = similarity.find_similar(token_dict)
				print(sim_results)
				sim_grade=float("{0:.2f}".format(sim_results[0][1]))
				if sim_results[0][1] == 0 : sim_desc=""
				else : sim_desc = sim_results[0][2]
				#print("%.2f".format(sim_results[0][1]))

				# Twitter
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

				# Add tags if possible
				for t in post_tags :
					if t not in post_title and len(post_title)+len(t)+2 <= tweet_size_allowed :
						tweet_text = tweet_text+" #"+t

				# Add source if possible
				if (len(tweet_text) + len(rss_twitter) < tweet_size_allowed) :
						tweet_text = tweet_text+" "+rss_twitter

				# Add Image & push tweet
				if out_img and not out_img.startswith("data:"):
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

				# Remove oldest message from json :
				if len(json_data) >= 100 :
					m = min(json_data)
					if debug : print("Removed "+m)
					del json_data[m]

				# Add to json
				post_id = str(current_milli_time())
				json_data[post_id] = []
				json_data[post_id].append({
					'service': service_name,
					'title': post_title,
					'date' : post.updated,
					'lang' : rss_lang,
    				'source': post.link,
					'image': out_img,
					'tags' : post_tags,
					'similarity' : sim_grade,
					'similarity_with' : sim_desc,
					'text' : out_text
				})

			print(" "+entry+" created")

#Write json
with open(feed_json_file, 'w') as jsonfile:
    #json.dump(json_data, jsonfile, sort_keys=True)
    json.dump(json_data, jsonfile)

#Write associated RSS feed
#for p in data['people']:
for news in json_data :
	for t in json_data[news] :
		fe = fg.add_entry()
		fe.id(news)
		fe.title(t['title'])
		fe.author(name=t['service'])
		#fe.updated(t['date'])
		fe.link(href=t['source'])

		if t['image'] is not None :
			out_text="<img src=\""+t['image']+"\"/><p>"+t['text']+"</p>"
		else :
			out_text="<p>"+t['text']+"</p>"
		fe.content(src=out_text, type="raw")
fg.atom_file(feed_atom_file) # Write the RSS feed to a file
