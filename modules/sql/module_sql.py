from userlib import *

def BEGIN():
	res = ["URL"]
	return res

def RUN(file_name):
    loginUrl ='http://192.168.0.43/bWAPP/login.php'
    url = 'http://192.168.0.43/bWAPP/sqli_1.php'
    nonMaliciousValue='cebola'
    attemptsFolder='attempts/'
    filePrefix = 'form-'
    nonMaliciousResponseFileName = '-nonMaliciousAttempt'
    maliciousResponseFileName = '-attempt-'
    errorBasedPayloadFile='payloads/error_based'
    timeBasedPayloadFile='payloads/time_based'

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

        errorPayloadFile = open(errorBasedPayloadFile,'r')
        strategy = errorBasedSQLStrategy
        print("[+] Testing form " +str(id)+ "for error-based SQL injection detection")
        for attempt,errorPayload in enumerate(errorPayloadFile.read().splitlines()): 
            dataValues = createDictionary(form,errorPayload)
            print("[+] Sending request for FORM #" + str(id) + ". PAYLOAD: " + errorPayload)
            if errorBasedSQLStrategy(url,session,dataValues,requestType):
                print ("[!] Possible error-based vulnerability detected for form " 
                        + str(id) + " using payload " + errorPayload)
                print ("Do you want to continue testing (y/n)?")
                ans = input()
                if (str.lower(ans) == "n"):
                    break
        errorPayloadFile.close()


        #payloadFile = open(payloadFileName,'r')
        #for attempt,payload in enumerate(payloadFile.read().splitlines()): 
        #    dataValues = createDictionary(form,payload)
        #    filePath = attemptsFolder + filePrefix+ str(id) + maliciousResponseFileName + str(attempt)
        #    requestType=form.formType
        #    print("[+] Sending request for FORM #" + str(id) + ". PAYLOAD: " + payload)
        #    sendRequestAndSaveResponse(url,session,dataValues,requestType,filePath)
        #payloadFile.close()
        #print("[+] Finished all requests for FORM #" + str(id))

RUN("")