import scrapy

def get_current_page(response):
    '''Takes request item with a restaurant page; returns the current page'''
    
    xpath = '//div[@class="pageNumbers"]/a/@class'
    first_page_class = response.xpath(xpath).extract_first()
    is_first_page = first_page_class=='pageNum first current '
    if not is_first_page:
        xpath = """//div[@class="pageNumbers"]/a[@class="pageNum current "]
                    /@data-page-number"""
        current_page = int(response.xpath(xpath).extract_first())
    else:
        current_page = 1
    
    return current_page