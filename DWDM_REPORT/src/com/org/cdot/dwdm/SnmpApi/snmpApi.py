'''
Created on 06-Dec-2017

@author: cdot
'''
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from PySNMP.pysnmp.hlapi import *
from src.com.org.cdot.dwdm.Attribute import Constants, GlobalVars
from pprint import pformat, pprint
from PySNMP.pysnmp.proto.errind import oidNotIncreasing
import pprint
class SNMP(object):

    def __init__(self, timeout,retries):
            self.timeout=timeout
            self.retries=retries
   
    emptyStr=""
    lst=[]

#""""""""""""""""""""""""""""""""""""""
#Function to get Nodes direction _START_
#""""""""""""""""""""""""""""""""""""""
    def snmp_get(self,ip,oid):
        #print("SNMP get request for %s"%oid)
        print ".",
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData('public', mpModel=0),
                   UdpTransportTarget((GlobalVars.gneIP1, 161),timeout=self.timeout,retries=self.retries),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
            )

        if errorIndication:
            print(errorIndication)
            return self.emptyStr,Constants.GET_REQUEST_FAILED
        elif errorStatus:
            #print('%s at %s' % (errorStatus.prettyPrint(),
                        #errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            return self.emptyStr,Constants.GET_REQUEST_FAILED
        else:  
            for varBind in varBinds:         
                return varBind[1],Constants.NO_ERROR        
            
             
#""""""""""""""""""""""""""""""""""""""
#Function to get Nodes direction _END_
#""""""""""""""""""""""""""""""""""""""              

#""""""""""""""""""""""""""""""""""""""
#Function to Set  _START_
#""""""""""""""""""""""""""""""""""""""
    def snmp_set(self,ip,oid,strVal):
        print("sending set request to %s"%ip)
        errorIndication, errorStatus, errorIndex, varBinds = next(
            setCmd(SnmpEngine(),
            CommunityData('public'),
            UdpTransportTarget((ip, 161),timeout=self.timeout,retries=self.retries),
            ContextData(),
            ObjectType(ObjectIdentity(oid),OctetString(strVal))))

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                     errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            print("Set String:%s"%varBinds)
               
#""""""""""""""""""""""""""""""""""""""
#Function to set  _END_
#""""""""""""""""""""""""""""""""""""""                 

#""""""""""""""""""""""""""""""""""""""
#Trap Receiver  _START_
#""""""""""""""""""""""""""""""""""""""
##Trap receiver              


def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    if GlobalVars.END_TRAP_LISTENER==1:
        transportDispatcher.closeDispatcher()
        transportDispatcher.jobFinished(1)
    #print('cbFun is called')
    while wholeMsg:
        #print('loop...')
        msgVer = int(api.decodeMessageVersion(wholeMsg))
        if msgVer in api.protoModules:
            pMod = api.protoModules[msgVer]
        else:
            #print('Unsupported SNMP version %s' % msgVer)
            return
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg, asn1Spec=pMod.Message(),
            )
        #print('Notification message from %s:%s: ' % (
        #    transportDomain, transportAddress
        #    )
        #)
        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        if reqPDU.isSameTypeWith(pMod.TrapPDU()):
            if msgVer == api.protoVersion1:
                #print('Enterprise: %s' % (
                #    pMod.apiTrapPDU.getEnterprise(reqPDU).prettyPrint()
                #    )
                #)
                #print('Agent Address: %s' % (
                #    pMod.apiTrapPDU.getAgentAddr(reqPDU).prettyPrint()
                #    )
                #)
                #print('Generic Trap: %s' % (
                #    pMod.apiTrapPDU.getGenericTrap(reqPDU).prettyPrint()
                #    )
                #)
                #print('Specific Trap: %s' % (
                #    pMod.apiTrapPDU.getSpecificTrap(reqPDU).prettyPrint()
                #    )
                #)
                #print('Uptime: %s' % (
                #    pMod.apiTrapPDU.getTimeStamp(reqPDU).prettyPrint()
                #   )
                #)
                varBinds = pMod.apiTrapPDU.getVarBinds(reqPDU)
            else:
                varBinds = pMod.apiPDU.getVarBinds(reqPDU)
            #print('Var-binds:')
            for oid, val in varBinds:
                #print('%s = %s' % (oid.prettyPrint(), val.prettyPrint()))                  
                #print(GlobalVars.TRAP_OID)         
                tmpOid=pprint.pformat(oid.prettyPrint())  
                tmpOid='.'+tmpOid.replace("'","")    
                
                if  tmpOid in GlobalVars.TRAP_OID:
                    print("Online Monitoring OutPut:")
                    print('%s=%s' % (oid.prettyPrint(), val.prettyPrint()))
                    
    return wholeMsg


def receive_trap(self):
    
    transportDispatcher = AsynsockDispatcher()

    transportDispatcher.registerRecvCbFun(cbFun)

    # UDP/IPv4
    transportDispatcher.registerTransport(
        udp.domainName, udp.UdpSocketTransport().openServerMode(('192.168.115.187', 162))
        )

    # UDP/IPv6
    transportDispatcher.registerTransport(
        udp6.domainName, udp6.Udp6SocketTransport().openServerMode(('::1', 162))
        )

    transportDispatcher.jobStarted(1)

    try:
        # Dispatcher will never finish as job#1 never reaches zero
        print('run dispatcher')
        transportDispatcher.runDispatcher()
    except:
        transportDispatcher.closeDispatcher()
        raise
               
#""""""""""""""""""""""""""""""""""""""
#Trap Receiver  _END_
#""""""""""""""""""""""""""""""""""""""           
    