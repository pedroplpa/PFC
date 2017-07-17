from html.parser import HTMLParser

class HTMLForm:
	formType = "GET"
	elementList = []

	def __init__(self,formType):
		self.formType = formType

	def addElement(self,tag,elementName,elementType):
		self.elementList.append([tag,elementName,elementType])

	def processElement(self,tag,attrs):
		elementName=""
		elementType="input"
		for attr in attrs:
			if (str.upper(attr[0]) == "NAME"):
				elementName = attr[1]
			if (str.upper(attr[0]) == "TYPE"):
				elementType = attr[1]
		#Ensure that the SUBMIT field will not be included in the target element list
		if (str.upper(elementType) != "SUBMIT"):
			self.addElement(tag,elementName,elementType)

class HTMLTargetParser(HTMLParser):
	#For now, let us treat only the input elements of our HTML document
	#targetTagList = ['select','input','textarea','option']
	targetTagList = ['input']
	inForm = False
	formList = []
	formObject = None
	def handle_starttag(self, tag, attrs):
		if tag in self.targetTagList:
			if self.inForm:
				self.formObject.processElement(tag,attrs)
		if tag == 'form':
			method="GET"
			for attr in attrs:
				if (str.upper(attr[0]) == "METHOD"):
					method = attr[1]
			self.formObject = HTMLForm(method)
			self.inForm = True
	def handle_endtag(self, tag):
		if tag == 'form':
			self.formList.append(self.formObject)
			self.formObject = None
			self.inForm = False