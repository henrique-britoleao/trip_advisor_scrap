def ratings_mapper(ratings):
    '''
    Maps ratings extracted from TA to digits
    
    Parameters
    ----------
    ratings: list
        list with strings containing a TA review rating

    Returns
    -------
    mapped_ratings: list
        list with ints encoding each review 
    '''
    map = {f'ui_bubble_rating bubble_{i+1}0' : i+1 for i in range(5)}
    return [map[rating] for rating in ratings]