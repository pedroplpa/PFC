from .userlib import *
from collections import OrderedDict

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
        for id in idList:
            report["result"]["vulnerabilities"]["form-"+str(id)]=OrderedDict()
            report["result"]["vulnerabilities"]["form-"+str(id)]["reflected"]=OrderedDict()
            form = targetFormList[id]
            dataValues = createDictionary(form,nonMaliciousValue)
            filePath = attemptsFolder + filePrefix + str(id) + nonMaliciousResponseFileName
            requestType = form.formType
            print("[+] Sending non malicious request for FORM #" + str(id))
            sendRequestAndSaveResponse(url,session,dataValues,requestType,filePath)

            #Set our strategy for Reflected and test for every payload
            detectedXSSReflected = False
            xssPayloadFile = open(xssPayloadFileName,encoding='ISO-8859-1')
            strategy = xssReflectedStrategy
            print("[+] Testing form " + str(id) + " for reflected XSS detection")
            for attempt,xssPayload in enumerate(xssPayloadFile.read().splitlines()):
                dataValues = createDictionary(form,xssPayload)
                print("[+] Sending request for FORM #" + str(id) + ". PAYLOAD: " + xssPayload)
                retVal = strategy(url,session,dataValues,requestType)
                #If the first field of retVal is true, then there were vulnerabilities detected
                if retVal and retVal[0]:
                    detectedXSSReflected = True
                    print ("[!] Possible reflected xss vulnerability detected for form " 
                            + str(id) + " using payload " + xssPayload)

                    report["result"]["vulnerabilities"]["form-"+str(id)]["reflected"]["payload "+xssPayload+" "]=retVal[1]
                    print ("Do you want to continue testing (y/n)?")
                    ans = input()
                    if (str.lower(ans) == "n"):
                        break
            xssPayloadFile.close()

    except Exception as e:
        print ("[-] Too many request rejected. Host probably down.")
        print (e)
        return    
    closeResultsFile(resultsFile,report)
    return 0
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