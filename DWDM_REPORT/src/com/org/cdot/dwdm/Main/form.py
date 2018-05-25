'''
Created on 08-Jan-2018

@author: root
'''
from django import forms
from cProfile import label

class MyForm(forms.Form):
    GNEIP=forms.CharField(max_length=15,label='GNE IP')
    SIP=forms.CharField(max_length=15,label='Source IP')
    DESTIP=forms.CharField(max_length=15,label='Destination IP')
    WAVELEN=forms.IntegerField(label='Wavelength')
    DIRECTION=forms.IntegerField(label='Direction')
    INTERFACE=forms.IntegerField(label='Interface')