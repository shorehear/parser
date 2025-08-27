BOT_NAME = "vacancyparser"

SPIDER_MODULES = ["vacancyparser.spiders"]
NEWSPIDER_MODULE = "vacancyparser.spiders"
BOT_NAME = "vacancyparser"

AUTOTHROTTLE_ENABLED = True
ROBOTSTXT_OBEY=False
LOG_LEVEL="DEBUG"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
   'vacancyparser.pipelines.DatabasePipeline': 300,
}