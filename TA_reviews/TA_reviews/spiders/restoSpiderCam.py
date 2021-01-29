import scrapy
from TA_reviews.items import TAReview

class RestoPerso(scrapy.Spider):
    name = "RestoTAPerso"

    def __init__(self, *args, **kwargs): 
        super(RestoPerso, self).__init__(*args, **kwargs)

        self.page_nb = 1 
        self.review_page_nb = 1 
        self.max_page = 1 # 30 restaurants per page
        self.max_review_pages = 50 # 10 reviews per page

    def start_requests(self):
        '''
        # TODO
        '''
        url = 'https://www.tripadvisor.co.uk/Restaurants-g191259-Greater_London_' \
              'England.html'
        
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        '''
        # TODO
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
    
    def parse_resto(self, response, pages_parsed):
        '''
        # TODO
        '''
        # get current page TODO: put it in utils 
        xpath = '//div[@class="pageNumbers"]/a/@class'

        is_first_page = response.xpath(xpath).extract_first() == 'pageNum first current '
        if not is_first_page:
            xpath = '//div[@class="pageNumbers"]/a[@class="pageNum current "]' \
                    '/@data-page-number'
            current_page = int(response.xpath(xpath).extract_first())
        else:
            current_page = 1
        # if first page, add restaurant information 
        # TODO: implement Item Retaurant; add more information
        # TODO: look for more items to add 
        if current_page == 1:
            resto_item = {}
            xpath_name = '//div[@data-test-target="restaurant-detail-info"]/div' \
                         '/h1/text()'
            xpath_rating = '//a[@href="#REVIEWS"]/svg/@title'
            resto_item['resto_url'] = response.request.url
            resto_item['resto_name'] = response.xpath(xpath_name).extract()
            resto_item['resto_rating'] = response.xpath(xpath_rating).extract()
            
            details = response.xpath('//div[@class="_3UjHBXYa"]')
            keys = details.xpath('//div[@class="_14zKtJkz"]/text()').extract()
            values = details.xpath('//div[@class="_1XLfiSsv"]/text()').extract()

            details_info = dict(zip(keys, values))
            resto_item.update(details_info)

            yield resto_item

        # get review urls
        xpath_review_url = '//div[@class="reviewSelector"]/div/div/div/a/@href'
        urls_review = response.xpath(xpath_review_url).extract()
        for url_review in urls_review:
                yield response.follow(url=url_review, callback=self.parse_review)    
        
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
                                  cb_kwargs={'pages_parsed':pages_parsed+1})

    def parse_review(self, response):
        '''
        Parses through a Trip Advisor review page and yields useful iformation 
        about the review.

        Returns
        -------
        review_item: TAReview object
            includes the relevant information extracted from the review
        '''
        # TODO add restaurant key, to merge the two databases
        # TODO potentially add more keys
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