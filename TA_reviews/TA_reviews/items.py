# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TAReview(scrapy.Item):
    """Used to parse reviews from Trip Advisor"""
    review_url = scrapy.Field()
    # id = scrapy.Field() #not necessarily useful information 
    review_title = scrapy.Field()
    review_content = scrapy.Field()
    review_date = scrapy.Field()
    review_rating = scrapy.Field()
    review_likes = scrapy.Field()
    user_number_reviews = scrapy.Field()
    user_number_likes = scrapy.Field()