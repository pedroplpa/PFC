import json
import requests
import datetime
import os

#Imports the shared HTML Parser
import sys
from ..shared.parser import HTMLTargetParser
from ..shared.parser import HTMLForm

#Method for askink an user-informed cookie
def getSessionWithCookie(session,url):
    print("Inform the cookie")
    cookie = input()
    session.headers.update({'cookie':cookie})
    return session

#Testing for any redirects in the response
def testAndGetSession(session,url):
    x = session.get(url)
    if x.history is not []:
        print ("[!] It seems the URL is being redirected ("+str(x.history)+")")
        print ("Redirection URL: " + x.url)
        print ("If a login is required, then is recommended to inform a cookie for the session")
        print ("Do you want to follow the redirect URL or inform a cookie? (f/c)")
        ans = input()
        if str.lower(ans) == "c":
            session = getSessionWithCookie(session,url)
        elif str.lower(ans) == "f":
            print("[+] Following URL")
        else:
            print("[!] Invalid answer, following the redirect URL")
    return session

#Method for creating the results file for documenting all errors detected
def createResultsFile(fileName,url,report):
    date = datetime.datetime.now()
    resultFileName = fileName+"_result"+".json"
    resultsFile = open(resultFileName,'w')
    report["title"] = "Test sql from date: " + str(date.strftime("%Y-%m-%d %H:%M:%S")) + " on the url: " + url
    return resultsFile

#Dumping all the report fields into the JSON file
def closeResultsFile(resultsFile,report):
    date = datetime.datetime.now()
    report["result"]["finish-date"] = date.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(report,resultsFile)
    resultsFile.close()

#Method for logging into the application and creating a Session for accessing the 
#different vulnerable pages in the bWAPP server for demonstration and testing
def loginIntoBWAPPApplication(loginUrl,timeout = 3):
    try:
        session = requests.Session()
        loginPayload = {'login':'bee','password':'bug','security_level':'0','form':'submit'}
        login = session.post(loginUrl, data=loginPayload,timeout = timeout)
    except requests.Timeout:
        raise Exception("[-] Login request timeout") 
    return session
    
#Method for parsing the web page and finding all HTML forms 
def parseHtmlPage(url,session):
    try:
        r = session.get(url,timeout = 3)
        print ("[+] Response received. Parsing HTML Document in order to detect FORMS")
        targetParser = HTMLTargetParser()
        targetParser.feed(r.text)
        if not targetParser.formList:
            raise Exception("[-] The given URL had no forms for targetting")
    except requests.Timeout:
        raise Exception("[-] Request for page timeout")
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
    os.makedirs(os.path.dirname(fileName),exist_ok=True)
    f = open(fileName,'w')
    f.write(s.text)
    f.close()

def errorBasedSQLStrategy (url,session, dataValues,requestType):
    timeout = 4
    result = False
    messageList=[]
    try:
        if (requestType == 'POST'):
            s = session.post(url, data = dataValues,timeout = timeout)  
        if (requestType == 'GET'):
            s = session.get(url, params = dataValues,timeout = timeout)
    except requests.Timeout:
        print ("[-] Request timeout")
        return
    with open(os.path.dirname(__file__) + "/sql_error_check","r") as checkFile:
        checkLines = checkFile.readlines()
        for line in checkLines:
            if line.rstrip() in str.lower(s.text):
                print ("[-] Detected \"" + line.rstrip() + "\" in the response, possible sql error-based vulnerability")
                messageList.append(line.rstrip())
                result = True
    if not result:
        print ("[-] No errors detected")
    return result,messageList

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
