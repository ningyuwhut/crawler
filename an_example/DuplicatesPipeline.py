#encoding=gb2312
from scrapy.exceptions import DropItem

class DuplicatesPipeline(object):
	def process_item(self, item, spider):
		if Redis.exists('url:%s' % item['url']):
			raise DropItem("Duplicate item found: %s" % item)
		else:
			Redis.set('url:%s' % item['url'],1)
			return item
