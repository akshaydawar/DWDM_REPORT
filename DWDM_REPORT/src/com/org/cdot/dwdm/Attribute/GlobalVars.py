'''
Created on 06-Dec-2017

@author: cdot
'''
nodeDirectionDict={}
iP2ToiP1Mapping={}
cardDetailsDict={}
dataPath=[]
dataPathHopCount=0
nodeList=[]
myList1=[]
nodeCounter=0
gneSiteName=""
gneIP1="0.0.0.0"
gneIP2="0.0.0.0"
gneIP1subStr="192.168.115."
gneIP2subStr="10.5.0"
sourceIP="0.0.0.0"
destIP="0.0.0.0"
destIP2="0.0.0.0"
waveLength=0
direction=0
interface=0
DEFAULT_STR=""
DEFAULT_IP="0.0.0.0"
END_TRAP_LISTENER=0
#---------OIDs--------------
CM_OID='.1.3.6.1.4.1.5380.3.2.5.2.'
PM_OID='1.3.6.1.4.1.5380.3.2.5.5.'
PM_TRAP_OID='.1.3.6.1.4.1.5380.3.2.5.6.'
MASTER_OID='.1.3.6.1.4.1.5380.3.2.5.9.'
DISC_OID='.1.3.6.1.4.1.5380.3.2.5.1.'
CARD_INFO_OID='.1.3.6.1.4.1.5380.3.2.5.1.'
AMPLIFIER_INFO_OID='.1.3.6.1.4.1.5380.3.2.5.2.'
TRAP_OID={}
#----------DATA TYPES for json storage----------
NODE='NODE'
TOPOLOGY='TOPOLOGY'
MPNINFO='MPNINFO'