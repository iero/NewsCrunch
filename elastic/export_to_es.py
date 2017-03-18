import elasticsearch
import requests, json, codecs
from datetime import datetime
import os
from elastic import Summary
from elastic import detect_lang
from elastic import extract_main_sentences_fr
#from elastic import extract_main_sentences_en


es_host = "localhost:9200"
es_index = "news_index"
TYPE="articles"

#---------------------------
#---------------------------
#Export to ElasticSearch form directory
def export_to_es_from_directory(directory, source, title):

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
        #mainsentences = extract_main_sentences_fr.extract_sentences_fr(textstring,nb_of_words)
        mainsentences = ""
        mainwords = extract_main_sentences_fr.extract_words_fr(textstring,nb_of_words)
    elif language == 'english':
        text_summary = Summary.summary(directory + '/' + title,language,3)
        #mainsentences = extract_main_sentences_en.extract_sentences_en(textstring,nb_of_words)
        mainsentences = ""
        mainwords = extract_main_sentences_en.extract_words_en(textstring,nb_of_words)
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
            "is_tagged_by_ai": "",
            "is_tagged_by_ai": ""}


    print(datepublish)
                      #"published": "1483225200000",

    res=es.index(index=INDEX_NAME, doc_type='article', body=body)

    return res['_id']

#---------------------------
#---------------------------
#Export to ElasticSearch form a text
def export_to_es_from_text(text_of_document, source, title):

    es = elasticsearch.Elasticsearch(hosts=es_host)
    INDEX_NAME = es_index

    textstring = text_of_document

    #get the content
    content = textstring

    #detect language
    language = detect_lang.get_language(textstring)

    #count number of words
    from nltk.tokenize import TreebankWordTokenizer
    tokenizer = TreebankWordTokenizer()
    nb_of_words = 1+len(tokenizer.tokenize(textstring))/100
    print("+-- Nb words : "+str(nb_of_words))

    text_summary = ""
    mainsentences = ""
    mainwords = ""

    if language == 'french':
        text_summary = Summary.summary(textstring,language,3)
        #mainsentences = extract_main_sentences_fr.extract_sentences_fr(textstring,nb_of_words)
        mainsentences = ""
        mainwords = extract_main_sentences_fr.extract_words_fr(textstring,nb_of_words)
    elif language == 'english':
        text_summary = Summary.summary(textstring,language,3)
        #mainsentences = extract_main_sentences_en.extract_sentences_en(textstring,nb_of_words)
        mainsentences = ""
        mainwords = extract_main_sentences_en.extract_words_en(textstring,nb_of_words)

    print("+-- Summary : "+text_summary)
    for m in mainwords : print(m)
    print("+-- Main words : "+', '.join(mainwords))
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
            "is_tagged_by_ai": "",
            "is_tagged_by_ai": ""}


    print(datepublish)
                      #"published": "1483225200000",

    res = es.index(index=INDEX_NAME, doc_type='article', body=body)

    return res['_id']

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
                        task=export_to_es_from_directory(directory, source, title)
                        print(task)
    return print('Done')
