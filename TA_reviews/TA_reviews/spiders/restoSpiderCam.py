import scrapy

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
        item = {}

        # get each restaurant url and parse it
        xpath = '//*[@id="component_2"]/div//div/span/div[1]/div[2]/div[1]/div/span/a/@href'
        restaurant_urls = response.xpath(xpath).extract()
        for restaurant_url in restaurant_urls:
            item['restaurant_url'] = restaurant_url
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

        # get review urls 
        urls_review = response.xpath('//div[@class="reviewSelector"]/div/div/div/a/@href').extract()
        for url_review in urls_review:
            yield response.follow(url=url_review, callback=self.parse_review)    

        # doesn't work > goal is to go to the next page of reviews (only get 5 by restaurant so far)
        #next_page_reviews = response.xpath('//a[@class="nav next ui_button primary"]/@data-page-number').extract_first()
        #if self.review_nb < self.max_reviews and next_page_reviews is not None:
        #    yield response.follow(url=next_page_reviews, callback=self.parse_resto)

    def parse_review(self, response):
        # works fine
        # TO DO: create "review" scrapy Item in items.py

        self.review_nb += 1
        review_item = {}
        review_item['review_url'] = response.request.url

        # get review ID to indicate the right xpath (otherwise long reviews with empty lines are not recognized)
        review_item['review_id'] = response.xpath('//div[@class="reviewSelector"]/@data-reviewid').extract_first()
        xpath = '//div[@data-reviewid="' + review_item['review_id'] + '"]/div/div/div/div'

        # once we have the xpath for this specific review (id), get title, content, date and overall customer rating
        review_item['review_title'] = response.xpath(xpath).xpath('div/a/span/text()').extract_first()
        review_item['review_content'] = response.xpath(xpath).xpath('div[@data-prwidget-name="reviews_text_summary_hsx"]/div/p/text()').extract()
        review_item['review_date'] = response.xpath(xpath).xpath('div[@data-prwidget-name="reviews_stay_date_hsx"]/text()').extract_first()
        review_item['rating'] = response.xpath(xpath).xpath('div[@class="rating reviewItemInline"]/span/@class').extract_first()
        
        yield review_item

