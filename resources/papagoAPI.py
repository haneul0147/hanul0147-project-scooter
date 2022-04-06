import json
import os
import sys
from config import Config
import urllib.request

def PaPago(names):
    client_id = Config.client_id
    client_secret= Config.client_secret 
  
    encText = urllib.parse.quote(names)
    data = "source=en&target=ko&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
            response_body = response.read()
            print(response_body.decode('utf-8'))
            print()
            json_dict = json.loads(response_body.decode('utf-8'))
            print(json_dict['message']['result']['translatedText'])
            transTxt = json_dict['message']['result']['translatedText']
            return transTxt
            
    else:
        return("Error Code:" + rescode)
