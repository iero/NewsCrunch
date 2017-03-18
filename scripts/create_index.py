import elasticsearch
import requests
import json
import time
import nltk
from nltk.corpus import stopwords

es_host = "localhost:9200"
es_index = "news_index"
TYPE="articles"

#---------------------
#---------------------
#create index in Elastic
def create_index(es_host):
    es = elasticsearch.Elasticsearch(hosts=es_host)
    body = {
        "mappings" : {
           "article" : {
                "properties" : {
                    "title" : { "type": "text" },
                    "content" : { "type": "text" },
                    "abstract" : {  "type": "text" },
                    "authors" : { "type": "text" },
                    "url" : { "type": "text" },
                    "site": { "type": "keyword" },
                    "mainsentences" : { "type": "text" },
                    "mainwords" : { "type": "keyword" },
                    "cluster": {  "type": "text" },
                    "has_similar": {  "type": "text" },
                    "language": { "type": "keyword" },
                    "published": { "type": "date",
                                   "format": "yyyy-MM-dd HH:mm:ss"},
                    "is_tagged_by_human": { "type": "text" },
                    "is_tagged_by_ai": { "type": "text" }
                     }
                }
            }
        }
    try:
        es.indices.delete(index=es_index)
    except elasticsearch.NotFoundError as e:
        print("cannot delete index")
        pass
    es.indices.create(index=es_index, body=body)

##------------------
#-------------------
def delete_index(es_host):
    es = elasticsearch.Elasticsearch(hosts=es_host)
    es.indices.delete(index=es_index)
