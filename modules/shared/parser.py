from html.parser import HTMLParser

class HTMLForm:
	def __init__(self,formType = "GET"):
		self.formType = formType
		self.elementList = []
	
	def addElement(self,tag,elementName,elementType,elementValue):
		self.elementList.append([tag,elementName,elementType,elementValue])

	def processElement(self,tag,attrs):
		tag = str.lower(tag)
		elementType = ''
		elementName = ''
		elementValue = ''
		if tag in ['input','textarea','select']:
			#Default type for input tags is text 
			if tag == 'input':
				elementType='text'
			for attr in attrs:
				if (str.lower(attr[0]) == 'name'):
					elementName = attr[1]
				if (str.lower(attr[0]) == 'type'):
					elementType = attr[1]
				if (str.lower(attr[0]) == 'value'):
					elementValue = attr[1]
			#Ensure that the INPUT submit field will not be included in the target element list
			if (str.lower(elementType) != "submit"):
				self.addElement(tag,elementName,elementType,elementValue)
		
		#Check if it is a button tag with action and search values, for composing the "ACTION" field of a request
		if tag == 'button':
			for attr in attrs:
				if (str.lower(attr[0]) == 'name'):
					elementName = attr[1]
				if (str.lower(attr[0]) == 'type'):
					elementType = attr[1]
				if (str.lower(attr[0]) == 'value'):
					elementValue = attr[1]
			if (str.lower(elementType) == "submit"): 
				self.addElement(tag,elementName,elementType,elementValue)
			
class HTMLTargetParser(HTMLParser):
	def __init__(self):
		super(HTMLTargetParser,self).__init__()
	#For now, let us treat only the input elements of our HTML document
	#targetTagList = ['select','input','textarea','option']
		self.targetTagList = ['input','button','select','textarea']
		self.inForm = False
		self.formList = []
		self.formObject = None
	
	def handle_starttag(self, tag, attrs):
		if tag in self.targetTagList:
			if self.inForm:
				self.formObject.processElement(tag,attrs)
		if tag == 'form':
			method="GET"
			action=None
			for attr in attrs:
				if (str.upper(attr[0]) == "METHOD"):
					method = str.upper(attr[1])
			self.formObject = HTMLForm(method)
			self.inForm = True

	def handle_endtag(self, tag):
		if tag == 'form':
			self.formList.append(self.formObject)
			self.formObject = None
			self.inForm = False