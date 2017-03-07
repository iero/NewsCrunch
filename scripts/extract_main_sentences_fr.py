#David Campion - 2017/03/04
#require the following ressources:
# - java (last verison)
# - the full stanford tagger version (http://nlp.stanford.edu/software/stanford-postagger-full-2014-08-27.zip)

#extract the stanford tagger and change the path to the model and the jar file in the variables below

import nltk.data
import os
import re #import the regular expressions library; will be used to strip punctuation

import nltk
from nltk.corpus import stopwords #import stopwords from nltk corpus
from nltk.stem.snowball import FrenchStemmer #import the French stemming library
from nltk.tokenize import TreebankWordTokenizer #import the Treebank tokenizer
from nltk.probability import FreqDist #to calculate frenquency
from nltk.tag.stanford import StanfordPOSTagger #import the stanford pos tagger

#variables
#change the path regarding your installation of the stanford pos tagger
path_stanford_model='/tmp/newscruncher/POSTAGGER/stanford-postagger-full-2014-08-27/models/french.tagger'
path_stanford_tagger_jar='/tmp/newscruncher/POSTAGGER/stanford-postagger-full-2014-08-27/stanford-postagger.jar' 

#retrieve stanford pos tagger for french
st = StanfordPOSTagger(path_stanford_model,path_stanford_tagger_jar)

#create stopword list
stopwords_base = ""
stopwords_fr = stopwords.words('french')
punctuation = ['.',',',':',';','?','!','"',"'",'$','%','(',')','«','»','’', '`','``', "''",'-', '_', '&']
useless_words = ['les','a','tout','toute','toutes','tous','plus','moins','très','encore','autre', 'comme', 'autres',
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
verbes_ternes = ['être', 'etre', 'est', 'sont','fut','êtes',
                 'faut', 'falloir', 'font','fait', 'faire', 'faites',
                 'avoir','à','avez',
                 'devoir', 'doit','doivent','devrait', 'devraient','devez',
                 'permet', 'permettre', 
                 'voir', 'vu','voyez',
                 'savoir','sait','su','savez',
                 'pouvoir', 'peut', 'peuvent', 'pouvez',
                'aller', 'va', 'vont', 'allez']
determinants = ['je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles']
months = ['janvier', 'février', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout',
         'septembre', 'octobre', 'novembre', 'décembre', 'decembre']
date = ['jour', 'jours', 'minutes', 'minute', 'seconde', 'secondes', 'mois', 'année', 'années', 'an', 'ans', 'nuit', 'temps']
measures = ['mm', 'cm', 'km', 'm']
stopwords_fr += punctuation + useless_words + verbes_ternes + determinants + months + date + measures

#create french grammar It's a Regex
grammar_french = r"""
    NBAR:
        {<N.*|ADJ|P>*<N.*>} # nouns and adjectives, terminated with nouns
            
    NP:
        {<NBAR>}
        {<NBAR><P><NBAR>} # above, connected with dans, de, sur, etc.
"""

# chargement du tokenizer
tokenizer = nltk.data.load('tokenizers/punkt/PY3/french.pickle')

#------------------------
#------------------------
#function to build the word tree of the document
def leaves(tree):
    """find NP (npun) leaf nodes in chunck tree"""
    for subtree in tree.subtrees(filter = lambda t: t.label()=='NP'):
        yield subtree.leaves()
        
def normalise(word):
    #define lemmatizer and stemmer
    lemmatizer=nltk.WordNetLemmatizer()
    stemmer=nltk.stem.porter.PorterStemmer()
    
    """normlaisde in lowcase and stem them"""
    word = word.lower()
    #word = stemmer.stem(word)
    word = lemmatizer.lemmatize(word)
    return word

def acceptable_word(word):
    """check conditions for acceptable words"""
    accepted = bool(2 <= len(word) <=15 and word.lower() not in stopwords_base)
    return accepted

def get_terms(tree):
    for leaf in leaves(tree):
        term = [normalise(w) for w,t in leaf if acceptable_word(normalise(w))]
        yield term
        
#----------------------------
#----------------------------
#correct the punctuation in the texrt
def replacepunct(text):
    text = text.replace('.',  ' . ')
    text = text.replace(",",  " , ")
    text = text.replace("(",  " ( ")
    text = text.replace(")",  " ) ")
    text = text.replace("'",  " ' ")
    text = text.replace("’",  " ’ ")
    text = text.replace("?",  " ? ")
    text = text.replace("!",  " ! ")
    text = text.replace(":",  " : ")    
    return text

#----------------------------
#----------------------------
#extract most frequent words from text, with a minimum frequency and provide them in a list
def text_fdist(text, min_occurence):
    from nltk.probability import FreqDist
    from nltk.tokenize import TreebankWordTokenizer

    tokenizer = TreebankWordTokenizer()

    #tokenise words:
    tokens = tokenizer.tokenize(text)
    #remove stopwords
    tokens = [token.lower() for token in tokens if token.lower() not in stopwords_fr]

    fdist_in = FreqDist(tokens)
    
    #filter words with more than one occurence
    fdist = list(filter(lambda x: x[1]>=min_occurence,fdist_in.items()))
    return fdist

#-------------------------------
#-------------------------------
#check existence of a word in a text
def check_word_existence(word,text):
    from nltk.tokenize import TreebankWordTokenizer

    tokenizer = TreebankWordTokenizer()

    #tokenise text:
    tokens = tokenizer.tokenize(text)
    
    #check presence:
    check = False
    for i in range (0,len(tokens)):
        if word == tokens[i]:
                check = True
                
    return check

#---------------------------
#---------------------------
#extract main sentences
def extract_sentences_fr(text, min_word_frequency):
      
    #correct punctuation
    text = replacepunct(text)
    
    # create the chunker to retrieve sentences regarding specified grammar
    chunker = nltk.RegexpParser(grammar_french)
    
    #tag tokens (i.e. define nouns, verbs, etc.)
    tokens = tokenizer.tokenize(text)

    postokens = st.tag(tokens)
    
    #build a tree based on tagged tokens:
    tree = chunker.parse(postokens)
    
    #extract all sentences from the text as a list, tuples.
    main_sentences = list(get_terms(tree))
    
    #combines words from tuples into a single phrase
    sentences = [""]*len(main_sentences)

    for i in range (0,len(main_sentences)):
        for j in range (0,len(main_sentences[i])):
            if j == 0:
                sentences[i] += main_sentences[i][j]
            else:
                sentences[i] += " " + main_sentences[i][j]

    #calculate frequence of words in the whole text
    mostcommon = text_fdist(text,min_word_frequency)
    
    final_sentences=['']*len(sentences)
    
    #extract the sentences containing more frequent words
    for i in range (0,len(sentences)):
        check = False
        for j in range (0,len(mostcommon)):
            if check_word_existence(mostcommon[j][0],sentences[i]):
                check = True
        if check == True:
            final_sentences[i]=sentences[i]
    
    #filter to remove empty list
    final_sentences=filter(None,final_sentences)
    
    #remove duplicates
    final_sentences = list(set(final_sentences))
    
    return final_sentences

#---------------------------
#---------------------------
#extract main sentences
def extract_words_fr(text, min_word_frequency):
    
    #correct punctuation
    text = replacepunct(text)
    
    #calculate frequence of words in the whole text
    mostcommon = text_fdist(text,min_word_frequency)
    
    final_words=['']*len(mostcommon)
    
    #extract the words
    for i in range (0,len(mostcommon)):
            final_words[i]=mostcommon[i][0]  
    
    return final_words