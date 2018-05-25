'''
Created on 07-Jan-2018

@author: root
'''
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from cProfile import label
from . form import MyForm
from django.http import HttpResponseRedirect
from src.com.org.cdot.dwdm.Attribute import GlobalVars
from twisted.protocols.dict import Definition
from src.com.org.cdot.dwdm.FunctionDef import Definitions
from time import sleep
from main import main
from django.contrib import messages
import json
def home(request):
    #homeView=template = loader.get_template("Main/index.html")
    return render(request,'Main/index.html')
def home1(request,context):
    #homeView=template = loader.get_template("Main/index.html")
    return HttpResponse("hiiiiiiiii")
def formAction(request): 
    if request.method == 'POST':
        #form = MyForm(request.POST)
        #formData=json.dumps(request.POST)
        #print(request.POST)
        formData=request.POST['formData']
        #print(formData)
        data=formData.split("&")
        #print(data[0])
        formData=data[1].split("=")
        #print(formData[1])
        
        submitbutton= request.POST.get("Submit")
        #context={'submitbutton':submitbutton,'form':form}
        
        #if form.is_valid():
        formData=data[1].split("=")
        GlobalVars.gneIP1=formData[1]
        formData=data[2].split("=")
        GlobalVars.sourceIP=formData[1]
        formData=data[3].split("=")
        GlobalVars.destIP=formData[1]
        formData=data[4].split("=")
        GlobalVars.waveLength=formData[1]
        formData=data[5].split("=")
        GlobalVars.direction=formData[1]
        formData=data[6].split("=")
        GlobalVars.interface=formData[1]
        response_data = {}
        response_data['STATUS'] = 'Fetching Data....'
        response_data['GNEIP'] = GlobalVars.gneIP1
        response_data['SOURCEIP'] = GlobalVars.sourceIP
        response_data['DESTIP'] = GlobalVars.destIP
        response_data['WAVELEN'] = GlobalVars.waveLength
        response_data['DIRECTION'] = GlobalVars.direction
        response_data['INTF'] = GlobalVars.interface
        #from threading import Thread
        #t = Thread(target=main, args=(request))
        #t.start()
            
        #messages.success(request, 'Fetching info....')
        #messages.success(request, 'Fetched...')
        #Definitions.get_set_main_function()
        return HttpResponse(json.dumps(response_data), content_type="application/json")
            
    else:
        form = MyForm()

        return render(request, 'Main/index.html',{'form':form})    