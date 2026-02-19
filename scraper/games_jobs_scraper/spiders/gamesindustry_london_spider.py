"""
Spider: gamesindustry_london — specific spider for London game jobs.
London is the largest UK game dev hub. This spider ensures deep scraping
of the London listings on gamesindustry.biz.
"""
import scrapy
import hashlib
from datetime import datetime
from games_jobs_scraper.items import JobItem


class GamesIndustryLondonSpider(scrapy.Spider):
    """
    Spider for London game industry jobs from gamesindustry.biz.
    Covers London specifically, ensuring pagination depth for the largest hub.
    """
    name = "gamesindustry_london"
    allowed_domains = ["jobs.gamesindustry.biz"]
    start_urls = [
        "https://jobs.gamesindustry.biz/jobs/london",
    ]

    def parse(self, response):
        """Parse London listing pages."""
        self.logger.info(f"Parsing London games jobs page: {response.url}")

        job_links = response.css('a.recruiter-job-link::attr(href)').getall()
        job_links = list(set(job_links))
        self.logger.info(f"Found {len(job_links)} London job links on {response.url}")

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
        """Parse individual job detail page."""
        item = JobItem()

        item['url'] = response.url
        item['source_website'] = "gamesindustry.biz"
        item['scraped_date'] = datetime.now()

        item['title'] = response.css('h1::text').get(default='').strip() or "Unknown Job Title"

        item['company'] = (
            response.css('.pane-node-recruiter-company-profile-job-organization a::text').get()
            or response.css('.recruiter-company-profile-job-organization a::text').get()
            or "Unknown Company"
        )

        item['location'] = "London, UK"  # We know this spider is London-only

        desc_parts = response.css('.field--name-body *::text').getall()
        item['description'] = "\n".join([p.strip() for p in desc_parts if p.strip()])

        item['salary'] = response.css('.field--name-field-salary-range .field__item::text').get()

        date_text = response.css('.job-published-date p::text').get()
        if date_text:
            try:
                item['posting_date'] = datetime.strptime(
                    date_text.replace("Published on", "").strip(), "%d %b %Y"
                )
            except ValueError:
                item['posting_date'] = datetime.now()
        else:
            item['posting_date'] = datetime.now()

        content_str = str(item['title']) + str(item['company']) + str(item['location'])
        item['content_hash'] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        yield item
