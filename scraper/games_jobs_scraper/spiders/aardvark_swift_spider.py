import scrapy
import hashlib
from datetime import datetime
from games_jobs_scraper.items import JobItem

class AardvarkSwiftSpider(scrapy.Spider):
    name = "aardvark_swift"
    allowed_domains = ["aswift.com"]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
    }


    def parse(self, response):
        self.logger.info(f"Parsing Aardvark Swift jobs page: {response.url}")
        
        # Extract job links
        # Based on the markdown, links are like https://aswift.com/job/title
        job_links = response.css('a[href*="/job/"]::attr(href)').getall()
        job_links = list(set(job_links))
        
        for link in job_links:
            if "/save_job" in link or "/apply" in link:
                continue
            yield response.follow(link, callback=self.parse_job)

        # Pagination: usually "Next" button or infinite scroll (not easily handled without JS)
        # We'll check for a simple "Next" link
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_job(self, response):
        item = JobItem()
        item['url'] = response.url
        item['source_website'] = "aswift.com"
        item['scraped_date'] = datetime.now()
        
        # Title - typical agency site structure
        item['title'] = response.css('h1::text').get(default='').strip()
        if not item['title']:
             item['title'] = response.css('.job-title::text').get(default='').strip()

        # Company - Agencies often hide this, so we default to the Agency Name if not found
        # or look for "Client" text
        item['company'] = "Aardvark Swift"
        
        # Location
        # From text like "- United Kingdom" or "- Bracknell"
        # We can look for list items or specific location classes
        loc = response.css('.job-location::text').get()
        if not loc:
             # Try generic Meta info
             loc = response.xpath('//li[contains(text(), "Location")]/following-sibling::li/text()').get()
        
        item['location'] = (loc or "United Kingdom").strip()
        
        # Description
        desc = response.css('.job-description ::text').getall()
        if not desc:
            desc = response.css('div.content ::text').getall()
        item['description'] = "\n".join([d.strip() for d in desc if d.strip()])
        
        # Salary
        # Often in a list or header
        salary = response.css('.job-salary::text').get()
        item['salary'] = (salary or "").strip()

        # Date
        # "Posted 3 months ago"
        item['posting_date'] = datetime.now() # Default to now as relative dates are hard and less precise
        
        # Hash
        content_str = str(item['title']) + str(item['company']) + str(item['location'])
        item['content_hash'] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
        
        if item['title']:
            yield item
