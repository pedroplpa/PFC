import json
import requests
from parser import HTMLForm
from parser import HTMLTargetParser

def BEGIN():
	res = ["URL"]
	return res

def RUN(file_name):
    url = 'https://ctf.imesec.org/web-4444'
    try:
        r = requests.get(url)
        targetParser = HTMLTargetParser()
        targetParser.feed(r.text)
    except Exception:
        print("[-] The URL did not respond to the request")
        exit()

    if not targetParser.formList:
        print ("[-] The given URL had no forms for POST targeting")
    else:
        for form in targetParser.formList:
            print (targetParser.formList[0].formType)
            dataValues={}
            for dataField in form.elementList:
                dataValues.update({dataField[1]:'cebola'})
                print (dataValues)
            try:
                s = requests.post(url,data = dataValues,verify = True)  
                print (s.text)
            except Exception:
                print ("[-] An error occured while trying to POST data")

RUN("mope")