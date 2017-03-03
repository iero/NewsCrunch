# import & logging preliminaries
import logging
import itertools

import re
import gensim
import nltk

from nltk.corpus import stopwords

from gensim.summarization import summarize
from nltk.probability import FreqDist

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO

stopwords_en = stopwords.words('english')

#-------------------------------------
#use to build the tree of sentences:

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
    accepted = bool(2 <= len(word) <=15 and word.lower() not in stopwords_en)
    return accepted

def get_terms(tree):
    for leaf in leaves(tree):
        term = [normalise(w) for w,t in leaf if acceptable_word(w)]
        yield term
        
#-----------------------
#simple summary function
def summary(text,nb_words):
    from gensim.summarization import summarize
    #conversion in utf8
    textsummary = summarize(textstring, word_count=nb_words, split=False)
    return textsummary
    
#-----------------------
#extract main sentences
def extract_sentences(text, nb_keywords):
    
    import nltk
    from nltk.corpus import stopwords
    from nltk.probability import FreqDist

    #grammar to be use to recognize stemmed sentences.m It's a Regex
    grammar = r"""
        NBAR:
            {<NN.*|JJ>*<NN.*>} # nouns and adjectives, terminated with nouns
            
        NP:
            {<NBAR>}
            {<NBAR><IN><NBAR>} # above, connected with in, of, etc.
    """
    
    # create the chunker to retrieve sentences regarding specified grammar
    chunker = nltk.RegexpParser(grammar)
    
    #extract tokens
    tokens = nltk.word_tokenize(text)
    #tag tokens (i.e. define nouns, verbs, etc.)
    postokens = nltk.tag.pos_tag(tokens)
    
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

    #calculate frequence of sentences
    fdist = FreqDist(sentences)
    
    #select more frequent words in all sentences
    mostcommon = fdist.most_common(nb_keywords)
    
    final_sentences=['']*len(sentences)
    
    #extract the sentences containing more frequent words
    for i in range (0,len(sentences)):
        check = False
        for j in range (0,len(mostcommon)):
            #print mostcommon[j][0]
            #print sentences[i]
            if mostcommon[j][0] in sentences[i]:
                check = True
        if check == True:
            final_sentences[i]=sentences[i]
    
    #filter to remove empty list
    final_sentences=filter(None,final_sentences)
    
    #remove duplicates
    final_sentences = list(set(final_sentences))
    
    return final_sentences
    
