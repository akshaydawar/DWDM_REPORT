from django.conf.urls import include,url
from django.contrib import admin
from src.com.org.cdot.dwdm.FunctionDef import Definitions

urlpatterns = [
    url(r'^$',Definitions.get_set_main_function()),
 
]