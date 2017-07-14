from html.parser import HTMLParser
import requests
import string

class HTMLForm:
	formType = "GET"
	elementList = []
	def __init__(self,formType):
		self.formType = formType
	def addElement(self,tag,attrs):
		self.elementList.append([tag,attrs])

class HTMLTargetParser(HTMLParser):
	inForm = False
	#targetTagList = ['select','input','textarea','option']
	targetTagList = ['input']
	formList = []
	formObject = None
	def handle_starttag(self, tag, attrs):
		if tag in self.targetTagList:
			if self.inForm:
				self.formObject.addElement(tag,attrs)
			print ('Tag detected: ' + tag + ' with following attributes')
			print (attrs)
		if tag == 'form':
			print ('Form detected with following attributes:')
			print (attrs)
			method="GET"
			for attr in attrs:
				if (str.upper(attr[0]) == "METHOD"):
					method = attr[1]
					print (method)
			self.formObject = HTMLForm(method)
			self.inForm = True
	def handle_endtag(self, tag):
		if tag == 'form':
			print ('End of form')
			self.formList.append(self.formObject)
			self.formObject = None
			self.inForm = False

url = 'http://ctf.imesec.org/web-4444'
#data_values={'userName':'cebola',
#	'userPassword':'batata'}
#r = requests.post(url,data = data_values)
r = requests.get(url)
targetParser = HTMLTargetParser()
targetParser.feed(r.text)
print (str(targetParser.formList[0].elementList))