import scrapy
from TA_reviews.items import TAReview

def ratings_mapper(ratings):
    map = {f'ui_bubble_rating bubble_{i+1}0' : i+1 for i in range(5)}
    return [map[rating] for rating in ratings]

class RestoSpider(scrapy.Spider):
    name = "Restaurant"

    def __init__(self, *args, **kwargs): 
        super(RestoSpider, self).__init__(*args, **kwargs)

        self.review_page_nb = 1 
        self.max_review_pages = 50 # 10 reviews per page 
        self.filter = [1, 2, 3, 4]  

    def start_requests(self):
        url ='https://www.tripadvisor.co.uk/Restaurant_Review-g1639613-d3704640-Reviews-Mario_s_Pizzeria-Sidcup_Greater_London_England.html'    
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, pages_parsed=1):        
        # get review urls
        xpath_review_url = '//div[@class="reviewSelector"]/div/div/div/a/@href'
        urls_review = response.xpath(xpath_review_url).extract()

        # get review ratings
        xpath_review_rating = '//div[@class="reviewSelector"]//div[@class=' \
                              '"ui_column is-9"]/span[1]/@class'
        review_ratings = response.xpath(xpath_review_rating).extract()
        # clean ratings 
        review_ratings_mapped = ratings_mapper(review_ratings)

        for (url, rating) in zip(urls_review, review_ratings_mapped):
            if rating in self.filter:
                yield response.follow(url=url, callback=self.parse_review)
            else:
                pass

        # move to next page
        xpath_next = '//a[@class="nav next ui_button primary"]/@data-page-number'
        next_rev_page_nb = response.xpath(xpath_next).extract_first()
        if next_rev_page_nb is not None and pages_parsed < self.max_review_pages:
            # retrieve url of next page
            xpath_next_url = '//a[@class="nav next ui_button primary"]/@href'
            next_rev_page_url = response.xpath(xpath_next_url).extract_first()
            # parse next page
            yield response.follow(url=next_rev_page_url,
                                  callback=self.parse,
                                  cb_kwargs={'pages_parsed':pages_parsed+1})

    def parse_review(self, response):
        review_item = TAReview()

        review_id = response.xpath(
            '//div[@class="reviewSelector"]/@data-reviewid'
        ).extract_first()
        xpath = '//div[@data-reviewid="' + review_id + '"]/div'

        review_xpath = xpath + '/div[@class="ui_column is-9"]' # review data

        review_item['review_title'] = response.xpath(
            review_xpath + '//div[@class="quote"]/a/span/text()'
        ).extract_first()
        review_item['review_rating'] = response.xpath(
            review_xpath + 
            '//div[@class="rating reviewItemInline"]/span/@class'
        ).extract_first()
        
        yield review_item   
    

    