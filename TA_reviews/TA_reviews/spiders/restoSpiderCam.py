import scrapy
from TA_reviews.items import TAReview, TAResto
from TA_reviews.utils.get_current_page import get_current_page

class RestoPerso(scrapy.Spider):
    '''
    Spider to crawl through a Trip Advisor city page and scrap restaurant 
    reviews.
    '''
    name = "RestoTAPerso"

    def __init__(self, *args, **kwargs): 
        super(RestoPerso, self).__init__(*args, **kwargs)

        self.page_nb = 1 
        self.review_page_nb = 1 
        self.max_page = 4 # 30 restaurants per page
        self.max_review_pages = 50 # 10 reviews per page

    def start_requests(self):
        '''Submits first request to Spider to crawl'''
        url = 'https://www.tripadvisor.co.uk/Restaurants-g191259-Greater' \
              '_London_England.html'
        
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):  
        '''
        Parses through a Trip Advisor city page. Yields Requests for each 
        restaurant connected to the city.

        Yields
        ------
        request: scrapy Request object
            request of a restaurant.
        '''
        # get restaurant urls in current page
        xpath = '//*[@id="component_2"]/div//div/span/div[1]/div[2]/div[1]/div/' \
                'span/a/@href'
        restaurant_urls = response.xpath(xpath).extract()
        for restaurant_url in restaurant_urls:
            yield response.follow(url=restaurant_url, callback=self.parse_resto,
                                  cb_kwargs={'pages_parsed':1})

        # move to next page
        xpath_next_resto = '//*[@id="EATERY_LIST_CONTENTS"]//a[@class="nav next ' \
                           'rndBtn ui_button primary taLnk"]'
        next_resto_page_number = response.xpath(xpath_next_resto+'/@data-page-number'
                                                ).extract_first()

        if next_resto_page_number is not None and self.page_nb < self.max_page:
            self.page_nb += 1
            # retrieve url of next page
            next_resto_page_url = response.xpath(xpath_next_resto+'/@href'
                                                 ).extract_first()
            # parse next page
            yield response.follow(url=next_resto_page_url, callback=self.parse)
    
    def parse_resto(self, response, pages_parsed, resto_name=None):         
        '''
        Parses through a Trip Advisor restaurant page. Yields useful 
        information about the restaurant. Yields Requests for each review 
        connected to the restaurant.

        Yields
        ------
        resto_item: 
            includes the relevant information extracted from the restaurant.
        request: scrapy Request object
            request of a review.
        '''
        current_page = get_current_page(response)
        # if first page, add restaurant information 
        # TODO: implement Item Retaurant; add more information
        # TODO: look for more items to add 
        if current_page == 1:
            resto_item = TAResto()
            xpath_name = '//div[@data-test-target="restaurant-detail-info"]/div' \
                         '/h1/text()'
            xpath_rating = '//a[@href="#REVIEWS"]/svg/@title'

            xpath_keys = '//div[@class="_3UjHBXYa"]//div[@class="_14zKtJkz"]/text()'
            xpath_details = '//div[@class="_3UjHBXYa"]//div[@class="_1XLfiSsv"]' \
                            '/text()'

            resto_item['resto_url'] = response.request.url
            resto_item['resto_name'] = response.xpath(xpath_name).extract()
            resto_item['resto_rating'] = response.xpath(xpath_rating).extract()

            resto_item['resto_keys'] = response.xpath(xpath_keys).extract()
            resto_item['resto_details'] = response.xpath(xpath_details).extract()

            # define variable to use as a key on the reviews
            resto_name = response.xpath(xpath_name).extract()  

            yield resto_item

        # get review urls
        xpath_review_url = '//div[@class="reviewSelector"]/div/div/div/a/@href'
        urls_review = response.xpath(xpath_review_url).extract()
        for url_review in urls_review:
                yield response.follow(url=url_review, callback=self.parse_review,
                                      cb_kwargs={'resto_name':resto_name})    
        
        # move to next page
        xpath_next = '//a[@class="nav next ui_button primary"]/@data-page-number'
        next_rev_page_nb = response.xpath(xpath_next).extract_first()
        if next_rev_page_nb is not None and pages_parsed < self.max_review_pages:
            # retrieve url of next page
            xpath_next_url = '//a[@class="nav next ui_button primary"]/@href'
            next_rev_page_url = response.xpath(xpath_next_url).extract_first()
            # parse next page
            yield response.follow(url=next_rev_page_url,
                                  callback=self.parse_resto,
                                  cb_kwargs={'pages_parsed':pages_parsed+1,
                                             'resto_name':resto_name})

    def parse_review(self, response, resto_name):
        '''
        Parses through a Trip Advisor review page and yields useful iformation 
        about the review.

        Yields
        ------
        review_item: TAReview object
            includes the relevant information extracted from the review
        '''
        review_item = TAReview()

        review_item['resto_name'] = resto_name
        review_item['review_url'] = response.request.url

        # get review ID (else long reviews with empty lines not recognized)
        review_id = response.xpath(
            '//div[@class="reviewSelector"]/@data-reviewid'
        ).extract_first()
        xpath = '//div[@data-reviewid="' + review_id + '"]/div'

        # with specific review ID, get useful review information
        review_xpath = xpath + '/div[@class="ui_column is-9"]' # review data
        review_item['review_title'] = response.xpath(
            review_xpath + '//div[@class="quote"]/a/span/text()'
        ).extract_first()
        review_item['review_content'] = response.xpath(
            review_xpath + '//div[@class="entry"]/p/text()'
        ).extract_first()
        review_item['review_date'] = response.xpath(
            review_xpath + 
            '//div[@data-prwidget-name="reviews_stay_date_hsx"]/text()'
        ).extract_first()
        review_item['review_rating'] = response.xpath(
            review_xpath + 
            '//div[@class="rating reviewItemInline"]/span/@class'
        ).extract_first()
        review_item['review_likes'] = response.xpath(
            review_xpath + 
            '//span[@class="numHelp emphasizeWithColor"]/text()'
        ).extract_first()

        # with specific review ID, get user data
        user_path = xpath + '/div[@class="ui_column is-2"]' # user data
        user_data = response.xpath(
            user_path + '//span[@class="badgetext"]/text()'
        ).extract()
        review_item['user_number_reviews'] = user_data[0]

        if len(user_data)==2:
            review_item['user_number_likes'] = user_data[1]
        
        yield review_item