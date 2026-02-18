"""
Spider 1: gamesindustry_uk — scrapes all UK-specific pages on gamesindustry.biz
Uses direct regional URLs (england, scotland, london, manchester) to guarantee
only UK-based jobs are collected. Reuses the same selectors as games_industry_spider.py.
"""
import scrapy
import hashlib
from datetime import datetime
from games_jobs_scraper.items import JobItem


UK_START_URLS = [
    "https://jobs.gamesindustry.biz/jobs/united-kingdom",
    "https://jobs.gamesindustry.biz/jobs/england",
    "https://jobs.gamesindustry.biz/jobs/london",
    "https://jobs.gamesindustry.biz/jobs/scotland",
    "https://jobs.gamesindustry.biz/jobs/manchester",
    "https://jobs.gamesindustry.biz/jobs/edinburgh",
    "https://jobs.gamesindustry.biz/jobs/bristol",
    "https://jobs.gamesindustry.biz/jobs/remote",   # has many UK-remote roles
]


class GamesIndustryUKSpider(scrapy.Spider):
    """
    Spider focused exclusively on UK game industry jobs from gamesindustry.biz.
    Starts from UK-region-specific URLs so only UK listings are crawled.
    """
    name = "gamesindustry_uk"
    allowed_domains = ["jobs.gamesindustry.biz"]
    start_urls = UK_START_URLS

    def parse(self, response):
        """Parse a UK region listing page."""
        self.logger.info(f"Parsing UK region page: {response.url}")

        job_links = response.css('a.recruiter-job-link::attr(href)').getall()
        job_links = list(set(job_links))
        self.logger.info(f"Found {len(job_links)} job links on {response.url}")

        for link in job_links:
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.parse_job)

        # Pagination
        next_page = response.css('li.pager-next a::attr(href)').get()
        if not next_page:
            next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_job(self, response):
        """Parse individual job page — identical selectors to games_industry_spider."""
        item = JobItem()

        item['url'] = response.url
        item['source_website'] = "gamesindustry.biz"
        item['scraped_date'] = datetime.now()

        # Title
        item['title'] = response.css('h1::text').get(default='').strip() or "Unknown Job Title"

        # Company
        item['company'] = (
            response.css('.pane-node-recruiter-company-profile-job-organization a::text').get()
            or response.css('.recruiter-company-profile-job-organization a::text').get()
            or "Unknown Company"
        )

        # Location
        item['location'] = (
            response.css('.pane-node-field-job-region .field__item::text').get()
            or response.css('.node__location::text').get()
            or "United Kingdom"
        )
        item['location'] = item['location'].strip()

        # Description
        desc_parts = response.css('.field--name-body *::text').getall()
        item['description'] = "\n".join([p.strip() for p in desc_parts if p.strip()])

        # Salary
        item['salary'] = response.css('.field--name-field-salary-range .field__item::text').get()

        # Posting Date
        date_text = response.css('.job-published-date p::text').get()
        if date_text:
            date_str = date_text.replace("Published on", "").strip()
            try:
                item['posting_date'] = datetime.strptime(date_str, "%d %b %Y")
            except ValueError:
                item['posting_date'] = datetime.now()
        else:
            item['posting_date'] = datetime.now()

        # Content hash
        content_str = str(item['title']) + str(item['company']) + str(item['location'])
        item['content_hash'] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        yield item
