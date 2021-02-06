import itertools
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def show_wordcloud(corpus, ratings=None, filter_rating=None):
    if filter_rating is not None:
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