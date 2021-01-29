# Restaurant Review Scraping

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
Implements a spider to crawl trip advisor looking for restaurant reviews.
	
## Technologies
Project is created with:
* Python version: 3..
* Scrapy

	
## Setup
To run this project, install it locally:

```terminal
pip install -r requirements.txt
scrapy ReviewRestoTA --overwrite-output=TA_reviews/scrapped_data/scrapped_data.jl
```
Data from webscraping will be in ../trip_advisor_scrap/TA_reviews/TA_reviews/scrapped_data.
