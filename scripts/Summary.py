import sumy
#from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
#from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


def summary(PATH,LANGUAGE,SENTENCES_COUNT):
    parser = PlaintextParser.from_file(PATH, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    resume = ""
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        resume += str(sentence)
    return resume
