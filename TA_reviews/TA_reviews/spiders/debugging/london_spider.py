import scrapy
from TA_reviews.items import TAReview

class LondonSpider(scrapy.Spider):
    name = "London"

    def __init__(self, *args, **kwargs): 
        super(LondonSpider, self).__init__(*args, **kwargs)

        self.page_nb = 1 
        self.review_page_nb = 1 
        self.max_page = 2 # 30 restaurants per page
        self.max_review_pages = 2 # 10 reviews per page
         
    def start_requests(self):
        ''' '''
        url = 'https://www.tripadvisor.co.uk/Restaurants-g191259-Greater_London_England.html'
        
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        '''
        '''
        # get restaurant urls in current page
        xpath = '//*[@id="component_2"]/div//div/span/div[1]/div[2]/div[1]/div/span/a/@href'
        restaurant_urls = response.xpath(xpath).extract()
        for restaurant_url in restaurant_urls:
            yield response.follow(url=restaurant_url, callback=self.parse_resto, cb_kwargs={'pages_parsed':1})
        
        # move to next page
        next_resto_page_number = response.xpath('//*[@id="EATERY_LIST_CONTENTS"]//a[@class="nav next rndBtn ui_button primary taLnk"]/@data-page-number').extract_first()

        if next_resto_page_number is not None and self.page_nb < self.max_page:
            self.page_nb += 1
            # retrieve url of next page
            next_resto_page_url = response.xpath('//*[@id="EATERY_LIST_CONTENTS"]//a[@class="nav next rndBtn ui_button primary taLnk"]/@href').extract_first()
            # parse next page
            yield response.follow(url=next_resto_page_url, callback=self.parse)

    def parse_resto(self, response, pages_parsed):
        '''
        '''
        # get current page TO DO: put it in utils 
        xpath = '//div[@class="pageNumbers"]/a/@class'
        
        is_first_page = response.xpath(xpath).extract_first()=='pageNum first current '
        if not is_first_page:
            xpath = '//div[@class="pageNumbers"]/a[@class="pageNum current "]/@data-page-number'
            current_page = int(response.xpath(xpath).extract_first())
        else:
            current_page = 1
        
        if current_page == 1:
            resto_item = {}
            resto_item['resto_name'] = response.xpath('//div[@data-test-target="restaurant-detail-info"]/div/h1/text()').extract()

            yield resto_item

        # get review urls
        urls_review = response.xpath('//div[@class="reviewSelector"]/div/div/div/a/@href').extract()
        for url_review in urls_review:
                yield response.follow(url=url_review, callback=self.parse_review)    
        
        # move to next page
        next_review_page_number = response.xpath('//a[@class="nav next ui_button primary"]/@data-page-number').extract_first()
        if next_review_page_number is not None and pages_parsed < self.max_review_pages:
            # retrieve url of next page
            next_review_page_url = response.xpath('//a[@class="nav next ui_button primary"]/@href').extract_first()
            # parse next page
            yield response.follow(url=next_review_page_url, callback=self.parse_resto, cb_kwargs={'pages_parsed':pages_parsed+1})

    def parse_review(self, response):
        '''
        Parses through a Trip Advisor review page and yields useful iformation 
        about the review.

        Returns
        -------
        review_item: TAReview object
            includes the relevant information extracted from the review
        '''
        review_item = TAReview()
        # review_item['review_url'] = response.request.url

        # get review ID (else long reviews with empty lines not recognized)
        review_id = response.xpath(
            '//div[@class="reviewSelector"]/@data-reviewid'
        ).extract_first()
        xpath = '//div[@data-reviewid="' + review_id + '"]/div'
        review_xpath = xpath + '/div[@class="ui_column is-9"]' # review data

        review_item['review_title'] = response.xpath(
            review_xpath + '//div[@class="quote"]/a/span/text()'
        ).extract_first()

        yield review_item
                 
    