from .userlib import *
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options



def BEGIN():
    res = ["URL"]
    return res

def RUN(fileName):
    #The report is an Ordered Dictionary for storing all relevant results for writing the JSON report
    report = OrderedDict()
    with open(fileName + ".json", "r") as inputData:
        parameters = json.load(inputData)
    url = parameters["URL"]
    resultsFile = createResultsFile(fileName,url,report)
    report["result"] = OrderedDict()
    ip=url.split('/')
    loginUrl ='http://'+ ip[2] +'/bWAPP/login.php'
    nonMaliciousValue='cebola'
    attemptsFolder = os.path.dirname(__file__) + '/attempts/'
    filePrefix = 'form-'
    nonMaliciousResponseFileName = '-nonMaliciousAttempt'
    xssPayloadFileName = os.path.dirname(__file__) + '/payloads/xss_payloads'
    #errorBasedPayloadFileName =os.path.dirname(__file__) + '/payloads/error_based'
    #timeBasedPayloadFileName=os.path.dirname(__file__) + '/payloads/time_based'
    try:
        #session = loginIntoBWAPPApplication(loginUrl)
        session = requests.Session()
        testAndGetSession(session,url)
    except Exception as e:
        print (e)
        return
    print ("[+] Sending request for the URL web page")
    try:
        targetParser = parseHtmlPage(url,session)
        #print ("target parser: " + list(targetParser))
    except Exception as e:
        print (e)
        return
    targetFormList = targetParser.formList
    print ("[+] Parsing completed")

    print ("[+] The following FORMS were found in the HTML document:")
    reportFormList = []
    #print ("formList: " + str(targetParser.formList))
    for index,form in enumerate(targetParser.formList):
        dataValues = createDictionary(form)
        requestType = form.formType
        print (" ID: #" + str(index) + " : " + requestType + " form with the following fields:")
        print (dataValues)
        reportFormList.append({str(index):str(dataValues)})
    report["result"]["forms-detected"] = reportFormList

    print ("Which of the forms will be tested? (space-separated ID list) or (all)")
    options = input()

    if str.lower(options) != 'all':
        idList = [int(i) for i in options.split()]
    else:
        idList = list(range(0,len(targetFormList)))

    report["result"]["forms-tested"] = str(idList) 
    report["result"]["vulnerabilities"]=OrderedDict()
    try:
        print("[+] Opening test browser window")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(os.path.dirname(__file__) + '/chromedriver',chrome_options=chrome_options)  # Optional argument, if not specified will search path.
        for id in idList:
            report["result"]["vulnerabilities"]["form-"+str(id)]=OrderedDict()
            report["result"]["vulnerabilities"]["form-"+str(id)]["reflected"]=OrderedDict()
            report["result"]["vulnerabilities"]["form-"+str(id)]["stored"]=OrderedDict()

            form = targetFormList[id]
            dataValues = createDictionary(form,nonMaliciousValue)
            filePath = attemptsFolder + filePrefix + str(id) + nonMaliciousResponseFileName
            requestType = form.formType
            print("[+] Sending non malicious request for FORM #" + str(id))
            sendRequestAndSaveResponse(url,session,dataValues,requestType,filePath)

            #Set our strategy for Reflected and test for every payload
            xssPayloadFile = open(xssPayloadFileName,encoding='ISO-8859-1')
            strategy = xssReflectedStrategy
            print("[+] Testing form " + str(id) + " for reflected XSS detection")
            for attempt,xssPayload in enumerate(xssPayloadFile.read().splitlines()):
                dataValues = createDictionary(form,xssPayload)
                print("[+] Sending request for FORM #" + str(id) + ". PAYLOAD: " + xssPayload)
                retVal = strategy(url,session,dataValues,requestType,driver)
                #If the first field of retVal is true, then there were vulnerabilities detected
                if retVal and retVal[0]:
                    print ("[!] Possible reflected xss vulnerability detected for form " 
                            + str(id) + " using payload " + xssPayload)

                    report["result"]["vulnerabilities"]["form-"+str(id)]["reflected"]["payload "+xssPayload+" "]=retVal[1]
                    print ("[!] Sending non-malicious request to check for stored xss as well")
                    dataValues = createDictionary(form,nonMaliciousValue)
                    print("[+] Sending non-malicious request for FORM #" + str(id) + ".")
                    retVal = strategy(url,session,dataValues,requestType,driver)
                    #If the first field of retVal is true, then there were vulnerabilities detected
                    if retVal and retVal[0]:
                        detectedXSSStored = True
                        print ("[!] Possible stored xss vulnerability detected for form " 
                            + str(id) + " using payload " + xssPayload)
                        report["result"]["vulnerabilities"]["form-"+str(id)]["stored"]["payload "+xssPayload+" "]=retVal[1]
                    else:
                        print ("[!] Possible reflected xss vulnerability detected")
                        print ("[!] No stored xss found")
                break

    except Exception as e:
        print ("[-] An error has occurred!")
        return
    xssPayloadFile.close()
    closeResultsFile(resultsFile,report)
    driver.close()
    input("Press enter to continue...")
    return 
        #payloadFile = open(payloadFileName,'r')
        #for attempt,payload in enumerate(payloadFile.read().splitlines()): 
        #    dataValues = createDictionary(form,payload)
        #    filePath = attemptsFolder + filePrefix+ str(id) + maliciousResponseFileName + str(attempt)
        #    requestType=form.formType
        #    print("[+] Sending request for FORM #" + str(id) + ". PAYLOAD: " + payload)
        #    sendRequestAndSaveResponse(url,session,dataValues,requestType,filePath)
        #payloadFile.close()
        #print("[+] Finished all requests for FORM #" + str(id))

#RUN("")