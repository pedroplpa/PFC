from html.parser import HTMLParser
import requests

class HTMLTargetParser(HTMLParser):
	inForm = False
	targetTagList = ['select','input','textarea']

	def handle_starttag(self, tag, attrs):
		if tag in self.targetTagList:
			print ('Tag detected: ' + tag + ' with following attributes')
			print (attrs)
		if tag == 'form':
			print ('Form detected with following attributes:')
			print (attrs)
			self.inForm = True
	def handle_endtag(self, tag):
		if tag == 'form':
			print ('End of form')
			self.inForm = False

url = 'http://ctf.imesec.org/web-4444'
data_values={'userName':'cebola ',
	'userPassword':'batata'}
r = requests.post(url,data = data_values)
targetParser = HTMLTargetParser()
targetParser.feed(r.text)

print (r.text)
