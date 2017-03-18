#David Campion - 11/03/2017

from elasticsearch import Elasticsearch


#variables
es_host = "localhost:9200"
es_index="news_index"
doctype = "article"
min_term_frenq = 2
max_query_term = 70
include = "false"
field_to_be_checked = "content"

#set connection
es = Elasticsearch(es_host)

#-------------
#-------------
#check if similar document alredy exist
#return a tuple ("has_similar","docID"), where has_similar is a boolean and docID a string

def es_search_doc_similar_to_text(text,es_field,es_min_term_freq,es_max_query_terms,minimal_score):

    #example:
    #   es_search_doc_similar_to_text("text_to_look_for_similar", "field_name_to_compare", 1, 70,50)

    #text: text string to search. Must be string.
    #es_field: field to compare in the index. Must be string. Example: "content"
    #es_min_term_freq: min term frequency for the search. Example: 1
    #es_max_query_terms: max query term. Example : 70
    #minial_score: if a score above this value exist, return True.

    #note: above 90 should be identical document. above 50 should be similar
    # so setting 'minimal_score' to 90 should retrieve the doc ID of the exact document


    has_similar = False
    most_similar_ID = ""
    similarity_score = ""

    #query
    query='{"query": {"more_like_this" : {"fields" : ["'+ es_field + '"],"like" : "' + text + '","min_term_freq" : ' + str(es_min_term_freq) + ',"max_query_terms" : ' + str(es_max_query_terms) + '}}}'

    #request elastic
    res = es.search(index=es_index, body=query)

    if res['hits']['max_score'] > minimal_score:
        has_similar = True
        most_similar_ID = res['hits']['hits']['_id']
        similarity_score = res['hits']['max_score']

    return has_similar, most_similar_ID, similarity_score

#-------------
#-------------
#Retrieve a specific document based on ID
def es_search_doc_by_ID(docID):

    # set query
    query= '{"query": { "match": { "_id": "'+ docID + '" } }}'

    #request elastic
    res = es.search(index=es_index, body=query)

    if res['hits']['total'] = 1:
        result = res['hits']['hits']['_source']
    else:
        result = []

    return result

#-------------
#-------------
#update a field of a specific docID
def es_update_field(docID, field, value):

    # set query
    query = '{"doc" : {"'+ field + '": ' + value + '}}'

    #request elastic
    res = es.update(index=es_index, doc_type=doctype, id=docID, body=query)

    return res

#-------------
#-------------
#Retrieve a specific document based on ID
def es_retrieve_fieldvalue(docID, field):

    # set query
    query= '{"query": { "match": { "_id": "'+ docID + '" } }}'

    #request elastic
    res = es.search(index=es_index, body=query)

    if res['hits']['total'] = 1:
        result = res['hits']['hits']['_source']["'" + field + "'"]
    else:
        result = ""

    return result
