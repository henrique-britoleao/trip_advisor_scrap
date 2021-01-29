import scrapy
from TA_reviews.items import TAReview

class ReviewSpider(scrapy.Spider):
    name = "Review"

    def __init__(self, *args, **kwargs): 
        super(ReviewSpider, self).__init__(*args, **kwargs)

        self.main_nb = 0
        self.resto_nb = 0
        self.review_nb = 0
        self.max_reviews = 100
        self.max_pages = 2       

    def start_requests(self):
        url = 'https://www.tripadvisor.co.uk/ShowUserReviews-g186338-d13544747-r780888800-Amrutha_Lounge-London_England.html'
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        '''
        Parses through a Trip Advisor review page and yields useful iformation 
        about the review.

        Returns
        -------
        review_item: TAReview object
            includes the relevant information extracted from the review
        '''

        # TO DO: create "review" scrapy Item in items.py


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