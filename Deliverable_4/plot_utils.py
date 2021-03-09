import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class PlotAttentionWeights:
    """Function to untokenize review and plot attention weights for each word in each sentence of a review.

    Parameters
    ----------
    padded_review: list of one tensor of shape (sentences_maxlen, words_maxlen)
        List of sentences (strings) of the review.
    
    han_model: tf HAN model with loaded weight.

    reverse_word_mapper: reverse dictionary with integers and associated words from tokenizer.

    Attributes
    -------
    get_weights: return attention weights computed with HAN model as list of lists. 
    untokenize_sentence: return untokenized sentences with words associated with each integer token.
    untokenize_review: return untokenized sequences as a list of untokenized sentences in a review.
    plot_attention_weights_sentences: plot attention weights per word for each sentence in a review.

    """

    def __init__(self, padded_review, han_model, reverse_word_mapper):
        self.review = padded_review
        self.model = han_model
        self.word_mapper = reverse_word_mapper

    def get_weights(self):
        context_vector, attention_weights = self.model.word_to_sentence_encoder(self.review)
        return attention_weights[0]

    def untokenize_sentence(self, sentence):
        untokenized_sequence = [self.word_mapper[token] if token!=0 else token for token in sentence]
        return untokenized_sequence

    def untokenize_review(self):
        padded_seq_review = self.review[0]
        seq_as_array = list(np.array(padded_seq_review))
        untokenized_seq = [self.untokenize_sentence(sentence) for sentence in seq_as_array]
        return untokenized_seq

    def plot_attention_weights_sentences(self):
        attention_weights = self.get_weights()
        untokenized_seq = self.untokenize_review()
        #return untokenized_seq, attention_weights

        for i in range(len(untokenized_seq)):
            weights = [np.array(x)[0] for x in list(attention_weights[i])]
            untokenized_sent = untokenized_seq[i]
            summ = pd.DataFrame({'word': untokenized_sent, 'weights': weights})
            if np.all(summ['word']==0):
                pass
            else:
                plt.figure(figsize=(10, 6))
                plt.title(f'Phrase {i+1} in the review')
                sns.barplot(x=summ[summ['word']!=0]['word'], y=summ[summ['word']!=0]['weights'])
                plt.xticks(rotation=90)
                plt.show()