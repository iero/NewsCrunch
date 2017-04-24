import json

import xml.etree.ElementTree as ET

def loadxml(params_file) :
    tree = ET.parse(params_file)
    return tree.getroot()

def loadjson(feed_json_file) :
    with open(feed_json_file) as json_file:
        return json.load(json_file)

def printjsonTitles(json_data) :
    for news in json_data :
        for t in json_data[news] :
            print(t['title'])

def sanitizeText(text) :
	filtered_words=["adsbygoogle","toto"]
	if any(x in text for x in filtered_words):
		return ""
	else :
		return text.replace(r'\r','')

# detect
# type name="value"
#    section attribute
# ie : div class="toto"
#        a href=""
def extractImageFromPage(soup,type,name,value,section,attribute) :
    out_img=""
    if (name == "class") :
        img_sec=soup.find(type, class_=value)
        #print(img_sec)
    if img_sec is not None and img_sec.find(section) is not None :
        out_img=img_sec.find(section).get(attribute)
    return out_img

def extractTextFromPage(soup,type,name,value,section) :
    out_text=""
    if (name == "class") :
        text_sec=soup.find(type, class_=value)
    if text_sec is not None :
        for t in text_sec.find_all(section):
            out_text=out_text+sanitizeText(t.get_text())
    return out_text

def extractFormatedTextFromPage(soup,type,name,value,section) :
    out_text=""
    if (name == "class") :
        text_sec=soup.find(type, class_=value)

    if text_sec is not None :
        for t in text_sec.find_all(section):
            sText=sanitizeText(t.get_text())
            if sText :
                out_text=out_text+"<p>"+sText+"</p>"
    return out_text

def extractTagsFromPage(soup,type,name,section,value) :
    out_tags=[]
    #print(soup)
    if (name == "class") :
        #print(type)
        #print(value)
        tags_sec=soup.find(type, class_=value)
        #print(tags_sec)
    if tags_sec is not None and tags_sec.find_all(section) is not None :
        for t in tags_sec.find_all(section):
            tag = t.get_text().lower()
            tag = tag.replace("-","")
            tag = tag.replace(" ","")
            tag = tag.replace("...","")
            print(tag)
            if tag : out_tags.append(tag)
    return out_tags

def findArticlefromText(json_data,text) :
    for news in json_data :
    	for t in json_data[news] :
            if text in t['text'] :
                return t['title']
