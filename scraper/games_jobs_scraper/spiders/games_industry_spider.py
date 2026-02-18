import scrapy
from datetime import datetime
from games_jobs_scraper.items import JobItem
import re

class GamesIndustrySpider(scrapy.Spider):
    """
    Spider for scraping GamesIndustry.biz job board.
    Target URL: https://jobs.gamesindustry.biz/jobs
    """
    name = "games_industry"
    allowed_domains = ["jobs.gamesindustry.biz"]
    start_urls = ["https://jobs.gamesindustry.biz/jobs"]
    
    def parse(self, response):
        """Parse the main jobs list page."""
        self.logger.info(f"Parsing main page: {response.url}")
        
        # Select all job links using the class found in HTML
        job_links = response.css('a.recruiter-job-link::attr(href)').getall()
        
        # Deduplicate links found on page
        job_links = sorted(list(set(job_links)))
        
        self.logger.info(f"Found {len(job_links)} job links")
        
        for link in job_links:
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.parse_job)
            
        # Pagination
        # Look for "next" page link
        next_page = response.css('li.pager-next a::attr(href)').get()
        if not next_page:
             next_page = response.css('a[rel="next"]::attr(href)').get()
            
        if next_page:
            self.logger.info(f"Following pagination to: {next_page}")
            yield response.follow(next_page, callback=self.parse)
            
    def parse_job(self, response):
        """Parse individual job details."""
        item = JobItem()
        
        item['url'] = response.url
        item['source_website'] = "gamesindustry.biz"
        item['scraped_date'] = datetime.now()
        
        # Title (from h1)
        item['title'] = response.css('h1::text').get(default='').strip()
        
        # Ensure title is not empty
        if not item['title']:
            item['title'] = "Unknown Job Title"

        # Company
        # Selector: .pane-node-recruiter-company-profile-job-organization a
        item['company'] = response.css('.pane-node-recruiter-company-profile-job-organization a::text').get()
        if not item['company']:
             # Fallback
             item['company'] = response.css('.recruiter-company-profile-job-organization a::text').get()
             
        # Ensure company is not empty
        if not item['company']:
            item['company'] = "Unknown Company"
            
        # Location
        # Selector: .pane-node-field-job-region .field__item
        item['location'] = response.css('.pane-node-field-job-region .field__item::text').get()
        if not item['location']:
             # Fallback
             item['location'] = response.css('.node__location::text').get(default="Remote/Unknown")
        item['location'] = item['location'].strip()
        
        # Description
        # Selector: .field--name-body (contains all description text)
        description_parts = response.css('.field--name-body *::text').getall()
             
        item['description'] = "\n".join([p.strip() for p in description_parts if p.strip()])
        
        # Salary (often missing but check)
        item['salary'] = response.css('.field--name-field-salary-range .field__item::text').get()
        
        # Posting Date
        # Selector: .job-published-date p::text ("Published on 11 Feb 2026")
        date_text = response.css('.job-published-date p::text').get()
        if date_text:
            date_str = date_text.replace("Published on", "").strip()
            try:
                # Try parsing "16 Feb 2026"
                item['posting_date'] = datetime.strptime(date_str, "%d %b %Y")
            except ValueError:
                item['posting_date'] = datetime.now()
        else:
            item['posting_date'] = datetime.now()
            
        # Generate content hash
        import hashlib
        content_str = str(item['title']) + str(item['company']) + str(item['location'])
        item['content_hash'] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
        
        yield item
