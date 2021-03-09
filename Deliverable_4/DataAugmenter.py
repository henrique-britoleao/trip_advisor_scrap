import os
from numpy import full
from pandas import DataFrame, concat
from augment_utils import parse_sentence

class DataAugmenter():       
    '''
    # TODO
    '''
    def __init__(self, ratings):
        # check which ratings have already been augmented

        files_ratings_dict = {'aug_ones.txt':1, 'aug_twos.txt':2, 'aug_threes.txt':3,
                              'aug_fours.txt':4, 'aug_fives.txt':5}
        self._ratings_files_dict = {1:'ones.txt', 2:'twos.txt', 3:'threes.txt',
                                    4:'fours.txt', 5:'fives.txt'}
        self._ratings_aug_files_dict = {1:'aug_ones.txt', 2:'aug_twos.txt', 
                                        3:'aug_threes.txt', 4:'aug_fours.txt',
                                        5:'aug_fives.txt'}
   
        aug_ratings_files = os.listdir('augmented_data')  
        
        self._augmented_ratings = [files_ratings_dict[file] for file in aug_ratings_files] 

        if self._augmented_ratings:
            print('The following reviews have been augmented:',
                  *self._augmented_ratings)
        
        # get ratings remaining to be augmented
        self._ratings_to_augment = [
            rating for rating in ratings if rating not in self._augmented_ratings
        ]
        
        if self._ratings_to_augment:
            print('The following reviews still have to be augmented:', 
                  *self._ratings_to_augment, 
                  '\n Call the augment method to complete the data augmentation.')
        
        # get ratings to be merged 
        self._ratings_to_merge = ratings
    
    def augment(self, data_path='data_to_augment'):
        '''
        # TODO
        '''
        for rating in self._ratings_to_augment:
            file = self._ratings_files_dict[rating]

            reviews = self._read(os.path.join(data_path,file))

            augmented = [parse_sentence(review) for review in reviews]

            self._write(
                os.path.join('augmented_data',self._ratings_aug_files_dict[rating]),
                augmented
            )

    def merge(self, df, ratings_to_merge=None):
        '''
        # TODO
        '''
        if ratings_to_merge is None:
            ratings_to_merge = self._ratings_to_merge
        
        self._output_df = df

        for rating in ratings_to_merge:
            # load augmented data
            file = self._ratings_aug_files_dict[rating]
            aug_reviews = self._read(os.path.join('augmented_data',file))
            # initialize array of ratings
            ratings = full(shape=len(aug_reviews), fill_value=rating)
            aug_data = zip(aug_reviews, ratings)
            # build data frame
            aug_df = DataFrame(aug_data, columns=[
                'review_content', 'review_rating'
            ])
            # merge created df with df parsed
            self._output_df = concat([self._output_df, aug_df])
        
        return self._output_df

    def _read(self, file):
        '''
        # TODO
        '''

        with open(file, 'r') as f:
            reviews = f.readlines()
        # clean text of special characters
        for i in range(len(reviews)):
            reviews[i] = reviews[i].strip('\n').strip(' ')
        
        return reviews
    
    def _write(self, file, aug_sentences):
        '''
        # TODO
        '''
        with open(file, 'a') as f:
            for sentence in aug_sentences:
                f.write(f'{sentence}\n')