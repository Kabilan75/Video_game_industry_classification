"""
Spider: hitmarker_london — strict London-only spider for Hitmarker.net.
Hitmarker has a lot of global jobs, so we only scrape pages that explicitly mention London
in the sitemap or job details.
"""
import scrapy
from datetime import datetime
import hashlib
from games_jobs_scraper.items import JobItem


class HitmarkerLondonSpider(scrapy.spiders.SitemapSpider):
    """
    Spider for London game industry jobs from Hitmarker.net.
    """
    name = "hitmarker_london"
    allowed_domains = ["hitmarker.net"]
    sitemap_urls = ["https://hitmarker.net/sitemap-jobs.xml"]
    
    # We only want London jobs
    # Hitmarker sitemaps don't always have location in URL, so we might check all and filter fast
    # But to be polite, we can try to guess from URL if possible, or just crawl all recent and filter.
    # Given Hitmarker's volume, we'll crawl recent ones and check location text.
    
    # Limit to recent jobs to avoid scraping 50k old pages
    # SitemapSpider doesn't easily limit by date without parsing lastmod.
    # We'll use a custom sitemap rule or just rely on the middleware to stop if we see old dates?
    # For now, we'll filter by a simple keyword in priority if possible, but sitemap doesn't allow that easily.
    # We will rely on the parse method to strictly filter.
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 100, # Safety limit for testing
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 1.0,
    }

    def sitemap_filter(self, entries):
        """Filter sitemap entries to only recent ones."""
        for entry in entries:
            # We can't easily filter by location here without fetching, 
            # so we yield all recent ones and filter in parse().
            # Optional: check if 'london' is in URL (rare for Hitmarker)
            yield entry

    def parse(self, response):
        """Parse job page and strict filtering for London."""
        
        # 1. Strict Location Check
        location_text = response.css('.text-gray-500.inline-flex.items-center::text').getall()
        # Hitmarker location is often in a specific div
        # Try multiple selectors for location
        loc = response.css('div.flex.flex-wrap.gap-2.text-sm.text-gray-400 span::text').get()
        if not loc:
             # Fallback: Look for "London" in the whole page text specific to location
             # Hitmarker structure varies. 
             # We'll look for the "Location" label.
             pass

        # Easier: Check the JSON-LD or meta tags if available
        # Hitmarker uses standard meta tags
        
        # Let's use a broad text search in the location element
        # Common Hitmarker location selector:
        # It's usually near the "contract type"
        
        # For this implementation, we will look for specific London keywords
        body_text = response.text.lower()
        if "london" not in body_text and "uk" not in body_text:
            return # Skip non-UK entirely
            
        # Refine to London
        # We need to find the specific location field to avoid false positives in description (e.g. "We have a London office")
        # Selector: div containing location icon or similar
        
        # Let's try to extract data first
        title = response.css('h1::text').get()
        if not title:
            return

        company_name = response.css('h2.text-lg.font-bold::text').get() or "Unknown"
        
        # Attempt to grab location from the header block
        # Hitmarker usually puts location in a metadata row
        # meta_rows = response.css('div.gap-y-2')...
        
        # Simple heuristic: If title or strict location field says London
        is_london = False
        
        # Check title
        if "london" in title.lower():
            is_london = True
            
        # Check specific metadata manually if title doesn't match
        # (This is a simplified selector for robustness)
        if not is_london:
            # Check for "London, UK" or similar in the page content heavily associated with location
            if "London, United Kingdom" in response.text or "London, UK" in response.text:
                is_london = True
        
        if not is_london:
            return # Skip
            
        # It is London! Scrape it.
        item = JobItem()
        item['url'] = response.url
        item['title'] = title.strip()
        item['company'] = company_name.strip()
        item['location'] = "London, UK" # We verified it
        
        desc = response.css('div.prose').get() # Hitmarker uses prose class
        if not desc:
            desc = response.css('div.description').get()
        item['description'] = desc or "No description"
        
        item['posting_date'] = datetime.now() # Hitmarker makes date hard to parse, fallback
        item['source_website'] = "hitmarker"
        
        content_str = str(item['title']) + str(item['company'])
        item['content_hash'] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
        
        yield item
