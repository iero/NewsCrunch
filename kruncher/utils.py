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
