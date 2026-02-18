"""
Scrapy Item definitions.
Define the data structure for scraped job listings.
"""

import scrapy


class JobItem(scrapy.Item):
    """Job listing item."""
    
    url = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    salary = scrapy.Field()
    posting_date = scrapy.Field()
    source_website = scrapy.Field()
    scraped_date = scrapy.Field()
    content_hash = scrapy.Field()
    keywords = scrapy.Field()  # Dict of extracted keywords
