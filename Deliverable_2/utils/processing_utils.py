import numpy as np
import cld2
 
# char set function
def get_char_sentence(sentence): 
    '''
    # TODO 
    '''
    chars = set()
    char_list = list(sentence)

    for char in char_list:
        chars.add(char)

    return chars

def get_char_corpus(corpus):
    '''
    # TODO
    '''
    chars = set()

    for sentence in corpus:
        sent_char = get_char_sentence(sentence)
        chars.update(sent_char)

    return chars

# filter out non-English comments
def language_filter(df, column_to_clean, lang=['ENGLISH', 'Unknown', 'ZHUANG']):
    '''
    # TODO
    '''
    if type(lang) is not list:
        raise TypeError(f'lang must be a list, but is a {type(lang)}')
    else:
        langs = np.array([cld2.detect(review)[2] for review in df[column_to_clean]], 
                    dtype=object) # get list of langs detected in phrase
        # create filter
        filt = langs[:,0,0] == lang[0]
        for language in lang: # iterate over list of languages
            filt = filt | (langs[:,0,0] == language)
        
        # make sure no secong language included
        filt = filt & (langs[:,1,0] == 'Unknown')
        
        filtered_df = df[filt]
        
        return filtered_df.reset_index(drop=True)