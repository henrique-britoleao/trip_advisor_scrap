
# Capgemini Datacamp

## Table of contents
- [Deliverable 1:](#deliverable-1-)
  * [General info](#general-info)
  * [Technologies](#technologies)
  * [Setup](#setup)
- [Deliverable 2:](#deliverable-2-)
  * [General info](#general-info-1)
  * [Technologies](#technologies-1)
  * [Setup](#setup-1)


## Deliverable 1:

### General info
Implements a spider to crawl trip advisor looking for restaurant reviews.
	
### Technologies
Project is created with:
* Python version: 3..
* Scrapy

	
### Setup
To run this project, install it locally:

```terminal
pip install -r requirements.txt
scrapy ReviewRestoTA --overwrite-output=TA_reviews/scrapped_data/scrapped_data.jl
```
Data from webscraping will be in ../trip_advisor_scrap/TA_reviews/TA_reviews/scrapped_data.

## Deliverable 2: 

### General info
Preprocessed data obtained in first part of the project. Main delivery in Deliverable.ipynb
Performed:
* Data cleaning
* Data exploration
* Tokenization, stemming, and lemmatization 


### Technologies 
* Python version: 3..
* nltk
* pycld2
* Wordcloud

### Setup
Make sure to install dependencies before running the notebook. Also make sure that the steps taken in Deliverable 1 have all been taken. 
```terminal
pip install -r requirements.txt
```
