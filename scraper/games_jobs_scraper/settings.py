# Scrapy settings for games_jobs_scraper project

BOT_NAME = "games_jobs_scraper"

SPIDER_MODULES = ["games_jobs_scraper.spiders"]
NEWSPIDER_MODULE = "games_jobs_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests
DOWNLOAD_DELAY = 2

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    'games_jobs_scraper.middlewares.DuplicateFilterMiddleware': 543,
}

# Enable or disable item pipelines
ITEM_PIPELINES = {
    'games_jobs_scraper.pipelines.DataCleaningPipeline': 300,
    'games_jobs_scraper.pipelines.DuplicateDetectionPipeline': 400,
    'games_jobs_scraper.pipelines.DatabasePipeline': 500,
}

# HTTP Cache — disabled by default so the spider always fetches live data.
# Re-enable during development to avoid repeat hits: scrapy crawl hitmarker -s HTTPCACHE_ENABLED=True
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours (only used when cache is on)
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404]

# Request fingerprint to avoid re-scraping
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'

# Set settings whose default value is deprecated
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Autothrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = None  # Set to file path to redirect logs
