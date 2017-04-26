# Initial David Campion - 03/2017
# Adapted version Greg Fabre - 04/2017

import os
import string
import re
from unidecode import unidecode

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.stem.porter import PorterStemmer

import nltk
from nltk.corpus import stopwords #import stopwords from nltk corpus
from nltk.stem.snowball import FrenchStemmer #import the French stemming library
from nltk.stem.snowball import EnglishStemmer #import the English stemming library
from nltk.tokenize import TreebankWordTokenizer #import the Treebank tokenizer
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import TreebankWordTokenizer

from nltk.probability import FreqDist

#import lib to detect language
import elastic.detect_lang
import elastic.common as common

#name stemmers
stemmer_fr=FrenchStemmer()
stemmer_en=EnglishStemmer()

# Load tokenizer
# You can choose the most efficient, however wordpunct is working well
#tokenizer = TreebankWordTokenizer()
tokenizer = WordPunctTokenizer()

# stemer function text
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

#tokenize a text depending on its language
def tokenizeText(text,lang):
    tokens = tokenizer.tokenize(text)
    t = [token for token in tokens if token.lower() not in common.getStopWords(lang) + common.punctuation]
    return t

def stemTokens(t,lang) :
    if lang == "french" :
        return stem_tokens(t, stemmer_fr)
    elif lang == "english" :
        return stem_tokens(t, stemmer_en)
    else :
        return stem_tokens(t, stemmer_en)

def tokenize(text) :
    language = elastic.detect_lang.get_language(text)

    tokens = tokenizer.tokenize(text)
    t = [token for token in tokens if token.lower() not in common.getStopWords(language) + common.punctuation]

    if language == "french" :
        return stem_tokens(t, stemmer_fr)
    elif language == "english" :
        return stem_tokens(t, stemmer_en)
    else :
        return stem_tokens(t, stemmer_en)

#------
#clean text: remove punctuation and get lower characters
def clean_text(text):
    lowers = text.lower()
    #code to remove punctuation. uncomment if required
    #table = {ord(char): None for char in string.punctuation}
    #cleaned = lowers.translate(table)
    cleaned = lowers
    return cleaned

def find_similar(token_dict, top_n = 1): #tfidf_matrix,

    # Only one item
    if len(token_dict) == 1 : return [0,1,token_dict[0]]

    # Reverse list to put the seed in first position
    reverse_dict=[]
    for n in range(0,len(token_dict)) :
        #print("Swap {} with {}".format(n,len(token_dict)-n-1))
        reverse_dict.append(token_dict[len(token_dict)-n-1])

    index = len(token_dict)-1

    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=common.getStopWords("all"))
    #tfidf_matrix = tfidf.fit_transform(token_dict.values())
    tfidf_matrix = tfidf.fit_transform(reverse_dict)

    cosine_similarities = linear_kernel(tfidf_matrix[0:1], tfidf_matrix).flatten()

    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != 0]

    #return top_n similar documents in the matrix. For each of them:
    # - index of the document in the matrix
    # - score of similarity
    # - text of the similar document.
    return [(index, cosine_similarities[index],reverse_dict[index]) for index in related_docs_indices][0:top_n]

def findTags(text,nbTags):
    language = elastic.detect_lang.get_language(text)
    tokens = tokenizeText(text,language)

    fdist_in = FreqDist(tokens)

    # Min 3 occurences
    min_occurence=3
    fdist = fdist_in.most_common(nbTags)
    out=[]
    for x in fdist :
        pattern = re.compile('[\W_]+', re.UNICODE)
        word = pattern.sub('', x[0])
        word = unidecode(word).lower()
        if word : out.append(word)

    return out
