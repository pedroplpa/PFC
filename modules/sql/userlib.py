import json
import requests
import datetime
from .parser import HTMLForm
from .parser import HTMLTargetParser

#Method for creating the results file for documenting all errors detected
def createResultsFile():
    date = datetime.datetime.now()
    resultsFile = open("results/report",'w')
    resultsFile.writelines("Testing starting at %s \n" %date)
    return resultsFile

def closeResultsFile(resultsFile):
    date = datetime.datetime.now()
    resultsFile.writelines("Testing finished at %s \n" %date)

#Method for logging into the application and creating a Session for accessing the 
#different vulnerable pages in the bWAPP server for demonstration and testing
def loginIntoBWAPPApplication(loginUrl,timeout = 3):
    try:
        session = requests.Session()
        loginPayload = {'login':'bee','password':'bug','security_level':'0','form':'submit'}
        login = session.post(loginUrl, data=loginPayload,timeout = timeout)
    except requests.Timeout:
        print ("[-] Login request timeout")
        exit()
    return session
    
#Method for parsing the web page and finding all HTML forms 
def parseHtmlPage(url,session):
    try:
        r = session.get(url,timeout = 3)
        print ("[+] Response received. Parsing HTML Document in order to detect FORMS")
        targetParser = HTMLTargetParser()
        targetParser.feed(r.text)
        if not targetParser.formList:
            print ("[-] The given URL had no forms for targetting")
            exit()
    except requests.Timeout:
        print ("[-] Request for page timeout")
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

def sendRequestAndSaveResponse(url,session,dataValues,requestType,fileName,timeout = 3):
    try:
        if (requestType == 'POST'):
            s = session.post(url, data = dataValues,timeout = timeout)  
        if (requestType == 'GET'):
            s = session.get(url, params = dataValues,timeout = timeout)
    except requests.Timeout:
        print ("[-] Request timeout")
        return
    f = open(fileName,'w')
    f.write(s.text)
    f.close()

def errorBasedSQLStrategy (url,session, dataValues,requestType):
    timeout = 4
    result = False
    timeout = 3
    try:
        if (requestType == 'POST'):
            s = session.post(url, data = dataValues,timeout = timeout)  
        if (requestType == 'GET'):
            s = session.get(url, params = dataValues,timeout = timeout)
    except requests.Timeout:
        print ("[-] Request timeout")
        return
    with open("sql_error_check.txt","r") as checkFile:
        checkLines = checkFile.readlines()
        for line in checkLines:
            if line.rstrip() in str.lower(s.text):
                print ("[-] Detected \"" + line.rstrip() + "\" in the response, possible sql error-based vulnerability")
                result = True
    if not result:
        print ("[-] No errors detected")
    return result

def timeBasedBlindSQLStrategy (url,session,dataValues,requestType):
    #Defining the first timeout as 5 seconds
    timeout = 5
    retValue = False
    try:
        if (requestType == 'POST'):
            s = session.post(url, data = dataValues,timeout = timeout)  
        if (requestType == 'GET'):
            s = session.get(url, params = dataValues,timeout = timeout)
    except requests.Timeout:
        #If the request timeouts, increase the timeout value to 10 seconds to ensure it is not a false positive
        print ("[+] Possible time-based SQL injection vulnerability detected. Setting timeout for 10 seconds to reduce the chance of false-positive")
        timeout = 10
        print ("[+] Sending a new request to check if the server is OK.")
        try:
            if (requestType == 'POST'):
                    s = session.post(url,timeout = timeout)  
            if (requestType == 'GET'):
                    s = session.get(url,timeout = timeout)
            try:
                print ("[+] Server is OK. Trying a new request to check ")
                if (requestType == 'POST'):
                    s = session.post(url, data = dataValues,timeout = timeout)  
                if (requestType == 'GET'):
                    s = session.get(url, params = dataValues,timeout = timeout)
            except requests.Timeout:
                print ("[+] Timeout reached, possible vulnerability detected. Yay!")
                retValue = True
                return retValue
        except requests.Timeout:
            print ("[-] Timeout reached, it seems that server crashed. Try again later.")
            return retValue
