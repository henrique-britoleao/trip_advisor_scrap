import scrapy
from TA_reviews.items import TAReview

class RestoPerso(scrapy.Spider):
    name = "RestoTAPerso"

    def __init__(self, *args, **kwargs): 
        super(RestoPerso, self).__init__(*args, **kwargs)

        self.main_nb = 0
        self.resto_nb = 0
        self.review_nb = 0
        self.max_reviews = 30
        self.max_pages = 2

    def start_requests(self):
        url = 'https://www.tripadvisor.co.uk/Restaurants-g191259-Greater_London_England.html'
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        # item = {}

        # get each restaurant url and parse it
        xpath = '//*[@id="component_2"]/div//div/span/div[1]/div[2]/div[1]/div/span/a/@href'
        restaurant_urls = response.xpath(xpath).extract()
        for restaurant_url in restaurant_urls:
            # item['restaurant_url'] = restaurant_url
            yield response.follow(url=restaurant_url, callback=self.parse_resto)

        # go to the next page of restaurants
        xpath = '//*[@id="EATERY_LIST_CONTENTS"]/div/div/a'
        next_page = response.xpath(xpath).css('::attr(href)').extract()[-1]
        next_page_number = response.xpath(xpath).css('::attr(data-page-number)').extract()[-1]
        if int(next_page_number) < self.max_pages:

            yield response.follow(url=next_page, callback=self.parse_resto)
    
    def parse_resto(self, response):
        
        # doesn't work for now but the goal is to scrape restaurant data if we're on the first page of reviews
        # then iterate through all review pages (cf end of the function) and scrape only review urls each time 
        current_page = 1
        #current_page = response.xpath('//div[@class="pageNumbers"]/a[@class="pageNum first current "]/@data-page-number').extract_first()
        #if current_page == None:
        #    current_page = response.xpath('//div[@class="pageNumbers"]/a[@class="pageNum current "]/@data-page-number').extract_first()
        
        # get restaurant info (url, name, rating, cuisine, regimes, price range...)
        # TO DO: create "Resto" item in items.py
        # Issue with details cuisine etc. > not always the same fields. Not sure we can use the dictionary technique below if we create an item.
        if int(current_page) == 1:
            self.resto_nb += 1
            resto_item = {}
            resto_item['resto_url'] = response.request.url
            resto_item['resto_name'] = response.xpath('//div[@data-test-target="restaurant-detail-info"]/div/h1/text()').extract()
            resto_item['resto_rating'] = response.xpath('//a[@href="#REVIEWS"]/svg/@title').extract()
            
            details = response.xpath('//div[@class="_3UjHBXYa"]')
            keys = details.xpath('//div[@class="_14zKtJkz"]/text()').extract()
            values = details.xpath('//div[@class="_1XLfiSsv"]/text()').extract()

            details_info = dict(zip(keys, values))
            resto_item.update(details_info)

            yield resto_item

        # get review from current page 
        urls_review = response.xpath('//div[@class="reviewSelector"]/div/div/div/a/@href').extract()
        for url_review in urls_review:
            yield response.follow(url=url_review, callback=self.parse_review)

        # move to next page
        next_page_number = response.xpath('//a[@class="nav next ui_button primary"]/@data-page-number').extract_first()
        if next_page_number is not None and self.review_nb < self.max_reviews:
            # retrieve url of next page
            next_page_url = response.xpath('//a[@class="nav next ui_button primary"]/@href').extract_first()
            # get reviews from next page
            yield response.follow(url=next_page_url, callback=self.parse_resto)

    def parse_review(self, response):
        '''
        Parses through a Trip Advisor review page and yields useful iformation 
        about the review.

        Returns
        -------
        review_item: TAReview object
            includes the relevant information extracted from the review
        '''
        self.review_nb += 1
        review_item = TAReview()
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