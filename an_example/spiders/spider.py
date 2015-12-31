#encoding=gb2312
import scrapy
from an_example.items import Item
from scrapy.linkextractors import FilteringLinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlParserLinkExtractor
from scrapy.spiders import CrawlSpider,Rule
import parse_page
from urlparse import urlparse
import tldextract
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.response import get_base_url
from scrapy.utils.python import unique as unique_list

class AnExampleSpider(CrawlSpider):
	name="anexample"
	rules=[]
	def __init__(self, url_file ):
		data = open(url_file, 'r').readlines()
		self.allowed_domains = [ i.strip() for i in data ] 
		self.start_urls = ['http://www.' + domain for domain in self.allowed_domains]
		print "spider allowed_domain in __init__", self.allowed_domains

		self.maximumPagesPerSite=10000 #每个网站最多可以爬取的页面个数
		self.crawledPagesPerSite={}
		self.dynamic_deny_domain=[]
		link_extractor=CustomLinkExtractor(allow=r"/*.html",allow_domains=self.allowed_domains )
		rule_1=Rule(link_extractor, callback="parse_url", follow=True)
		AnExampleSpider.rules.append(rule_1)
		print "spider.rules[0] allow_domains in __init__", AnExampleSpider.rules[0].link_extractor.allow_domains
		super(AnExampleSpider, self).__init__()#*a, **kw

	def parse_url(self, response):
		url=response.url
		domain_name=tldextract.extract(url).domain
		item=Item()
		html_text=response.body
		extracted_text=parse_page.parse_page(html_text)	
		item["url"]=url
		item["extracted_text"]=extracted_text
		return item

class CustomLinkExtractor(FilteringLinkExtractor):
	def __init__(self, allow=(), deny=(), allow_domains=(), deny_domains=(), restrict_xpaths=(),
tags=('a', 'area'), attrs=('href',), canonicalize=True,
    unique=True, process_value=None, deny_extensions=None, restrict_css=()):
		tags, attrs = set(arg_to_iter(tags)), set(arg_to_iter(attrs))
		tag_func = lambda x: x in tags
		attr_func = lambda x: x in attrs
		lx = LxmlParserLinkExtractor(tag=tag_func, attr=attr_func, unique=unique, process=process_value)
		self.crawledPagesPerSite={}
		self.maximumPagesPerSite=10000 #每个网站最多可以爬取的页面个数
		super(CustomLinkExtractor, self).__init__(lx, allow=allow, deny=deny,
            allow_domains=allow_domains, deny_domains=deny_domains,
            restrict_xpaths=restrict_xpaths, restrict_css=restrict_css,
            canonicalize=canonicalize, deny_extensions=deny_extensions)

	def extract_links(self, response):
		base_url = get_base_url(response)
		print "base_url", base_url
		domain_name=tldextract.extract(base_url).domain
		if domain_name in self.crawledPagesPerSite and self.crawledPagesPerSite[domain_name]>self.maximumPagesPerSite:
			return []

		if self.restrict_xpaths:
			docs = [subdoc for x in self.restrict_xpaths for subdoc in response.xpath(x)]
		else:
			docs = [response.selector]
		all_links = []
		for doc in docs:
			links = self._extract_links(doc, response.url, response.encoding, base_url)
			all_links.extend(self._process_links(links))

		all_links=unique_list(all_links)

		new_all_links=[]

		for link in all_links:
			url=link.url
			
			domain_name=tldextract.extract(url).domain
			suffix=tldextract.extract(url).suffix
			domain_and_suffix=domain_name+"."+suffix

			if domain_and_suffix not in self.allow_domains:
				continue
				
			if domain_name in self.crawledPagesPerSite:
				self.crawledPagesPerSite[domain_name]+=1
			else:
				self.crawledPagesPerSite[domain_name]=1

			if self.crawledPagesPerSite[domain_name]>self.maximumPagesPerSite:
				break	
			else:
				print "have crawled " , self.crawledPagesPerSite[domain_name], "pages"
				new_all_links.append(link)
		return new_all_links
