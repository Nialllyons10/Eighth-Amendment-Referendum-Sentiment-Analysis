from nltk.corpus import wordnet as wordnet
from nltk.corpus import sentiwordnet as swn
import nltk
import math

from nltk.tag.perceptron import PerceptronTagger
tagger = PerceptronTagger()


def loadDictionary():
    '''Using Positive and Negative Opinion Lexicons added from: 
      https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html'''
    d= dict()

    wpos = open('lexicon/words_positive','r').readlines()
    for i in range(len(wpos)):
        a = wpos[i].replace("\n","")
        d[a]=[1,0]

    wneg = open('lexicon/words_negative','r').readlines()
    for i in range(len(wneg)):
        a = wneg[i].replace("\n","")
        d[a]=[-1,0]

    wafinn = open('lexicon/AFINN-111.txt','r').readlines()
    for i in range(len(wafinn)):
        ln = wafinn[i].replace("\n","").split("\t")
        sc = float(ln[1])/5.0
        d[ln[0]]= [sc,0]

    imp_words = open('lexicon/important_words','r').readlines()
    for i in range(len(imp_words)):
        ln = imp_words[i].replace("\n","").split("\t")
        d[ln[0]]= [0,1]

    politic_sent = open('lexicon/politic_sent_words','r').readlines()
    for i in range(len(politic_sent)):
        ln = politic_sent[i].replace("\n","").split("\t")
        sc = float(ln[-1])
        d[ln[0]]= [sc,0]

    wgael = open('lexicon/senti-focloir.txt','r').readlines()
    for i in range(len(wgael)):
        ln = wgael[i].replace("\n","").split("\t")
        sc = float(ln[1])/5.0
        d[ln[0]]= [sc,0]

    return d

d=loadDictionary()



def getListScore(word,diction):
    word = word.lower()
    return [0,0] if (word not in diction) else diction[word]



def wordnet_pos_code(tag):
    '''Translation from nltk tags to Wordnet code'''
    if tag.startswith('NN'):
        return wordnet.NOUN
    elif tag.startswith('VB'):
        return wordnet.VERB
    elif tag.startswith('JJ'):
        return wordnet.ADJ
    elif tag.startswith('RB'):
        return wordnet.ADV
    else:
        return ''



def pos_tag(sentence):
    '''POS tagging of a sentence.'''
    tagged_words = []
    tokens = nltk.word_tokenize(sentence)
    #tag_tuples = nltk.pos_tag(tokens)
    tag_tuples = nltk.tag._pos_tag(tokens, None, tagger)
    for (string, tag) in tag_tuples:
        token = {'word':string, 'pos':tag}            
        tagged_words.append(token)    
    return tagged_words

def word_sense_cdf(word, context, wn_pos):
    '''Word sense disambiguation in terms of matching words frequency 
    between the context each sense's definition. Adapted from
    www.slideshare.net/faigg/tutotial-of-sentiment-analysis'''
    senses = wordnet.synsets(word, wn_pos)
    if len(senses) > 0:
        cfd = nltk.ConditionalFreqDist((sense, def_word)
                       for sense in senses
                       for def_word in sense.definition().split()
                       if def_word in context)
        best_sense = senses[0]
        for sense in senses:
            try:
                if cfd[sense].max() > cfd[best_sense].max():
                    best_sense = sense
            except: 
                pass                
        return best_sense
    else:
        return None

def word_sense_similarity(word, context, dummy = None):
    '''Another word sense disambiguation technique.
    Adapted from: pythonhosted.org/sentiment_classifier'''
    wordsynsets = wordnet.synsets(word)
    bestScore = 0.0
    result = None
    for synset in wordsynsets:
        for w in nltk.word_tokenize(context):
            score = 0.0
            for wsynset in wordnet.synsets(w):
                sim = wordnet.path_similarity(wsynset, synset)
                if(sim == None):
                    continue
                else:
                    score += sim
            if (score > bestScore):
                bestScore = score
                result = synset
    return result


def score_ngram(ngram, text, wsd = word_sense_cdf):
    sc=0.0
    imp=0.0
    ngram.append({'word': 'NULL', 'pos': 'NULL'})#in case it is an unigram
    bigram=ngram[0]["word"]+" "+ngram[1]["word"]
    unigram=ngram[0]["word"]
    #is bigram in our dictionary
    if (sum(getListScore(bigram,d)) != 0):
        [sc,imp] = getListScore(bigram,d) 
    #is word in our dictionary
    elif (sum(getListScore(unigram,d)) != 0):
        [sc,imp] = getListScore(unigram,d) 
    else:
        if 'punct' not in ngram[0] :
            sense = wsd(ngram[0]['word'], text, wordnet_pos_code(ngram[0]['pos']))
            if sense is not None:
                sent = swn.senti_synset(sense.name())
                if sent is not None:
                    pos=float(sent.pos_score() or 0)
                    neg=float(sent.neg_score() or 0)
                    if (pos>neg):
                        sc=pos
                    elif (pos<neg):
                        sc=-neg
    return [sc,imp]




def sentence_score(text, threshold = 0.75, wsd = word_sense_cdf):
    '''Classifies a phrase according to sentiment analysis based
    on WordNet and SentiWordNet. It also computes a thresholded 
    score by ignoring strongly objective words.'''
    tagged_words = pos_tag(text)
    count=0
    acumsum = 0.0
    imp_acumsum = 1.0
    sc=0.0
    imp=0.0
    imp_weight=5
    for i in range(1,len(tagged_words)+1):
        mngr=tagged_words[i-1:i+1]
        [sc,imp]=score_ngram(mngr,text,wsd)
        acumsum=acumsum+sc
        imp_acumsum=imp_acumsum+imp
    return acumsum*imp_acumsum


def sentTweetWords_final_score(text):
    sentences = nltk.sent_tokenize(text)
    score = 0.0
    for sentence in sentences:
        score = sentence_score(sentence)
    return 1 / (1 + math.exp(-score))
