"""
Spider: workwithindies_london — strict London-only spider.
Parses WorkWithIndies RSS and filters for London/UK matches.
"""
import scrapy
from datetime import datetime
import hashlib
from games_jobs_scraper.items import JobItem
import re

class WorkWithIndiesLondonSpider(scrapy.Spider):
    """
    Spider for London jobs from WorkWithIndies.
    """
    name = "workwithindies_london"
    allowed_domains = ["workwithindies.com"]
    start_urls = ["https://www.workwithindies.com/feed.xml"]

    def parse(self, response):
        """Parse RSS feed."""
        response.selector.register_namespace('atom', 'http://www.w3.org/2005/Atom')
        
        # Iterate over entries
        entries = response.xpath('//item') 
        if not entries:
            entries = response.xpath('//entry') # Atom support
            
        for entry in entries:
            title = entry.xpath('title/text()').get()
            link = entry.xpath('link/text()').get() or entry.xpath('link/@href').get()
            description = entry.xpath('description/text()').get() or entry.xpath('content/text()').get()
            
            if not title or not link:
                continue
                
            # RSS Title format is often: "Company is hiring a Role to work from Location"
            # We strictly look for "London" in the title string
            title_lower = title.lower()
            
            is_london = False
            if "london" in title_lower:
                is_london = True
            elif "uk" in title_lower and "remote" not in title_lower:
                # If it says "UK" but not "Remote", implies a location, might be London?
                # Safer to stick to "London" for the user's "only london" request.
                pass
                
            if not is_london:
                continue
                
            # Scrape it
            item = JobItem()
            item['url'] = link
            item['title'] = title
            item['description'] = description
            item['location'] = "London, UK"
            item['source_website'] = "workwithindies"
            item['company'] = title.split(' is hiring')[0] if ' is hiring' in title else "Indie Studio"
            item['posting_date'] = datetime.now() 
            
            # Hash
            content_str = str(item['title']) + str(item['company'])
            item['content_hash'] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
            
            yield item
