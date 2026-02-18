"""
Spider 3: gamesindustry_scotland — specifically targets Scottish game dev jobs.
Scotland has a thriving games scene (Dundee is known as the "birthplace of
Grand Theft Auto"). This spider covers Scotland and Edinburgh specifically.
"""
import scrapy
import hashlib
from datetime import datetime
from games_jobs_scraper.items import JobItem


class GamesIndustryScotlandSpider(scrapy.Spider):
    """
    Spider for Scottish game industry jobs from gamesindustry.biz.
    Covers Dundee, Edinburgh, Glasgow — key Scottish game dev cities.
    """
    name = "gamesindustry_scotland"
    allowed_domains = ["jobs.gamesindustry.biz"]
    start_urls = [
        "https://jobs.gamesindustry.biz/jobs/scotland",
        "https://jobs.gamesindustry.biz/jobs/edinburgh",
        "https://jobs.gamesindustry.biz/jobs/dundee",
        "https://jobs.gamesindustry.biz/jobs/glasgow",
    ]

    def parse(self, response):
        """Parse Scotland/Edinburgh/Dundee region listing pages."""
        self.logger.info(f"Parsing Scottish games jobs page: {response.url}")

        job_links = response.css('a.recruiter-job-link::attr(href)').getall()
        job_links = list(set(job_links))
        self.logger.info(f"Found {len(job_links)} Scottish job links on {response.url}")

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

        item['location'] = (
            response.css('.pane-node-field-job-region .field__item::text').get()
            or response.css('.node__location::text').get()
            or "Scotland, UK"
        )
        item['location'] = item['location'].strip()

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
