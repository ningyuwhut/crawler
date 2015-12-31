#encoding=gbk

from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Comment
from bs4 import Doctype
import urllib2

def walker(soup, indent, encoding):
	text=""
	if soup.name is not None:
		for child in soup.children:
			if isinstance(child, NavigableString):
				if len(child) != 1: #如何判断是否为空
					text = indent + unicode(child).encode('utf-8').strip() +"\n"
			else:
				text += walker(child, indent+"\t", encoding)
	return text

if __name__ == "__main__":

	soup = BeautifulSoup( urllib2.urlopen("http://item.jd.com/1592573020.html").read()) #open('test_html') #,fromEncoding="utf-8"
	encoding=soup.original_encoding
	print "encoding", encoding

	doctypes=soup.findAll(text=lambda text: isinstance(text, Doctype))
	[doctype.extract() for doctype in doctypes]

	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	[comment.extract() for comment in comments]

	for script in soup("script"):
		script.extract()
	for noscript in soup("noscript"):
		noscript.extract()
	for style in soup("style"):
		style.extract()
	text=walker(soup, "" , encoding)
	output=file("a", "w")
	#print text #.decode('gbk').encode('utf-8')
	output.write(text+"\n")
#	print "text", text.decode('gbk') #.encode('utf-8') #.decode('gbk').encode('utf-8') #.decode('utf-8').encode('gbk') #unicode(text).encode('utf-8')
