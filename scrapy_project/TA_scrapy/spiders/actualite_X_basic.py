import sys
import scrapy
import logging
import logzero
from logzero import logger

from TA_scrapy.items import XActuItem


class ActuXBasicSpider(scrapy.Spider):
    name = "actuX_basic"

    def __init__(self, *args, **kwargs):
        super(ActuXBasicSpider, self).__init__(*args, **kwargs)

        # Set logging level
        logzero.loglevel(logging.DEBUG)

        # To track the evolution of scrapping
        self.main_nb = 0
        self.article_nb = 0
        self.nb_article_max = 10 ** 10
        super().__init__(**kwargs)
        if type(self.nb_article_max) == str:
            self.nb_article_max = int(self.nb_article_max)

    def start_requests(self):
        url = 'https://www.polytechnique.edu/fr/actualités'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        logger.warn('> PARSING NEW MAIN PAGE OF ARTICLES ({})'.format(self.main_nb))
        self.main_nb += 1

        # Get the list of the articles
        xpath = '//li[contains(@class,"views-row")]'
        my_articles = response.xpath(xpath)[:-1]

        for article in my_articles:
            if self.article_nb < self.nb_article_max:
                logger.info('> PARSING NEW ARTICLE ({})'.format(self.article_nb))
                self.article_nb += 1

                # Intitiate storing object
                actu_item = XActuItem()

                # Get link of full article
                css_locator = 'div.field-items ::attr(href)'
                actu_item['lien_article'] = article.css(css_locator).extract_first()

                # Get date and title
                css_locator = 'div.field-items ::text'
                rep = article.css(css_locator).extract()
                actu_item['titre_article'] = rep[0]
                actu_item['date_article'] = rep[1]

                # Get content
                css_locator = 'p ::text'
                actu_item['content'] = article.css(css_locator).extract_first()

                # Get related subject info
                css_locator = 'strong ::text'
                subjects = article.css(css_locator).extract()
                subjects = [subject for subject in subjects if subject not in ['#', ', ']]
                actu_item['related_subject'] = subjects

                css_locator = 'strong ::attr(href)'
                actu_item['related_subject_links'] = article.css(css_locator).extract()

                yield actu_item

        # Have we reached the article limit ?
        go_on = self.article_nb < self.nb_article_max

        # Deal with next page
        css_locator = 'li.pager-next ::attr(href)'
        next_page = response.css(css_locator).extract_first()
        if next_page is not None and go_on:
            yield response.follow(next_page, callback=self.parse)
