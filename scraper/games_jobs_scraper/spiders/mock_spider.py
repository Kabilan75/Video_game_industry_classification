import scrapy
from datetime import datetime
from games_jobs_scraper.items import JobItem

class MockSpider(scrapy.Spider):
    """
    Mock spider for testing pipeline integration.
    Yields synthetic job items with rich descriptions to test keyword extraction.
    """
    name = "mock_spider"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com"]
    
    def parse(self, response):
        """Yield mock items."""
        self.logger.info("Generating mock job listings...")
        
        # Mock Job 1: Senior Developer
        yield JobItem(
            url="http://example.com/job/1",
            title="Senior Game Developer",
            company="Mock Studio A",
            location="London",
            description="""
            We are looking for a Senior C++ Developer to join our team. 
            Experience with Unreal Engine 5 is essential. 
            You will work on AAA console games.
            Must have strong 3D math skills and knowledge of Physics Programming.
            """,
            salary="£60,000 - £80,000",
            posting_date=datetime.now(),
            source_website="mock_source",
            scraped_date=datetime.now(),
            content_hash="hash1"
        )
        
        # Mock Job 2: Junior Designer
        yield JobItem(
            url="http://example.com/job/2",
            title="Junior Level Designer",
            company="Mock Studio B",
            location="Leamington Spa",
            description="""
            Exciting opportunity for a Junior Designer.
            Proficiency in Unity and C# is required.
            Experience with Level Design and Greyboxing.
            Familiarity with Git and Jira is a plus.
            """,
            salary="£25,000 - £30,000",
            posting_date=datetime.now(),
            source_website="mock_source",
            scraped_date=datetime.now(),
            content_hash="hash2"
        )
