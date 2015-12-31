# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


#class AnExamplePipeline(object):
#    def process_item(self, item, spider):
#        return item
#
import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from config import Redis
from scrapy import log
#from urlparse import urlparse
#from tld import get_tld
import tldextract

class DuplicatesPipeline(object):
	def process_item(self, item, spider):
		if Redis.exists('url:%s' % item['url']):
			raise DropItem("Duplicate item found: %s" % item['url'])
		else:
			Redis.set('url:%s' % item['url'],1)
			return item

class MongoDBPipeline(object):
	def __init__(self):
		self.connection = pymongo.MongoClient( settings['MONGODB_SERVER'], settings['MONGODB_PORT'] )

	def process_item(self, item, spider):
		domain_name=tldextract.extract(item['url']).domain
		db = self.connection[domain_name] #用域名作为
		self.collection = db[settings['MONGODB_COLLECTION']]
		valid = True
		for data in item:
			if not data:
				valid = False
				raise DropItem("Missing {0}!".format(data))
			if valid:
				if domain_name in spider.crawledPagesPerSite and spider.crawledPagesPerSite[domain_name]>spider.maximumPagesPerSite:
					return None
					
				self.collection.insert(dict(item))
				if domain_name in spider.crawledPagesPerSite:
					spider.crawledPagesPerSite[domain_name]+=1
				else:
					spider.crawledPagesPerSite[domain_name]=1
				print "crawledPagesPerSite", spider.crawledPagesPerSite[domain_name]
				print "spider.allowed_domains", spider.allowed_domains
				print "spider.maximumPagesPerSite", spider.maximumPagesPerSite
				print "domain_name", domain_name, item['url']
				if spider.crawledPagesPerSite[domain_name]>spider.maximumPagesPerSite:
					suffix=tldextract.extract(item['url']).suffix
					domain_and_suffix=domain_name+"."+suffix
					print domain_and_suffix
					if domain_and_suffix in spider.allowed_domains:
						spider.allowed_domains.remove(domain_and_suffix)
						spider.dynamic_deny_domain.append(domain_name)
						#spider.rules[0].link_extractor.allow_domains.remove(domain_and_suffix)
						spider.rules[0].link_extractor.deny_domains.add(domain_and_suffix)
					print "spider.allowed_domains", spider.allowed_domains
					return None
				log.msg("Item added to MongoDB database!",level=log.DEBUG, spider=spider)
				return item
