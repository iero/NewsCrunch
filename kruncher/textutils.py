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
        
