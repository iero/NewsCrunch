# -*-coding:utf-8 -*

from __future__ import unicode_literals

import os
import socket
import re
import time
import json
import pytz

import urllib3
import requests
import feedparser
import urllib.request

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from feedgen.feed import FeedGenerator
from datetime import datetime
from pytz import timezone

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

# Tweet sizes = add 1 for extra space
tweet_size = 140
tweet_link_size = 1+23

# Load Services & security Settings
general_settings = utils.loadxml("settings.xml")
auth_settings = utils.loadxml("auth.xml")

print(datetime.now())

for service in auth_settings.findall('service') :
	if service.get("name") == "bitly" :
		shortener = Shortener('Bitly', bitly_token=service.find("token").text)
	elif service.get("name") == "twitter" :
		consumer_key=service.find("consumer_key").text
		consumer_secret=service.find("consumer_secret").text
		access_token_key=service.find("access_token_key").text
		access_token_secret=service.find("access_token_secret").text

headers = {'User-Agent': general_settings.find('settings').find('User-Agent').text}

# debug on local
print("Running on "+socket.gethostname())
if "digital-gf.local" in socket.gethostname() :
	print("Local testing...")
	debug = True
	doTweet = False
	out_directory = general_settings.find('settings').find('localoutput').text
else :
	debug = False
	doTweet = True
	out_directory = general_settings.find('settings').find('output').text

# Create directory structure
if not os.path.exists(out_directory): os.makedirs(out_directory)
if not os.path.exists(out_directory+'/fr'): os.makedirs(out_directory+'/fr')
if not os.path.exists(out_directory+'/en'): os.makedirs(out_directory+'/en')

# Create JSON feed
feed_json_file=general_settings.find('settings').find('feed_json_file').text
json_data = utils.loadjson(feed_json_file)

# Keep last X messages for process and for RSS
nbmax_news=float(general_settings.find('settings').find('max_news').text)
nbmax_rss_news=float(general_settings.find('settings').find('max_news_rss').text)

#if debug : print("+ JSON size : "+str(len(json_data)))
while len(json_data) > nbmax_news :
	m = min(json_data)
	if debug : print("Removed "+m)
	del json_data[m]

# create dictionnaries for similarity
title_dict = []
text_dict = []
for news in json_data :
	for t in json_data[news] :
		title_dict.append(t['title'])
		if (t['tags']) :
			text_dict.append(t['tags'])

if debug : print("+ JSON size : "+str(len(json_data))+" on "+str(nbmax_news))

# Create RSS feed
feed_atom_file=general_settings.find('settings').find('feed_atom_file').text
feed_url=general_settings.find('settings').find('feed_url').text

# Parse rss services and apply
for service in general_settings.findall('service'):
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
	if debug : print("+[RSS "+rss_lang+"] "+service_name)

	if not os.path.exists(rss_dir):
		print("+[New feed] "+rss_dir+" created")
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
			if debug : print("+-[New entry]")

			# Sanitize page url and get redirection target if needed
			web_page = requests.get(link, headers=headers, allow_redirects=True)
			if web_page.history:
				link = web_page.url.rsplit('?', 1)[0]
				if debug : print("+-[Redir] " + link)
				web_page = requests.get(link, headers=headers)
			else :
				if debug : print("+-[Link] " + link)

			if debug : print("+-[Local] " + rss_dir+'/'+entry)

			# Parse page
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
									if debug : print("+-[Page allowed] : "+sel_filter)

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
						print("+-[Title filter] matched on "+filter_value)
						filtered_post = True
					# based on content
					if filter_type == "class" :
						filter_name = filter.get('name')
						filter_section = filter.get('section')
						#print(filter_name)
						f=soup.find(filter_section, class_=filter_name)
						if f is not None and filter_value in f.get_text().lower() :
							print("+-[Content filter] matched on "+filter_value)
							filtered_post = True

			# Grab text
			rss_text_type = service.find('text').get('type')
			rss_text_name = service.find('text').get('name')
			rss_text_value = service.find('text').text
			rss_text_section = service.find('text').get('section')

			out_text= utils.extractTextFromPage(soup,rss_text_type,rss_text_name,rss_text_value,rss_text_section)

			raw_text= utils.extractFormatedTextFromPage(soup,rss_text_type,rss_text_name,rss_text_value,rss_text_section)

			file = open(rss_dir+'/'+entry, 'wb')
			file.write(out_text.encode('utf-8'))
			file.close()

			# Grab tags
			# if service.find('tags') is not None :
			# 	print("Looking for tags")
			# 	tags_type = service.find('tags').get('type')
			# 	tags_name = service.find('tags').get('name')
			# 	tags_section = service.find('tags').get('section')
			# 	tags_value = service.find('tags').text
			# 	post_tags = utils.extractTagsFromPage(soup, tags_type, tags_name, tags_section, tags_value)
			#
			# 	if post_tags and debug : print("+-[Tags] "+str(post_tags))


			# Grab main image
			out_img=""
			if service.find('image') is not None :
				rss_img_type = service.find('image').get('type')
				rss_img_name = service.find('image').get('name')
				rss_img_value = service.find('image').text
				rss_img_section = service.find('image').get('section')
				rss_img_attribute = service.find('image').get('attribute')

				out_img= utils.extractImageFromPage(soup,rss_img_type,rss_img_name,rss_img_value,rss_img_section,rss_img_attribute)
			if not out_img and service.find('image_alt') is not None :
				rss_img_type = service.find('image_alt').get('type')
				rss_img_name = service.find('image_alt').get('name')
				rss_img_value = service.find('image_alt').text
				rss_img_section = service.find('image_alt').get('section')
				rss_img_attribute = service.find('image_alt').get('attribute')

				out_img= utils.extractImageFromPage(soup,rss_img_type,rss_img_name,rss_img_value,rss_img_section,rss_img_attribute)

			#Filters title
			if service.find('filters') is not None :
				for filter in service.find('filters').findall("filter") :
					filter_type = filter.get('type')
					filter_value = filter.text
					filter_result = soup.find(filter_type, class_=filter_value)
					if filter_result is not None :
						print("+-[Content filter] matched on "+filter_value)
						filtered_post = True

			# Test similarity on title
			title_dict.append(post_title)
			sim_results = similarity.find_similar(title_dict)
			#print(sim_results)
			sim_grade=float("{0:.2f}".format(sim_results[0][1]))
			if sim_results[0][1] == 0 : sim_desc=""
			else : sim_desc = sim_results[0][2]
			#print("%.2f".format(sim_results[0][1]))
			if (sim_grade > 0.5) :
				print("+-[Duplicate] with [{}] Score : {}".format(sim_desc.encode('utf-8'),sim_grade))
				filtered_post = True
			else :
				if debug : print("+-[Test Duplicate] with [{}] Score : {}".format(sim_desc.encode('utf-8'),sim_grade))

			# find X most represented keywords
			for t in similarity.findTags(out_text,10) :
				post_tags.append(t)

			# Test similarity on text
			# text_dict.append(out_text)
			# sim_text_results = similarity.find_similar(text_dict)
			# sim_text_grade=float("{0:.2f}".format(sim_text_results[0][1]))
			# sim_text_desc = utils.findArticlefromText(json_data,sim_text_results[0][2])

			# Replace words by tags in title
			# tweet_size_allowed = tweet_size - tweet_link_size
			# for t in post_tags :
			# 	if t in post_title and len(post_title)+len(t) < tweet_size_allowed :
			# 		post_title = re.sub(t,"#"+t,post_title)

			if not filtered_post :
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

				# Add source if possible
				if (len(tweet_text) + len(rss_twitter) < tweet_size_allowed) :
						tweet_text = tweet_text+" "+rss_twitter

				# Add tags if possible
				for t in post_tags :
					if t not in post_title and len(post_title)+len(t)+2 <= tweet_size_allowed :
						tweet_text = tweet_text+" #"+t

				# Add Image & push tweet
				if out_img and not out_img.startswith("data:"):
					if debug : print("+-[img] " + out_img)
					if out_img.startswith("//") :
						out_img = "https:"+out_img
					elif out_img.startswith("/") :
						parsed_web_page = urlparse(web_page.url)
						dom =  '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_web_page)
						out_img = dom+out_img
					#print(out_img)

					twitterapi = TwitterAPI(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)

					try :
						response = requests.get(out_img, headers=headers, allow_redirects=True)
						data = response.content
						if doTweet : r = twitterapi.request('statuses/update_with_media', {'status':tweet_text}, {'media[]':data})
						if debug : print("+-[TweetPic] "+tweet_text)
					except :
						try :
							if doTweet : r = twitterapi.request('statuses/update', {'status':tweet_text})
							if debug : print("+-[TweetNoPicPb] "+tweet_text)
						except :
							if debug : print("+-[TweetPb] "+tweet_text)
				else :
					try :
						if doTweet : r = twitterapi.request('statuses/update', {'status':tweet_text})
						if debug : print("+-[Tweet] "+tweet_text)
					except :
						if debug : print("+-[TweetPb] "+tweet_text)

				# Remove oldest message from json :
				if len(json_data) >= nbmax_news :
					m = min(json_data)
					if debug : print("+-[Removed] "+m)
					del json_data[m]

				# Add to json
				post_id = str(current_milli_time())
				json_data[post_id] = []
				json_data[post_id].append({
					'service': service_name,
					'title': post_title,
					'date' : datetime.now(pytz.timezone('Europe/Paris')).isoformat(),
					'lang' : rss_lang,
    				'source': post.link,
					'image': out_img,
					'tags' : post_tags,
					'similarity' : str(sim_grade),
					'similarity_with' : sim_desc,
					#'similarity_content' : str(sim_text_grade),
					#'similarity_content_with' : sim_text_desc,
					'text' : out_text,
					'text_size' : str(len(out_text.split())),
					'raw' : raw_text
				})

			if debug : print("+-[Tags] "+", ".join(post_tags))
			print("+-[Entry] "+entry)

#Write json
with open(feed_json_file, 'w') as jsonfile:
    #json.dump(json_data, jsonfile, sort_keys=True)
    json.dump(json_data, jsonfile)

#Write associated RSS feed

fg = FeedGenerator()
fg.id(feed_url) #TODO : mettre numero unique
fg.title('Veille Digitale')
fg.subtitle(str(len(json_data))+" articles")
fg.author( {'name':'G. Fabre, Digital Advisor for Total E&P','email':'nomail@iero.org'} )
#fg.logo('http://ex.com/logo.jpg')
fg.link( href=feed_url, rel='self' )
fg.language('fr')

atomfeed = fg.atom_str(pretty=True) # Get the ATOM feed as string
fg.atom_file(feed_atom_file) # Write the ATOM feed to a file

reverse_news=[]
for news in json_data :
	reverse_news.append(news)
reverse_news.sort()
reverse_news.reverse()

#for news in json_data :
n=0
for news in reverse_news :
	for t in json_data[news] :
		if n < nbmax_rss_news :
			fe = fg.add_entry()
			fe.id(news)
			fe.title(t['title'])
			fe.author(name=t['service'])
			fe.published(t['date'])
			fe.updated(t['date'])
			fe.link(href=t['source'])

			if t['image'] is not None :
				try :
					out_text="<img src=\""+t['image']+"\"/>"+t['raw']
				except :
					out_text="<img src=\""+t['image']+"\"/><p>"+t['text']+"</p>"
			else :
				try :
					out_text=t['raw']
				except :
					out_text="<p>"+t['text']+"</p>"

			out_text=out_text+"<p>"+"Tags :" +str(t['tags'])+"</p>"
			out_text=out_text+"<p>"+"Similarity of " +str(t['similarity'])+" with "+t['similarity_with']+"</p>"
			fe.content(content=out_text, type="html")
			n = n+1

fg.atom_file(feed_atom_file) # Write the RSS feed to a file

print(datetime.now())
print("Done")
