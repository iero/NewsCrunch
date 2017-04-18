#017/03/23 David Campion

#usage:
# import this library in your code:
#       import similarity

# create a empty dictionnary:
#       token_dict = {}

# initiate the dictionnary:
#       similarity.initiate_dict(token_dict)

# add a new text to your dictionnary:
# Older texts (based on the NB_NEWS variable) are removed from it:
#       similarity.add_news_to_dict(token_dict,"this is a new text")

# Display the most similar document for the last added text (in the dictionary)
#       similarity.find_similar(token_dict, similarity.NB_NEWS)

# Display the 3 most similar document for the last added text (in the dictionary)
#       similarity.find_similar(token_dict, similarity.NB_NEWS, 3)


import os
import string

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.stem.porter import PorterStemmer

import nltk
from nltk.corpus import stopwords #import stopwords from nltk corpus
from nltk.stem.snowball import FrenchStemmer #import the French stemming library
from nltk.stem.snowball import EnglishStemmer #import the English stemming library
from nltk.tokenize import TreebankWordTokenizer #import the Treebank tokenizer
from nltk.tokenize import WordPunctTokenizer

#import lib to detect language
import elastic.detect_lang

#number of news in the dictionary
#NB_NEWS = 9

#name stemmers
stemmer_fr=FrenchStemmer()
stemmer_en=EnglishStemmer()

#create stopwords lists
stopwords_base = ""
stopwords_fr = stopwords.words('french')
stopwords_en = stopwords.words('english')

#stopwords common to fr and en
punctuation = ['.',',',':',';','?','!','"',"'",'$','%','(',')','«','»','’', '`','``', "''",'-', '_', '&']
measures = ['mm', 'cm', 'km', 'm']

#specific to fr
useless_words_fr = ['les','a','tout','toute','toutes','tous','plus','moins','très','encore','autre', 'comme', 'autres',
                 'mais','ou','où','et','donc','or','ni','car',
                 'si','aussi','alors','vers','entre','souvent','autour','chaque', 'chacun', 'chacune','quelques','quelqu',
                 'lorsque','enfin','déjà','grâce','dès',
                 'ce', 'cette', 'ci','ça','cela','ces','dont','chez','cet', 'ceux'
                 'aucun', 'aucune','autant',
                 "d’", "n’", "l’", "qu’", "s’",'leur', 'leurs',
                 'sans', 'avec', 'sous', 'sur', 'bon', 'bien','rien','depuis','ainsi','selon','ainsi','souvent','contre',
                 'début', 'fin', 'dernier', 'avant', 'après', 'fois','dernière', 'derniers', 'dernières',
                 'peu', 'beaucoup','grand', 'grands', 'grande', 'grandes', 'petit', 'petite', 'petits', 'petites',
                 'un', 'deux', 'trois','premier', 'première',
                 'hui']
verbes_ternes_fr = ['être', 'etre', 'est', 'sont','fut','êtes',
                 'faut', 'falloir', 'font','fait', 'faire', 'faites',
                 'avoir','à','avez',
                 'devoir', 'doit','doivent','devrait', 'devraient','devez',
                 'permet', 'permettre',
                 'voir', 'vu','voyez',
                 'savoir','sait','su','savez',
                 'pouvoir', 'peut', 'peuvent', 'pouvez',
                'aller', 'va', 'vont', 'allez']
determinants_fr = ['je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles']
months_fr = ['janvier', 'février', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout',
         'septembre', 'octobre', 'novembre', 'décembre', 'decembre']
date_fr = ['jour', 'jours', 'minutes', 'minute', 'seconde', 'secondes', 'mois', 'année', 'années', 'an', 'ans', 'nuit', 'temps']

#specific to en
useless_words_en = []
verbes_ternes_en = ['be', 'have']
determinants_en = ['i', 'you', 'he', 'she', 'it', 'we', 'their', 'they', 'them', 'its']
months_en = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
         'september', 'october', 'november', 'december']
date_en = ['day', 'days', 'minutes', 'minute', 'second', 'seconds', 'months', 'month', 'year', 'years','night', 'nights', 'time']

#create stopwords variables
stopwords_fr +=  useless_words_fr + verbes_ternes_fr + determinants_fr + months_fr + date_fr
stopwords_en += useless_words_en + verbes_ternes_en + determinants_en + months_en + date_en
stopwords_all = stopwords_en + stopwords_fr + punctuation + measures

#load tokenizer (you can choose the most efficient, however wordpunct is
#working well)

#tokenizer = TreebankWordTokenizer()
tokenizer = WordPunctTokenizer()

#FUNCTIONS
#-------
#-------
# stemer function text
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

#------
#------
#tokenize a  text depending on its language
def tokenize(text):
    #check language
    language = elastic.detect_lang.get_language(text)
    if language == 'french':
        #tokenize text
        tokens = tokenizer.tokenize(text)
        tokens = [token for token in tokens if token.lower() not in stopwords_fr + punctuation]
        #stem text
        stems = stem_tokens(tokens, stemmer_fr)
        #uncomment to print tokens and stem words
        #print("tokens: ", tokens)
    elif language == 'english':
        #tokenize text
        tokens = tokenizer.tokenize(text)
        tokens = [token for token in tokens if token.lower() not in stopwords_en + punctuation]
        #stem text
        stems = stem_tokens(tokens, stemmer_en)
        #uncomment to print tokens and stem words
        #print("tokens: ", tokens)
    else:
        #tokenize text
        tokens = tokenizer.tokenize(text)
        tokens = [token for token in tokens if token.lower() not in stopwords_en]
        #stem text
        stems = stem_tokens(tokens, stemmer_en)
        #uncomment to print tokens and stem words
        #print("tokens: ", tokens)

    #print("stems: ", stems)
    return stems

#------
#clean text: remove punctuation and get lower characters
def clean_text(text):
    lowers = text.lower()
    #code to remove punctuation. uncomment if required
    #table = {ord(char): None for char in string.punctuation}
    #cleaned = lowers.translate(table)
    cleaned = lowers
    return cleaned

#find similar doc for the last news. Parameters:
# - token_dict: a dictionnary of tokens,
# -  top_n = n most similar documents to retrieve

def get_similarity(token_dict, top_n = 1) :
        if len(token_dict) == 1 : return [0,1,token_dict[0]]

        # Reverse list to put the seed in first position
        reverse_dict=[]
        for n in range(0,len(token_dict)) :
            reverse_dict.append(token_dict[len(token_dict)-n-1])

        index = len(token_dict)-1

        tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=stopwords_all)
        tfidf_matrix = tfidf.fit_transform(reverse_dict)
        cosine_similarities = linear_kernel(tfidf_matrix[0:1], tfidf_matrix).flatten()
        related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != 0]

        return cosine_similarities[0]

def find_similar(token_dict, top_n = 1): #tfidf_matrix,

    # Only one item
    if len(token_dict) == 1 : return [0,1,token_dict[0]]

    # Reverse list to put the seed in first position
    reverse_dict=[]
    for n in range(0,len(token_dict)) :
        #print("Swap {} with {}".format(n,len(token_dict)-n-1))
        reverse_dict.append(token_dict[len(token_dict)-n-1])

    index = len(token_dict)-1

    # print("Looking for [{}] in : ".format(reverse_dict[0]))
    # i=0
    # for token in reverse_dict :
    #     #print("  {} : {}".format(token, token_dict[token]))
    #     print("  {} : {}".format(i,token))
    #     i=i+1

    # print(index)
    #create model
    # -  tfidf_matrix: the tfid matrix of documents

    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=stopwords_all)
    #tfidf_matrix = tfidf.fit_transform(token_dict.values())
    tfidf_matrix = tfidf.fit_transform(reverse_dict)

    #uncomment below to view tfidf of other features
    #print(tfidf_matrix)
    # response = tfidf.transform([list(token_dict.values())[index]])
    #response = tfidf.transform([list(token_dict.values())[index]])
    # print(response)
    # feature_names = tfidf.get_feature_names()
    # for col in response.nonzero()[1]:
    #     print(feature_names[col], ' - ', response[0, col])
    #
    #print("Calcul similarities")
    #print(tfidf_matrix[index:index+1])

    #define similarities
    #cosine_similarities = linear_kernel(tfidf_matrix[index:index+1], tfidf_matrix).flatten()
    # La matrice etait dans la ligne au dessus inversée ;)
    cosine_similarities = linear_kernel(tfidf_matrix[0:1], tfidf_matrix).flatten()
    #print(cosine_similarities)

    #related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != index]
    #du coup, il fallait viré l'index 0, pas le dernier (relicat de mon code)
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != 0]
    #print(related_docs_indices)

    #return top_n similar documents in the matrix. For each of them:
    # - index of the document in the matrix
    # - score of similarity
    # - text of the similar document.
    return [(index, cosine_similarities[index],reverse_dict[index]) for index in related_docs_indices][0:top_n]
