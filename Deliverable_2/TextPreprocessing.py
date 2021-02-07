#import libraries 
import pandas as pd 
import numpy as np 

# nltk functions
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
nltk.download('averaged_perceptron_tagger')

# other textpreprocessing functions
import re
import string
import cld2
from utils.processing_utils import get_char_sentence, get_char_corpus

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

# STEMMING TEXT
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

# LEMMATIZING TEXT
class LemmatizeCorpus:

    def __init__(self, corpus):
        self.lemmatizer = WordNetLemmatizer()
        self.corpus = corpus

    def nltk2wn_tag(self, nltk_tag):
        if nltk_tag.startswith('J'):
            return wordnet.ADJ
        elif nltk_tag.startswith('V'):
            return wordnet.VERB
        elif nltk_tag.startswith('N'):
            return wordnet.NOUN
        elif nltk_tag.startswith('R'):
            return wordnet.ADV
        else:                    
            return None

    def lemmatize_sentence(self, sentence):
        sentence = sentence.copy()
        sentence = " ".join(sentence)
        nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))    
        wn_tagged = map(lambda x: (x[0], self.nltk2wn_tag(x[1])), nltk_tagged)
        res_words = []
        for word, tag in wn_tagged:
            if tag is None:                        
                res_words.append(word)
            else:
                res_words.append(self.lemmatizer.lemmatize(word, tag))

        return res_words

    def lemmatize_corpus(self):
        lemmatized_corpus = [self.lemmatize_sentence(sentence) for sentence in self.corpus]
        return lemmatized_corpus

