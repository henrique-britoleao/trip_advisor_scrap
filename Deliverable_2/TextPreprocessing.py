#import libraries 
import pandas as pd 
import numpy as np 
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, PorterStemmer
import re
import string
from Utils.processing_utils import get_char_sentence, get_char_corpus

# PREPROCESSING TEXT
class TextPreprocessor:

    def __init__(self, df_to_clean, column_to_clean='review_content', 
                 chars=string.ascii_lowercase + string.digits + " "):
        self.df_to_clean = df_to_clean
        self.column_to_clean = column_to_clean
        self.corpus = self.corpus_creator()
        self.chars = chars

    def corpus_creator(self):
        '''
        #TODO
        '''
        corpus = self.df_to_clean[self.column_to_clean].tolist()

        return corpus

    def lowercase_transformer(self):
        '''
        #TODO
        '''
        corpus = [review.lower() for review in self.corpus]

        return corpus
    
    def decontractor(self, sentence): 
        '''
        #TODO
        '''

        # punctuation mistake 
        sentence = re.sub(r"’", "'", sentence)
        
        # specific
        sentence = re.sub(r"won\'t", "will not", sentence)
        sentence = re.sub(r"can\'t", "can not", sentence)

        # general
        sentence = re.sub(r"n\'t", " not", sentence)
        sentence = re.sub(r"\'re", " are", sentence)
        sentence = re.sub(r"\'s", " is", sentence)
        sentence = re.sub(r"\'d", " would", sentence)
        sentence = re.sub(r"\'ll", " will", sentence)
        sentence = re.sub(r"\'t", " not", sentence)
        sentence = re.sub(r"\'ve", " have", sentence)
        sentence = re.sub(r"\'m", " am", sentence)

        return sentence

    def accent_transformer(self):
        '''
        # TODO
        '''
        transform_dict = {'ú':'u', 'ß':'s', 'î':'i', 'í':'i', 'è':'e', 'ö':'o', 
                        'é':'e','ï':'i', 'ê':'e', 'ť':'t', 'ü':'u', 'ó':'o', 
                        'ñ':'n', 'ć':'c','ù':'u', 'ț':'t', 'û':'u', 'â':'a', 
                        'ô':'o', 'à':'a', 'á':'a','ĺ':'l', 'ç':'c', 'ď':'d', 
                        'е':'e', 'ı':'i'}
        transformer = str.maketrans(transform_dict)
        
        return [review.translate(transformer) for review in self.corpus]

    def char_filter(self):
        '''
        # TODO
        '''
        corpus_chars = get_char_corpus(self.corpus)
        set_chars = get_char_sentence(self.chars)

        unwanted = corpus_chars - set_chars # set difference

        transform_dict = {char:' ' for char in unwanted}
        transformer = str.maketrans(transform_dict)

        return [review.translate(transformer) for review in self.corpus]

    def tokenizer(self):
        '''
        # TODO
        '''
        corpus = [word_tokenize(review) for review in self.corpus]

        return corpus

    def stopword_remover(self):
        '''
        # TODO
        '''
        #create list of stopwords to remove
        stopword_list = stopwords.words('english')

        #remove stopwords
        corpus = [[token for token in tokenized_review if token not in stopword_list] 
                        for tokenized_review in self.corpus]
        
        return corpus

    def transform(self):
        # call lowercase
        self.corpus = self.lowercase_transformer()
        # call decontractor
        self.corpus = [self.decontractor(review) for review in self.corpus]
        # call accent_tranformer
        self.corpus = self.accent_transformer()
        # call character filter
        self.corpus = self.char_filter()
        # call tokenizer
        self.corpus = self.tokenizer()
        # call stopword remover
        self.corpus = self.stopword_remover()

# STEMMING/LEMMATIZING TEXT
def stem_corpus(corpus, stemmer_type="Lancaster"): 
    '''
        # stemmer type: Lancaster or Porter
    '''
    if stemmer_type=="Lancaster":
        stemmer = LancasterStemmer()
    else:
        stemmer = PorterStemmer()

    for i in range(len(corpus)):
        for j in range(len(corpus[i])):
            corpus[i][j] = stemmer.stem(corpus[i][j])
    return corpus