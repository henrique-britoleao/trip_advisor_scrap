import scrapy
from TA_reviews.items import TAReview

class RestoSpider(scrapy.Spider):
    name = "Restaurant"

    def __init__(self, *args, **kwargs): 
        super(RestoSpider, self).__init__(*args, **kwargs)

        # self.main_nb = 0
        self.resto_nb = 0
        self.review_nb = 0
        self.max_reviews = 50
        # self.max_pages = 2     

    def start_requests(self):
        url ='https://www.tripadvisor.co.uk/Restaurant_Review-g1639613-d3704640-Reviews-Mario_s_Pizzeria-Sidcup_Greater_London_England.html'    
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # get current page TO DO: put it in utils 
        xpath = '//div[@class="pageNumbers"]/a/@class'

        is_first_page = response.xpath(xpath).extract_first()=='pageNum first current '
        if not is_first_page:
            xpath = '//div[@class="pageNumbers"]/a[@class="pageNum current "]/@data-page-number'
            current_page = int(response.xpath(xpath).extract_first())
        else:
            current_page = 1
        print(f'Current page: {current_page}')
        # if first page, add restaurant information 
        # TO DO: implement Item Retaurant
        if current_page == 1:
            self.resto_nb += 1
            resto_item = {}
            resto_item['resto_name'] = response.xpath('//div[@data-test-target="restaurant-detail-info"]/div/h1/text()').extract()

            yield resto_item

        # get review urls 
        urls_review = response.xpath('//div[@class="reviewSelector"]/div/div/div/a/@href').extract()
        for url_review in urls_review:
            if self.review_nb <= self.max_reviews:
                self.review_nb += 1
                print(f'New review: {self.review_nb}')
                yield response.follow(url=url_review, callback=self.parse_review)      
            else:
                break
        
        #move to next page
        next_page_number = response.xpath('//a[@class="nav next ui_button primary"]/@data-page-number').extract_first()
        if next_page_number is not None and self.review_nb < self.max_reviews:
            next_page_url = response.xpath('//a[@class="nav next ui_button primary"]/@href').extract_first()
            yield response.follow(url=next_page_url, callback=self.parse)

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

        yield review_item   
    

    