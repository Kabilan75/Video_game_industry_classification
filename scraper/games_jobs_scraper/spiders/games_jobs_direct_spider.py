import scrapy
import json
import hashlib
from datetime import datetime
from games_jobs_scraper.items import JobItem

class GamesJobsDirectSpider(scrapy.Spider):
    name = "games_jobs_direct"
    allowed_domains = ["gamesjobsdirect.com"]
    # We use a comprehensive start URL list for major UK hubs + remote
    start_urls = [
        "https://www.gamesjobsdirect.com/jobs/united-kingdom",
        "https://www.gamesjobsdirect.com/jobs/london",
        "https://www.gamesjobsdirect.com/jobs/remote",
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    def parse(self, response):
        self.logger.info(f"Parsing GamesJobsDirect list: {response.url}")
        
        # Job links - typically look for /details/ or /job/ structure
        # We look for links inside job cards
        links = response.css('a[href*="/details/"]::attr(href)').getall()
        # Also try generic
        if not links:
            links = response.css('.job-title a::attr(href)').getall()
            
        links = list(set(links))
        self.logger.info(f"Found {len(links)} potential job links")

        for link in links:
            yield response.follow(link, callback=self.parse_job)
            
        # Pagination
        # Look for "Next" or page numbers
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_job(self, response):
        item = JobItem()
        item['url'] = response.url
        item['source_website'] = "gamesjobsdirect.com"
        item['scraped_date'] = datetime.now()
        
        # Attempt 1: Schema.org JSON-LD
        # This is the most reliable way if available
        json_ld = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if json_ld:
            try:
                data = json.loads(json_ld)
                # It might be a list or single object
                if isinstance(data, list):
                    data = data[0] if data else {}
                    
                if data.get('@type') == 'JobPosting':
                    item['title'] = data.get('title')
                    item['company'] = data.get('hiringOrganization', {}).get('name')
                    item['description'] = data.get('description')
                    item['posting_date'] = data.get('datePosted')
                    
                    # Location structure varies
                    loc = data.get('jobLocation', {})
                    if isinstance(loc, dict):
                         address = loc.get('address', {})
                         if isinstance(address, dict):
                             item['location'] = address.get('addressLocality') or address.get('addressRegion')
                    
                    # Initialize default dates if parsing fails later
                    if item['posting_date']:
                        try:
                            item['posting_date'] = datetime.fromisoformat(item['posting_date'])
                        except:
                            item['posting_date'] = datetime.now()
            except Exception as e:
                self.logger.warning(f"Failed to parse JSON-LD: {e}")

        # Attempt 2: CSS Selectors (Fallback)
        if not item.get('title'):
            item['title'] = response.css('h1::text').get(default='').strip()
        
        if not item.get('company'):
            item['company'] = response.css('.company-name::text').get() or "Unknown Company"
            
        if not item.get('location'):
            item['location'] = response.css('.location::text').get() or "United Kingdom"
            
        if not item.get('description'):
            desc = response.css('.job-description ::text').getall()
            item['description'] = "\n".join([d.strip() for d in desc if d.strip()])
            
        if not item.get('salary'):  # Often not in JSON-LD
             item['salary'] = response.css('.salary::text').get()

        # Defaults and cleanup
        item['title'] = item.get('title') or "Unknown Job"
        item['company'] = (item.get('company') or "Unknown Company").strip()
        item['location'] = (item.get('location') or "United Kingdom").strip()
        
        if not item.get('posting_date'):
            item['posting_date'] = datetime.now()
            
        # Hash
        content_str = str(item['title']) + str(item['company']) + str(item['location'])
        item['content_hash'] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        if item['title'] and item['title'] != "Unknown Job":
            yield item
