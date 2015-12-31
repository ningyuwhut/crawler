#encoding=gbk
import random
import base64
#from settings import PROXIES
from config import pool
import redis
from scrapy.exceptions import IgnoreRequest
import tldextract
from urlparse import urlparse
class DenySomeDomainNameDownloaderMiddleware(object):
	def __init__(self, denyDomainName):
		self.denyDomainList=[]
		denyDomainNameFile=file(denyDomainName,"r")
		for line in denyDomainNameFile:
			self.denyDomainList.append(line.strip())
		print "denyDomainList", self.denyDomainList

	@classmethod
	def from_crawler(cls, crawler):
		settings = crawler.settings
		my_setting = settings.get('DENYDOMAINNAME')
#		print "denyDomainName", settings['DENYDOMAINNAME']
#		print "denyDomainName", settings.get('MONGODB_COLLECTION')
#		print "denyDomainName", settings.get('DENYDOMAINNAME')
		return cls(my_setting)

	def process_request(self, request, spider):
		second_domain_name=urlparse(request.url).hostname #
		domain_name=tldextract.extract(request.url).domain
		print "second domain_name", domain_name
		print "domain_name", domain_name
		print "self.dynamic_deny_domain", spider.dynamic_deny_domain
		if second_domain_name in self.denyDomainList or domain_name in spider.dynamic_deny_domain:
			print "deny_url", request.url
			raise IgnoreRequest()
		
class RandomUserAgent(object):
	"""Randomly rotate user agents based on a list of predefined ones"""
	def __init__(self, agents): #USER_AGENTS
		self.agents =agents 
       # print "self.agents", self.agents

	@classmethod
	def from_crawler(cls, crawler):
#        print "user_agent", crawler.settings.getlist('USER_AGENTS')
		return cls(crawler.settings.getlist('USER_AGENTS'))

	def process_request(self, request, spider):
#		print "************************** USER AGENT" + random.choice(self.agents)
		request.headers.setdefault('User-Agent', random.choice(self.agents))
		print "request.headers", request.headers["User-Agent"]

class ProxyMiddleware(object):
    def process_request(self, request, spider):
		redis_conn = redis.StrictRedis(connection_pool=pool)
		key = "proxy_ip_ping_3" 
		timeout = 20
		proxy = getproxy(redis_conn,key)
#        if proxy['user_pass'] is not None:
#            request.meta['proxy'] = "http://%s" % proxy['ip_port']
#            encoded_user_pass = base64.encodestring(proxy['user_pass'])
#            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
#            print "**************ProxyMiddleware have pass************" + proxy['ip_port']
#        else:
		print "**************ProxyMiddleware no pass************" + proxy

		request.meta['proxy'] = "http://%s" % proxy

def getproxy(redis_conn,key):
# 根据权重获取随机代理ip, weight : [1...10]
# 代理IP在redis中以sorted set存储, weight越大,ip质量越差
	total = redis_conn.zcard(key) #key集合中的元素个数
	ips = redis_conn.zrange(key, 0, total/10*2)
	# 获取全部代理IP
	# ips = r.zrange(key, 0, -1)
#	proxies = {
#	    "http": "http://%s" % ips[random.randint(0, len(ips)-1)]
#	}
	proxies=ips[random.randint(0, len(ips)-1)]
	return proxies
