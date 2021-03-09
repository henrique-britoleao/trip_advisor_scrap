import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

from numpy.random import randint

import gensim.downloader as api
wv = api.load('glove-wiki-gigaword-300')

count = 0 
def print_every_five(function):
    '''Returns a function that prints the number of times it has been exectuted.'''
    def inner(sentence):
        global count
        count += 1
        if count % 5 ==0:
            print(f'Executed: {count}')
    
        return function(sentence)
    return inner

@print_every_five
def parse_sentence(sentence):
    '''Returns a sentence with augmented vocabulary.'''
    # lowercase transformer
    low_sent = sentence.lower()
    # tokenize
    tokens = low_sent.split()
    
    for i in range(0, len(tokens), 2): # replaces every 2 words
        tokens[i] = find_synonym(tokens[i])

    return " ".join(tokens)

def find_synonym(word):
    if word not in stopwords.words('english'): # does not augment stopwords
        try:
            return wv.most_similar(word)[randint(0,3)][0] # takes randomly one of 
                                                          #three most similar words
        except:
            return word
    else:
        return word