import os
import urllib3
import requests
import feedparser
import urllib.request

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from feedgen.feed import FeedGenerator

import xml.etree.ElementTree as ET

from TwitterAPI import TwitterAPI
from pyshorteners import Shortener

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

# Load Services Settings
params_file="settings.xml"
tree = ET.parse(params_file)
root = tree.getroot()
# Load security settings
auth_file="auth.xml"
auth_tree = ET.parse(auth_file)
auth_root = auth_tree.getroot()

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

	rss_parsed = urlparse(rss_url)
	rss_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=rss_parsed)

	rss_lang = service.get('lang')
	rss_dir = '{uri.netloc}'.format(uri=rss_parsed)
	rss_dir = out_directory + '/' + rss_lang +'/'+ rss_dir

	print("+ RSS : "+rss_name)
	if not os.path.exists(rss_dir):
		print("+- "+rss_dir+" created")
		os.makedirs(rss_dir)

	feed = feedparser.parse(rss_url)

	for post in feed.entries:

		entry=parseURLName(post.link)

		print("+-> " + post.link)
		print("+--> " + rss_dir+'/'+entry)

		# Continue if new page and test redirection
		if not os.path.isfile(rss_dir+'/'+entry):
			web_page = requests.get(post.link, headers=headers, allow_redirects=True)
			if web_page.history:
				link = web_page.url.rsplit('?', 1)[0]
				print("+--> " + link)
				web_page = requests.get(link, headers=headers)

			# Parse page
			#print("+-> " + web_page.url)
			soup = BeautifulSoup(web_page.content, "html.parser")


			# Grab text
			rss_text_type = service.find('text').get('type')
			rss_text_name = service.find('text').get('name')
			rss_text_value = service.find('text').text
			rss_text_section = service.find('text').get('section')
			out_text=""
			for t in soup.find(rss_text_type, class_=rss_text_value).find_all(rss_text_section):
				out_text=out_text+sanitizeText(t.get_text())

			# sanitize
			out_text=out_text.replace(r'\r','')

			# Grab main image
			rss_img_type = service.find('image').get('type')
			rss_img_name = service.find('image').get('name')
			rss_img_value = service.find('image').text
			rss_img_section = service.find('image').get('section')
			rss_img_attribute = service.find('image').get('attribute')

			out_img=""
			img_sec=soup.find(rss_img_type, class_=rss_img_value)
			if img_sec is not None :
				for element in img_sec.findAll(rss_img_section):
					out_img=element.get(rss_img_attribute)

			file = open(rss_dir+'/'+entry, 'wb')
			file.write(out_text.encode('utf-8'))
			file.close()

			#print(news_process.summary(out_text,35))
			filtered_post = False
			if service.find('filters') :
				for filter in service.find('filters').findall("filter") :
					filter_type = filter.get('type')
					filter_value = filter.text
					#filter_section = filter.get('section')
					#filter_result = soup.find(filter_type, class_=filter_value).find_all(filter_section)
					filter_result = soup.find(filter_type, class_=filter_value)
					if filter_result is not None :
						print("filter matched")
						filtered_post = True

			# Twitter
			if not filtered_post :
				twit_text = post.title
				if (len(twit_text) >= 116 ) :
					twit_text = twit_text[:115]
				try :
					bitly_article_url = shortener.short(web_page.url)
					twit_text = twit_text+" "+bitly_article_url
				except :
					twit_text = twit_text+" "+web_page.url

				if out_img :
					response = urllib.request.urlopen(out_img)
					data = response.read()
					r = twitterapi.request('statuses/update_with_media', {'status':twit_text}, {'media[]':data})
				else :
					r = twitterapi.request('statuses/update', {'status':twit_text})

				# Add to rss
				if out_img is not None :
					out_text="<img src=\""+out_img+"\"/><p>"+out_text+"</p>"
				fe = fg.add_entry()
				fe.id(entry)
				fe.title(post.title)
				fe.author(name=rss_name)
				#fe.updated(post.updated)
				fe.link(href=post.link)
				fe.content(src=out_text, type="raw")
				#fe.summary(src=out_text, type="raw")
				#fg.rss_file(feed_rss_file) # Write the RSS feed to a file
				fg.atom_file(feed_atom_file) # Write the RSS feed to a file


			print(" "+entry+" created")
