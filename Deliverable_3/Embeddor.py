import gensim
from gensim.test.utils import get_tmpfile
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
 

class Embeddor:
    '''
    Class to embed the words of the reviews obtained from Trip Advisor
    Outputs a dataframe with reviews as rows and principal components as columns

    Parameters
    ----------
    corpus: list
        list containing all reviews 
   
    Attributes
    ----------
    corpus: list
        list containing all reviews  
    
    '''
    def __init__(self, corpus):
        self.corpus = corpus

    def tfidf(self):
        ''' Returns a df with the tfidf vector of each word in the corpus'''
        untokenized_corpus = [" ".join(map(str, words)) for words in self.corpus]
        vectorizer = TfidfVectorizer(stop_words='english')
        vect_corpus = vectorizer.fit_transform(untokenized_corpus)
        feature_names = np.array(vectorizer.get_feature_names())
        df_tfidf = pd.DataFrame(vect_corpus.todense(), columns = feature_names)

        return df_tfidf, feature_names
  
    def pretrained(self, size_embedding=300, vec_method="word2vec"):
        ''' Returns a df with the word2vec or fasttext vector 
        of each word in the corpus '''
        if vec_method=="word2vec":
            model = gensim.models.Word2Vec(size=size_embedding, window=3,
                                 min_count=5, workers=4, seed=1, iter=50)
        elif vec_method=="fasttext":
            model = gensim.models.FastText(size=size_embedding, window=3,
                                 min_count=5, workers=4, sg=1, seed=1, iter=50)
      
        model.build_vocab(self.corpus)
        model.train(self.corpus, total_examples=model.corpus_count, 
                    epochs=model.iter) 

        embedding_matrix = dict()

        for word in model.wv.vocab.keys():
            embedding_matrix[word] = list(model.wv[word]) 

        embedding_matrix = pd.DataFrame(embedding_matrix)
      
        return embedding_matrix, model
 
    def select_n_components(self, method, var_threshold=0.95):
        ''' Returns the number of optimal components 
        to explain a specified ratio of the variance'''
        var_ratio = method.explained_variance_ratio_
        total_variance = 0.0
        n_components = 0
        for explained_variance in var_ratio:
            total_variance += explained_variance
            n_components += 1      
            if total_variance >= var_threshold:
                break
       
        return n_components   

    def dimension_reduction(self, vec_method="word2vec", how="PCA", 
                            n_components="n_opt", threshold=0.95):
        ''' Returns the embedding matrix after dimensionality reduction 
        (SVD or PCA)'''
        word_vectors = self.embedding_matrix
        n_max = word_vectors.shape[1]-1
        if vec_method in ["word2vec", "fasttext"]:
            word_vectors = self.embedding_matrix.T
            n_max = word_vectors.shape[1]-1

        if n_components == "n_opt":
            n_components = n_max

        if how == "SVD":
            method = TruncatedSVD(n_components)
        elif how == "PCA":
            method = PCA(n_components)
        else:
            raise NameError('"how" has to be in ["PCA", "SVD"]')

        if n_components == n_max:
            method.fit_transform(word_vectors)            
            n_components = self.select_n_components(method, 
                                                    var_threshold=threshold)
            print("The optimal number of components is: ", n_components)
            
            if how == "SVD":
                method = TruncatedSVD(n_components)
            elif how == "PCA":
                method = PCA(n_components)
            else:
                raise NameError('"how" has to be in ["PCA", "SVD"]')

        transformed_mat = method.fit_transform(word_vectors)
        transformed_df = pd.DataFrame(transformed_mat, columns=[how[:2] + 
                                      f'{i+1}' for i in range(n_components)])

        return transformed_mat, transformed_df, n_components
    
    def tsne(self, n_components_tsne=3):
        ''' Returns the transformed_mat after tsne dimensionality reduction'''
        tsne = TSNE(n_components=n_components_tsne, verbose=0, perplexity=40, 
                    n_iter=300)
        tsne_pca_results = tsne.fit_transform(self.transformed_mat)
        tsne_pca_df = pd.DataFrame(tsne_pca_results, columns=[f'PC_{i+1}' 
                                   for i in range(n_components_tsne)])
        # add indexes 
        tsne_pca_df.index = self.embedding_matrix.T.index

        return tsne_pca_results, tsne_pca_df    

    def pc_per_review(self, tsne=True, n_components_tsne=3):
        ''' Returns a dataframe of reviews and there principal components'''
        # build mapper
        if tsne:
            reduced_mat = self.tsne_pca_results
            n_components = n_components_tsne
        else:
            reduced_mat = self.transformed_mat
            n_components = self.n_components

        pca_mapper = {}
        for i in range(len(self.embedding_matrix.columns)):
            pca_mapper[self.embedding_matrix.columns[i]] = reduced_mat[i]

        # pca review dataframe
        vectors = []
        for review_content in self.corpus:
            review_vector = []
            for word in review_content:
                try:
                    review_vector.append(list(pca_mapper[word]))
                
                except KeyError:
                    pass
            vectors.append([sum(i) for i in zip(*review_vector)])
        
        #create dataframe
        review_embedding = pd.DataFrame(vectors)

        # set column names
        review_embedding.columns = ["Dimension_"+str(i+1) 
                                    for i in range(n_components)]

        return review_embedding

    def transform(self, vec_method="word2vec", how="PCA", n="n_opt", 
                  tsne=True, n_tnse=3, threshold=0.95):
        #self.corpus = self.corpus
        if vec_method=="tfidf":
            self.embedding_matrix = self.tfidf()[0]
            self.review_embedding = self.dimension_reduction(
                                        vec_method=vec_method, how=how, 
                                        n_components=n, threshold=threshold)[1]

        elif vec_method in ["word2vec", "fasttext"]:
            self.embedding_matrix = self.pretrained(vec_method=vec_method)[0]
            self.model = self.pretrained(vec_method=vec_method)[1]
            self.transformed_mat, self.transformed_df, self.n_components = self.dimension_reduction(vec_method=vec_method, how=how, n_components=n, threshold=threshold)
            if tsne:
                self.tsne_pca_results, self.tsne_pca_df = self.tsne(
                                                    n_components_tsne=n_tnse)
            self.review_embedding = self.pc_per_review(n_components_tsne=n_tnse, 
                                                       tsne=tsne)
        
        else:
            raise NameError('"vec_method" has tho be in ["word2vec", "fasttext",\
                             "tfidf"]')