import json
import pandas as pd 
import os 
import re
from Deliverable_2.utils import read_jl_file, extract_details

class TADataLoader():
    '''
    # TODO
    '''
    def __init__(self, data_file='scrapped_data', 
                 data_path='/Deliverable_1/TA_reviews/scrapped_data'):
        self.data_file = data_file
        self.data_path = data_path

    def build_df(self):
        '''
        # TODO
        '''
        data = read_jl_file(os.path.join(self.data_path,self.data_file))

        df = pd.DataFrame(data)
        df_restos = df[df['resto_url'].notnull()] # unique to resto
        df_reviews = df[df['review_url'].notnull()] # unique to review

        # check there are no duplicates
        if df_restos.duplicated.sum() >= 1:
            raise TypeError(f'Data has {df_restos.duplicated.sum()}'
                                ' duplicates and must have 0.')
        if df_reviews.duplicated.sum() >= 1:
            raise TypeError(f'Data has {df_reviews.duplicated.sum()}'
                                ' duplicates and must have 0.')

        self.dfs_built = True
        self.df_resto = df_restos.dropna(axis=1, how='all')
        self.df_review = df_reviews.dropna(axis=1, how='all')

    def clean_review(self):
        '''
        # TODO
        '''
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
        # update clean state
        self.review_clean = True

    def clean_resto(self):
        '''
        # TODO
        '''
        # transform resto_name
        self.df_resto['resto_name'] = self.df_resto['resto_name'].apply(
            lambda x: x[0]
        )
        # extract researchID
        self.df_resto['research_id'] = self.df_resto['research_id'].apply(
            lambda x: re.findall(r'\-g(\d+)\-', x)
        )
        self.df_resto['resto_id'] = self.df_resto['research_id'].apply(
            lambda x: re.findall(r'\-d(\d+)\-', x)
        )

        # extract rating
        self.df_resto['resto_rating'] = self.df_resto['resto_rating'].apply(
            lambda rating: float(re.findall(r'([0-9]\.[0-9])\s', rating[0])[0])
        )
        # extract additional information
        self.df_resto = extract_details(self.df_resto)

        self.resto_clean = True
        pass
    
    def load_reviews(self):
        '''
        # TODO
        '''
        if not self.dfs_built:
            self.build_df()

        if not self.review_clean:
            self.clean_review()

        return self.df_review
    
    def load_restos(self):
        '''
        # TODO
        '''
        if not self.dfs_built:
            self.build_df()

        if not self.resto_clean:
            self.clean_resto()

        return self.df_resto       

