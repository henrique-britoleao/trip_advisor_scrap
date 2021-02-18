import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
nltk.download('averaged_perceptron_tagger')

class LemmatizeCorpus:
    '''
    Class to lemmatize preprocessed corpus

    Parameters
    ----------
    lemmatizer: function
        lemmatizer to be used
    
    corpus: list
        list containing all reviews
    
    Attributes
    ----------
    corpus: list
        list containing all reviews
    
    sentence: str
        sentence to be lemmatized

    '''

    def __init__(self, corpus):
        self.lemmatizer = WordNetLemmatizer()
        self.corpus = corpus

    def nltk2wn_tag(self, nltk_tag):
        '''Returns WORDNET POS compliance to WORDENT lemmatization (a,n,r,v).'''
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
        '''Returns lemmatized sentence as list.'''
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
        '''Returns lemmatized corpus as list.'''
        lemmatized_corpus = [self.lemmatize_sentence(sentence) 
                             for sentence in self.corpus]
        return lemmatized_corpus