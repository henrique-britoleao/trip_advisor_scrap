import tensorflow as tf

class Attention(tf.keras.layers.Layer):
    """Attention mechanism used in "Hierarchical Attention Networks for Document Classification" paper.
        
    ```python
    attention_layer = Attention(units=64)
    ```
    """
    def __init__(self, units):
        """Attention layer constructor.

        Parameters
        ----------
        units: int.
            Dimension of the projection space.
        """
        super(Attention, self).__init__()
        self.W = tf.keras.layers.Dense(units)
        self.u = tf.keras.layers.Dense(1)

    def call(self, sequence):
        """Layer forward method.
        """
        attention_logits = self.u(tf.nn.tanh(self.W(sequence)))
        attention_weights = tf.nn.softmax(attention_logits, axis=-2)

        weighted_vectors = attention_weights * sequence
        context_vector = tf.reduce_sum(weighted_vectors, axis=-2)

        return context_vector, attention_weights


class HierarchicalAttentionNetwork(tf.keras.Model):
    """Hierarchical Attention Network implementation.

    Reference :
    * Hierarchical Attention Networks for Document Classification : https://www.cs.cmu.edu/~./hovy/papers/16HLT-hierarchical-attention-networks.pdf

    """
    def __init__(self, vocab_size, embedding_dim, gru_units, attention_units, classifier_units, pretrained_weights=None):
        """Hierarchical Attention Network class constructor.
        """
        super(HierarchicalAttentionNetwork, self).__init__()
        
        if pretrained_weights is not None:
            initializer = tf.keras.initializers.Constant(pretrained_weights)
        else:
            initializer = "uniform"

        self.embedding = tf.keras.layers.Embedding(
            vocab_size, 
            embedding_dim, 
            embeddings_initializer=initializer,
            trainable=True
        )
        self.WordGRU = tf.keras.layers.Bidirectional(
            tf.keras.layers.GRU(
                units=gru_units,
                activation="tanh",
                return_sequences=True
            ), 
            merge_mode='concat',
        )
        self.WordAttention = Attention(units=attention_units)
        self.SentenceGRU = tf.keras.layers.Bidirectional(
            tf.keras.layers.GRU(
                units=gru_units,
                activation="tanh",
                return_sequences=True
            ), 
            merge_mode='concat',
        )
        self.SentenceAttention = Attention(units=attention_units)
        self.fc = tf.keras.layers.Dense(units=classifier_units)

    def call(self, x):
        """Model forward method.
        """
        sentences_vectors, _ = self.word_to_sentence_encoder(x)
        document_vector, _ = self.sentence_to_document_encoder(sentences_vectors)
        return self.fc(document_vector)

    def word_to_sentence_encoder(self, x):
        """Given words from each sentences, 
        encode the contextual representation of the words from the sentence
        with Bidirectional GRU and Attention, and output a sentence_vector
        """
        x = self.embedding(x)
        x = tf.keras.layers.TimeDistributed(self.WordGRU)(x)
        context_vector, attention_weights = self.WordAttention(x)

        return context_vector, attention_weights
    
    def sentence_to_document_encoder(self, sentences_vectors):
        sentences_vectors = self.SentenceGRU(sentences_vectors)
        document_vector, attention_weights = self.SentenceAttention(sentences_vectors)
        return document_vector, attention_weights