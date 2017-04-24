import nltk
from nltk.corpus import stopwords #import stopwords from nltk corpus

#stopwords common to fr and en
punctuation = ['.',',',':',';','?','!','"',"'",'$','%','(',')','«','»','’', '`','``', "''",'-', '_', '&']
measures = ['mm', 'cm', 'km', 'm']

#specific to fr
useless_words_fr = ['les','a','tout','toute','toutes','tous','plus','moins','très','encore','autre', 'comme', 'autres', 'mais','ou','où','et','donc','or','ni','car',
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

def getStopWords(lang) :
    if lang == "french" :
        swords = stopwords.words(lang)
        swords +=  useless_words_fr + verbes_ternes_fr + determinants_fr + months_fr + date_fr
    elif lang == "english" :
        swords = stopwords.words(lang)
        swords += useless_words_en + verbes_ternes_en + determinants_en + months_en + date_en
    else :
        swords = getStopWords("french") + getStopWords("english") + punctuation + measures

    return swords
