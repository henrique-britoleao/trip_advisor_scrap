from nltk.stem import LancasterStemmer, PorterStemmer

def stem_corpus(corpus, stemmer_type="Lancaster"): 
    '''
    Applies a stemmer to a tokenized corpus

    Parameters
    ----------
    corpus: list
        corpus to be stemmed
    stemmer_type: str
        stemmer to be used. Must be either "Lancaster" or 
        "Porter"

    Returns
    -------
    corpus: list
        stemmed corpus
    '''
    if stemmer_type=="Lancaster":
        stemmer = LancasterStemmer()
    elif stemmer_type=="Porter":
        stemmer = PorterStemmer()
    else:
        raise TypeError(
            'stemmer_type must be either "Lancaster" or "Porter"'
        )

    for i in range(len(corpus)):
        for j in range(len(corpus[i])):
            corpus[i][j] = stemmer.stem(corpus[i][j])
    return corpus