"""
Example spider for scraping Indeed job listings.
This is a template spider - actual selectors need to be adjusted based on target website structure.
"""

import scrapy
from datetime import datetime, timedelta
from games_jobs_scraper.items import JobItem


class IndeedSpider(scrapy.Spider):
    """Spider for scraping game industry jobs from Indeed."""
    
    name = "indeed_games"
    allowed_domains = ["indeed.co.uk"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Base URL for UK game industry jobs
        self.start_urls = [
            "https://uk.indeed.com/jobs?q=game+developer&l=United+Kingdom",
            "https://uk.indeed.com/jobs?q=game+designer&l=United+Kingdom",
            "https://uk.indeed.com/jobs?q=game+programmer&l=United+Kingdom",
        ]
    
    def parse(self, response):
        """
        Parse job listing page.
        NOTE: Selectors are PLACEHOLDERS and need to be updated based on actual Indeed HTML structure.
        """
        self.logger.info(f"Parsing page: {response.url}")
        
        # Extract job cards (PLACEHOLDER SELECTOR)
        job_cards = response.css('div.job_seen_beacon')  # Example selector
        
        for job in job_cards:
            # Extract job URL
            job_url = job.css('a.jcs-JobTitle::attr(href)').get()
            if job_url:
                job_url = response.urljoin(job_url)
                yield scrapy.Request(job_url, callback=self.parse_job)
        
        # Follow pagination (PLACEHOLDER SELECTOR)
        next_page = response.css('a[aria-label="Next Page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
    
    def parse_job(self, response):
        """
        Parse individual job details page.
        NOTE: Selectors are PLACEHOLDERS and need to be updated.
        """
        item = JobItem()
        
        # Extract job details (PLACEHOLDER SELECTORS)
        item['url'] = response.url
        item['title'] = response.css('h1.jobsearch-JobInfoHeader-title::text').get()
        item['company'] = response.css('div[data-company-name="true"]::text').get()
        item['location'] = response.css('div[data-testid="job-location"]::text').get()
        item['description'] = ' '.join(response.css('div#jobDescriptionText').extract())
        item['salary'] = response.css('div#salaryInfoAndJobType::text').get()
        item['source_website'] = 'indeed'
        
        # Try to extract posting date (PLACEHOLDER)
        date_text = response.css('div.jobsearch-JobMetadataFooter::text').get()
        item['posting_date'] = self.parse_date(date_text) if date_text else None
        
        yield item
    
    def parse_date(self, date_text):
        """
        Parse relative date text (e.g., "2 days ago") to datetime.
        This is a basic implementation and needs enhancement.
        """
        if not date_text:
            return None
        
        # Handle common patterns
        if 'today' in date_text.lower():
            return datetime.now()
        elif 'yesterday' in date_text.lower():
            return datetime.now() - timedelta(days=1)
        # Add more sophisticated date parsing as needed
        
        return None
