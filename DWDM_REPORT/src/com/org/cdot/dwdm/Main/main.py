'''
Created on 06-Dec-2017

@author: cdot
'''
from src.com.org.cdot.dwdm.FunctionDef import Definitions
from src.com.org.cdot.dwdm.Attribute import GlobalVars, Constants
from src.com.org.cdot.dwdm.SnmpApi import snmpApi
import pandas as pd
from termcolor import colored
from pandas.io.json import json_normalize
#from src.com.org.cdot.dwdm.Attribute.GlobalVars import sourceIP
from multiprocessing import Process
from pandas.core.common import flatten
from _ast import Global
import thread
import time
from time import sleep
from django.http import HttpResponse
import json
def main(request):
    #snmpApi.receive_trap()
    
    givenLembdaDir=0
    Definitions.data('START','NONE',[])
    print("Starting.....")
    #dummyData={"192.168.115.12":{"CDC3":{"10.5.0.30":['1','2','3']}}}
    #listData=Definitions.printTabularData(dummyData,['IPAddress1','NODENAME','IP2','a','b','c'])
    #print(listData[0])
    #Definitions.data('MAPPING',listData)
    Definitions.log('SUCCESS','Starting.....')
    
    #print(colored("Hello world in red style!", 'red'))
    thread.start_new_thread(Definitions.get_set_main_function,(request,))
    sleep(1)
    snmpApi.receive_trap(request)
    response_data={}
    response_data['STATUS']='Completed!!'
    return HttpResponse(json.dumps(response_data),content_type="application/json")
    #Definitions.get_set_main_function()
    #while 1:
    #    pass
    
   
#if __name__=='__main__':    
#    main()    