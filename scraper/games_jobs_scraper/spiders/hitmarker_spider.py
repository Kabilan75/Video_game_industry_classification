import scrapy
from scrapy.spiders import SitemapSpider
from games_jobs_scraper.items import JobItem
from datetime import datetime
import re

# Accept London-based and UK-remote roles only
LONDON_KEYWORDS = {'london', 'remote (uk)', 'remote (united kingdom)'}


class HitmarkerSpider(SitemapSpider):
    """
    Spider for scraping Hitmarker.net using their sitemap.
    Filters to UK-based jobs only.
    """
    name = "hitmarker"
    allowed_domains = ["hitmarker.net"]
    
    sitemap_rules = [
        ('/jobs/', 'parse_job'),
    ]
    sitemap_urls = [
        'https://hitmarker.net/sitemap-jobs.xml/p1',
    ]

    def is_london_location(self, location: str) -> bool:
        """Return True only if the location explicitly mentions London."""
        if not location:
            return False
        loc_lower = location.lower()
        return any(kw in loc_lower for kw in LONDON_KEYWORDS)

    def parse_job(self, response):
        self.logger.info(f"Parsing job: {response.url}")
        
        item = JobItem()
        item['url'] = response.url
        item['source_website'] = "hitmarker.net"
        item['scraped_date'] = datetime.now()
        
        # Title
        item['title'] = response.css('h1::text').get(default='').strip()
        
        # Company
        item['company'] = response.css('a[href^="https://hitmarker.net/companies/"] span.truncate::text').get()
        if not item['company']:
            item['company'] = response.xpath('//a[contains(@href, "/companies/")]//span/text()').get()
        if not item['company']:
            item['company'] = "Unknown Company"

        # Location
        item['location'] = response.xpath('//div[span[contains(text(), "🌎")]]/span[contains(@class, "truncate")]/text()').get()
        if not item['location']:
            item['location'] = "Remote/Unknown"
        item['location'] = item['location'].strip()

        # --- LONDON FILTER ---
        if not self.is_london_location(item['location']):
            self.logger.info(f"Skipping non-London job: {item['title']} ({item['location']})")
            return  # Drop non-London jobs


        # Description
        description_parts = response.css('.prose *::text').getall()
        item['description'] = "\n".join([p.strip() for p in description_parts if p.strip()])
        
        # Salary
        item['salary'] = response.xpath('//div[img[@alt="Salary"]]/span/text()').get()

        # Posting Date
        date_str = response.css('span[data-datetime]::attr(data-datetime)').get()
        if date_str:
            try:
                item['posting_date'] = datetime.fromisoformat(date_str)
            except ValueError:
                item['posting_date'] = datetime.now()
        else:
            item['posting_date'] = datetime.now()

        # Content hash
        import hashlib
        content_str = str(item['title']) + str(item['company']) + str(item['location'])
        item['content_hash'] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        yield item
