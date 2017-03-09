import elasticsearch
import requests, json, codecs
from datetime import datetime
import os
import Summary
import detect_lang
import extract_main_sentences_fr


es_host = "localhost:9200"
es_index = "news_index"
TYPE="articles"

#---------------------------
#---------------------------
#Export to ElasticSearch
def export_to_es(directory, source, title):
                        
    es = elasticsearch.Elasticsearch(hosts=es_host)
    INDEX_NAME = es_index
    
    text = open(directory + '/' + title,'r')
    textstring = text.read()
                        
    #get the content
    content = textstring
    
    #detect language
    language = detect_lang.get_language(textstring)
    
    #count number of words
    from nltk.tokenize import TreebankWordTokenizer
    tokenizer = TreebankWordTokenizer()
    nb_of_words = 1+len(tokenizer.tokenize(textstring))/100

    if language == 'french':
        text_summary = Summary.summary(directory + '/' + title,language,3)
        mainsentences = extract_main_sentences_fr.extract_sentences_fr(textstring,nb_of_words)
        mainwords = extract_main_sentences_fr.extract_words_fr(textstring,nb_of_words)
    else:
        text_summary = ""
        mainsentences = ""
        mainwords = ""                          
            
    
    datepublish = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    body = {"title" : title,
            "content" : content,
            "abstract" : text_summary,
            "authors" : None,
            "url" : None,
            "site": source,
            "mainsentences" : mainsentences,
            "mainwords" : mainwords,
            "cluster": None,
            "language": language,
            "published": datepublish,
            "is_tagged": None}

            
    print(datepublish)
                      #"published": "1483225200000",
    
    es.index(index=INDEX_NAME, doc_type='article', body=body)
    

#-----------------
#-----------------
#walk to upload files
topdir = "/tmp/newscruncher/fr"

def walk_path(path):
    for root, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            for root2, dirnames2, filenames2 in os.walk(os.path.join(root, dirname)):
                for name in filenames2:
                    if name != '.DS_Store':
                        directory = os.path.join(root, dirname)
                        source = dirname
                        title  = name
                        print(title)
                        export_to_es(directory, source, title)
    return print('Done')