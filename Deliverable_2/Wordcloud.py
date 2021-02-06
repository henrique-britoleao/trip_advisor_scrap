import itertools
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def show_wordcloud(corpus, ratings=None, filter_rating=None):
    '''
    Shows a wordcloud with the text contained in courpus.

    Parameters
    ----------
    corpus: list
        corpus containing text to be plotted
    ratings: pd.Series
        column containing ratings of each review
    filter_rating: 
        rating to be filtered 
    
    Returns
    -------
    None 

    '''
    # filter ratings
    if filter_rating is not None:
        if ratings is None:
            raise ValueError('ratings must not be None to filter ratings')
        
        unique_ratings = ratings.unique()

        if filter_rating not in unique_ratings:
            raise ValueError(
                f'filter_rating must be one of {unique_ratings}'
            )

        rating_idx = np.where(ratings==filter_rating)[0]
        corpus = corpus.copy()
        corpus = [corpus[i] for i in rating_idx]

    # detokenize corpus
    full_corpus = list(itertools.chain.from_iterable(corpus))
    full_corpus = " ".join(review for review in full_corpus)

    # generate wordcloud
    wordcloud = WordCloud(background_color="white").generate(full_corpus)

    if filter_rating is not None:
        print(f"Wordcloud of reviews with rating {filter_rating}:")
    else:
        print("Wordcloud of reviews for all ratings")

    plt.figure(figsize=(15, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()