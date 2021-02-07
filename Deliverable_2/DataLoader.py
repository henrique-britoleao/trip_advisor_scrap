import json
import pandas as pd 
import os 
import sys
import re
import calendar

from Utils.loader_utils import read_jl_file, extract_details, get_resto_id, convert_date
from Utils.processing_utils import language_filter
###############################################################################
class TADataLoader:
    '''
    Class used to load the data scraped from Trip Advisor using the spider 
    contained in Deliverable 1. 

    Parameters
    ----------
    data_file: str
        name of the file containing data
    data_path: str 
        path to data_file

    Attributes
    ----------
    data_file: str
        name of the file containing data
    data_path: str 
        path to data_file
    df_resto: pandas.DataFrame
        contains the restaurant information scrapped
    df_reviews: pandas.DataFrame
        contains the review information scrapped
    __dfs_built: Bool
        indicates if df_resto and df_reviews have been build
    __review_clean: Bool
        indicates if df_reviews has been cleaned
    __resto_clean: Bool
        indicates if df_resto has been cleaned

    '''
    def __init__(self, data_file='scrapped_data.jl', 
                data_path='../Deliverable_1/TA_reviews/scrapped_data'):
        self.data_file = data_file
        self.data_path = data_path
        self.__dfs_built = False
        self.__review_clean = False
        self.__resto_clean = False

    def _build_df(self):
        '''Builds data frames from .jl file and store them in class.'''
        data = read_jl_file(os.path.join(self.data_path,self.data_file))

        df = pd.DataFrame(data)
        df_restos = df[df['resto_url'].notnull()] # unique to resto
        df_reviews = df[df['review_url'].notnull()] # unique to review

        # check there are no duplicates
        if df_restos['resto_url'].duplicated().sum() > 0:
            raise TypeError('Data has duplicated restaurants.')
        if df_reviews['review_url'].duplicated().sum() > 0:
            raise TypeError('Data has duplicated reviews.')

        df_reviews = language_filter(df_reviews, 'review_content')

        self.__dfs_built = True
        self.df_resto = df_restos.dropna(axis=1, how='all')
        self.df_review = df_reviews.dropna(axis=1, how='all')

    def _clean_review(self):
        '''Cleans self.df_reviews.'''
        # transform resto_name
        self.df_review['resto_name'] = self.df_review["resto_name"].apply(
            lambda x: x[0]
        )
        # fix formatting of review likes
        self.df_review['review_likes'] = self.df_review['review_likes'].apply(
            lambda x: 0 if x is None else int(x.split(" ")[0])
        )
        # fix formatting of user likes
        self.df_review['user_number_likes'] = (
            self.df_review['user_number_likes'].fillna(0).apply(int)
        )
        # fix formatting of user number reviews
        self.df_review['user_number_reviews'] = (
            self.df_review['user_number_reviews'].apply(int)
        )
        # fix ratings
        self.df_review['review_rating'] = (
            self.df_review['review_rating'].apply(lambda x: int(x[-2]))
        )
        # extract research ID
        self.df_review = get_resto_id(self.df_review, 'review')

        self.df_review['review_id'] = self.df_review['review_url'].apply(
            lambda x: re.findall(r'\-r(\d+)\-', x)[0]
        )

        # convert review dates to datetime objects
        self.df_review = convert_date(self.df_review)

        # add review length
        self.df_review['review_length'] = self.df_review['review_content'].apply(lambda x: len(x))

        # set bool to reflect operation was performed
        self.__review_clean = True

    def _clean_resto(self):
        '''Cleans self.df_resto.'''
        # transform resto_name
        self.df_resto['resto_name'] = self.df_resto['resto_name'].apply(
            lambda x: x[0]
        )
        # extract research ID
        self.df_resto = get_resto_id(self.df_resto, 'resto')

        # extract rating
        self.df_resto['resto_rating'] = self.df_resto['resto_rating'].apply(
            lambda rating: float(re.findall(r'([0-9]\.[0-9])\s', rating[0])[0])
        )
        # extract additional information
        self.df_resto = extract_details(self.df_resto)

        # set bool to reflect operation was performed
        self.__resto_clean = True
    
    def load_reviews(self):
        '''Returns data frame with review data.'''
        if not self.__dfs_built:
            self._build_df()
        if not self.__review_clean:
            self._clean_review()

        return self.df_review
    
    def load_restos(self):
        '''Returns data frame with restaurant data.'''
        if not self.__dfs_built:
            self._build_df()
        if not self.__resto_clean:
            self._clean_resto()

        return self.df_resto       