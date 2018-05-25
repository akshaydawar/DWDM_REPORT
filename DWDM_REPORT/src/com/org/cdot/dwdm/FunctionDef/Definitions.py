#"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Created on 06-Dec-2017
# @author: cdot
#"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#IMPORTS _START_
from src.com.org.cdot.dwdm.SnmpApi import snmpApi
from src.com.org.cdot.dwdm.Attribute import Constants
from src.com.org.cdot.dwdm.Attribute import GlobalVars
from platform import node
from pandas.io.json import json_normalize
from PySNMP.pysnmp.proto.errind import oidNotIncreasing
from django.http import HttpResponse
import pandas as pd 
import json
import os
from time import sleep
#IMPORTS _END_
#WRITE TO OUTPUT FILE _START_
def data(dataType,nodeId,data):
    script_dir = os.path.dirname(__file__)
    path= os.path.join(script_dir,'../Main/templates/Main/data.json')
    jsonObj=json.dumps(data)
    string={dataType:jsonObj}
    if dataType=='START':
        with open(path, 'w') as f:
            json.dump(string, f)
    else:   
        feeds={}  
        tmpObj={}   
        with open(path, mode='r') as feedsjson:
            #entry = {'name': '', 'url': ''}
            feeds = json.load(feedsjson)
            feedsjson.close()
            
        with open(path, mode='w') as feedsjson:
            #entry = {'name': '', 'url': ''}
            if int(nodeId)==Constants.DEFAULT:
                feeds[dataType]=jsonObj
                print('--5')
            else :
                
                if dataType in feeds.keys():
                    print('--1')
                    if(dataType==GlobalVars.NODE):
                        print('--2')
                        feeds.get(dataType)[nodeId]=jsonObj
                    elif(dataType==GlobalVars.MPNINFO):
                        feeds.MPNINFO[nodeId]=jsonObj   
                    #feeds.dataType[nodeId]=jsonObj
                else:
                    print('--3')
                    tmpObj[nodeId]=jsonObj
                    feeds[dataType]=tmpObj  
            print('--4')
            print(feeds)
            json.dump(feeds, feedsjson)
        
#WRITE TO OUTPUT FILE _END_
def update_json_file(dataType,nodeId,feeds,jsonObj):
    if(dataType==GlobalVars.NODE):
        feeds.NODE[nodeId]=jsonObj
    elif(dataType==GlobalVars.MPNINFO):
        feeds.MPNINFO[nodeId]=jsonObj   
    else:
        log('FAILURE','Unknown Data')    
    return feeds
def log(logType,log):
    script_dir = os.path.dirname(__file__)
    path= os.path.join(script_dir,'../Main/templates/Main/log.json')
    string={logType:log}
    with open(path, 'w') as f:
        json.dump(string, f)
    
#WRITE TO OUTPUT FILE _END_

#GET GNE INFO _START_
def get_gne_info(self):
    #print("Get GNE system info..")
    print("Get GNE info..")
    #response_data = {}
    endIP="1"
    retStr=get_system_info(GlobalVars.gneIP1,GlobalVars.DISC_OID+endIP+'.1.0') 
    
    if retStr==Constants.GET_REQUEST_FAILED:
        print("GNE is Not Available.")
        #response_data['STATUS'] = 'GNE is Not Reachable!'
        log('FAILED','GNE is Not Reachable!')
        #return Constants.GNE_NOT_AVAILABLE;
    else: 
        sysInfo=str(retStr).split("#")
        GlobalVars.gneSiteName=sysInfo[1]
        
        #response_data['STATUS'] = 'GNE info fetched.'
        log('SUCCESS','GNE info fetched.')
    #return HttpResponse(json.dumps(response_data),content_type="application/json")    
#GET GNE INFO _END_

#GET IP2 TO IP1 MAPPING _START_
def get_ip2_to_ip1_mapping(self):  
    #print("Get subagent info..")
    response_data={} 
    endIP='1'
    ip=GlobalVars.gneIP1
    retStr=get_subagent_info(ip,GlobalVars.MASTER_OID+endIP+'.1.0')
    
    if not retStr:
        print("Error!!!!!")
        response_data['STATUS'] = 'SubAgent info get request failed!!!.'
        log('FAILED','SubAgent info get request failed!!!.')
        #return Constants.UNABLE_TO_GET_SUBAGENTINFO;
 
    else:  
        print(str(retStr))            
        lst=str(retStr).split("#")
        
        nodeSeq=[]
        for idx,subLst in enumerate(lst[1:]):
            nodeInfo=subLst.split("-") 
            nodeSeq.append(nodeInfo[6])
        print(nodeSeq) 
        
        #------IP2 from Subagent info _START_------
        for subLst in lst[1:]:
            nodeInfo=subLst.split("-")  
            #print(subLst)
            egressNodeList=[]  
            if nodeInfo[0]==GlobalVars.gneSiteName:       
                egressNodeList=[nodeInfo[0],nodeInfo[6],'1','0']
                GlobalVars.iP2ToiP1Mapping[ip] =egressNodeList 
                egressNodeList=[nodeInfo[0],ip,'1','0']
                
            else:
                egressNodeList=[nodeInfo[0],GlobalVars.DEFAULT_STR,'','']     
            GlobalVars.iP2ToiP1Mapping[nodeInfo[6]] =egressNodeList  
        #print(GlobalVars.iP2ToiP1Mapping,)
        #------IP2 from Subagent info _END_------
        
        #------IP1 from System info _START_------   
        response_data['STATUS'] = 'System info get request failed for ' 
        for  node in nodeSeq:
                if  ip not in GlobalVars.iP2ToiP1Mapping.get(node):
                    ipSplit=node.split(".")
                    endIP=ipSplit[3]
                else:
                    endIP='1'       
                #print("node=%s,endIP=%s"% (node,endIP))
                retStr=get_system_info(GlobalVars.gneIP1,GlobalVars.DISC_OID+str(endIP)+'.1.0')
                if retStr != Constants.GET_REQUEST_FAILED:
                    str1=str(retStr).split("#")
                    #print("retStr=%s"% str(retStr))
                    #print("str1=%s"% str1[3])
                    GlobalVars.iP2ToiP1Mapping.get(node)[1]=str1[3]
                    GlobalVars.iP2ToiP1Mapping.get(node)[2]=endIP
                    GlobalVars.iP2ToiP1Mapping.get(node)[3]=str1[13]
                    if GlobalVars.iP2ToiP1Mapping.has_key(str1[3]):
                        GlobalVars.iP2ToiP1Mapping.get(str1[3])[1]=node
                        GlobalVars.iP2ToiP1Mapping.get(str1[3])[2]=endIP
                        GlobalVars.iP2ToiP1Mapping.get(str1[3])[3]=str1[13]
                    else:    
                        egressNodeList=[str1[1],node,endIP,str1[13]]   
                        GlobalVars.iP2ToiP1Mapping[str1[3]]=egressNodeList
                       
                else: 
                    print("Get system Info for %s failed"% node) 
                    log('FAILED',"Get system Info for  "+str(node)+" failed")
                    response_data['STATUS'] += str(node)+','  
         
        #------IP1 from System info _END_------  
        
        #print(GlobalVars.iP2ToiP1Mapping)
        #response_data['STATUS'] +='IP Mapping Done!!!'
        log('SUCCESS','IP Mapping Done!!!')
    #return HttpResponse(json.dumps(response_data),content_type="application/json")      
    return   GlobalVars.iP2ToiP1Mapping;      
#GET IP2 TO IP1 MAPPING _END_ 

#GET/SET MAIN FUNCTION
def get_set_main_function(self):
    givenLembdaDir=0
    #-------------------------INITIAL CONFIG _START_--------------------------------------
    get_gne_info(self)
    
    #endIP="1"
    ErrorState=get_ip2_to_ip1_mapping(self)
    if ErrorState==Constants.UNABLE_TO_GET_SUBAGENTINFO:
        print("IP Mapping is Empty.Could not fetch GNE SubAgent info..")
        log('FAILED',"IP Mapping is Empty.Could not fetch GNE SubAgent info..")
    else:
        print("\n----------------------------------------")
        print("             IP Mapping")
        print("----------------------------------------")
        printTabularData(GlobalVars.iP2ToiP1Mapping,['IPAddress1','NODE_NAME','IPAddress2','ENDIP','NODE_TYPE']) 
              
    #print("Get Topology") 
    endIP,ErrorState=get_end_ip(GlobalVars.sourceIP)
    if ErrorState==Constants.END_IP_NOT_FOUND:
        print("EndIp for %s Not Found"%GlobalVars.sourceIP)
        log('FAILED',"EndIp for "+str(GlobalVars.sourceIP)+" Not Found")
    else:                  
        ErrorState=get_node_list(GlobalVars.gneIP1,GlobalVars.MASTER_OID+str(endIP)+'.1.0')
        if ErrorState==Constants.UNABLE_TO_GET_SUBAGENTINFO:
            print("Could not fetch node list.Unable to fetch GNE Subagent info.")
            log('FAILED','Could not fetch node list.Unable to fetch GNE Subagent info.')
        else:    
            get_node_direction(GlobalVars.gneIP1,GlobalVars.MASTER_OID)
            print("\n----------------------------------------")
            print("            Network Topology   ")
            print("----------------------------------------")
            listData=printTabularData(GlobalVars.nodeDirectionDict,['Ingress_Node_IP','Direction','Egress_Node_IP'])
            #dummyData={"192.168.115.12":{"CDC3":{"10.5.0.30":['1','2','3']}}}
            #listData=printTabularData(dummyData,['IPAddress1','NODENAME','IP2','a','b','c'])
            print(listData)
            data('TOPOLOGY',str(GlobalVars.nodeCounter),listData)   
             
            topology=pd.DataFrame(GlobalVars.nodeDirectionDict)
            print("Below is the Connection Matrix:")
            log('SUCCESS','Connection Matrix fetched!')
            print(topology)
    
            if GlobalVars.iP2ToiP1Mapping.get(GlobalVars.destIP):
                if GlobalVars.iP2ToiP1Mapping.get(GlobalVars.destIP)[1]:
                    GlobalVars.destIP2=GlobalVars.iP2ToiP1Mapping.get(GlobalVars.destIP)[1]
                else:
                    print("%s Mapping Not available"%GlobalVars.destIP)
                    log('FAILED',str(GlobalVars.destIP)+' Mapping Not available')    
            else: 
                print("Destination ip %s Not available"%GlobalVars.destIP)
                log('FAILED','Destination ip ' +str(GlobalVars.destIP)+' Not available')
    #-------------------------INITIAL CONFIG _END_--------------------------------------
    
    #-----------------------------ADD _START_-------------------------------------------
            givenLembdaDir=add_node_configuration(GlobalVars.sourceIP,GlobalVars.waveLength)
    #-----------------------------ADD _END_---------------------------------------------
    
    #-----------------------------NEXT NODE _START_-------------------------------------
            nextNodeIp=get_next_node_ip(GlobalVars.sourceIP,givenLembdaDir)
    #-----------------------------NEXT NODE _END_---------------------------------------
    
    #-----------------------------PASS THROUGH _START_----------------------------------
            givenLembdaDir,prevNodeIp,nextNodeIp=pass_through_configuration(nextNodeIp,GlobalVars.sourceIP,givenLembdaDir)
    #-----------------------------PASS THROUGH _END_------------------------------------
    
    #-----------------------------NEXT NODE _START_-------------------------------------
    #nextNodeIp=Definitions.get_next_node_ip(GlobalVars.sourceIP,givenLembdaDir)
    #-----------------------------NEXT NODE _END_---------------------------------------
    
    #-----------------------------DROP _START_------------------------------------------
            drop_node_configuration(nextNodeIp,prevNodeIp,GlobalVars.waveLength)
    #-----------------------------DROP _END_--------------------------------------------
            print("DATA PATH IS:%s"%GlobalVars.dataPath)
            log('SUCCESS','DATA PATH IS: '+str(GlobalVars.dataPath))
            log('END','......ENDED......')
            print("END")
#GET/SET MAIN FUNCTION

#GET SUBAGENT INFO _START_
def get_subagent_info(ip,oid):
    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
    retStr,ErrorState=api.snmp_get(ip,oid) 
    if not retStr:
        #print("Error!!!!!")
        return Constants.GET_REQUEST_FAILED;
 
    else: 
        return retStr;
             
#GET SUBAGENT INFO _END_ 

#GET SYSTEM INFO _START_
def get_system_info(ip,oid):
    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
    retStr,ErrorState=api.snmp_get(ip,oid) 
    if not retStr:
        print("Error!!!!!")
        return Constants.GET_REQUEST_FAILED;
 
    else: 
        return retStr;
             
#GET SYSTEM INFO _END_ 


#ADD NODE CONFIGURATION _START_
def add_node_configuration(ip,waveLength):
    print("--------ADD NODE [%s] CONFIGURATION START.----------"%ip)
    log('SUCCESS','--------ADD NODE '+str(ip)+' . CONFIGURATION STARTING.----------')
    GlobalVars.nodeCounter+=1
    data('NODE',str(GlobalVars.nodeCounter),GlobalVars.iP2ToiP1Mapping.get(str(ip)))
    print(GlobalVars.iP2ToiP1Mapping.get(str(ip)))
    endIP,ErrorState=get_end_ip(ip)
    print("Get cards Info of node %s.."%ip)
    get_card_info(GlobalVars.sourceIP,GlobalVars.CARD_INFO_OID)
    fetch_mpn_configuration(ip,endIP)   
    givenLembdaDir=GlobalVars.direction
    print("givenLembdaDir MPN=%d"%int(givenLembdaDir))
    
    if givenLembdaDir!=0:
        #Get WSS Direction
        cardDetailList,wssTxDir,ErrorState=get_wss_direction_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.20',givenLembdaDir)
        if ErrorState!=Constants.EMPTY_WSS_DIR_CONFIG and ErrorState!=Constants.GIVEN_DIR_CARD_UNAVAILABLE:
            print("Direction=%d WSS cardDetailList =%d"%(int(givenLembdaDir),int(cardDetailList[0])))
            #Get WSS current Configuration
            get_wss_current_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.29.1.8.'+str(cardDetailList[0])+'.'+str(cardDetailList[1])+'.'+str(cardDetailList[2])+'.'+str(cardDetailList[3])+'.'+str(cardDetailList[4])+'.'+str(givenLembdaDir)+'.'+str(Constants.WSS_TX_DIR),waveLength)
            
        else:
            print("Wss Card List is EMPTY.May Be WSS is not Configured Properly")
    
        #Get BA INFO
        print("Get BA Configuration")
        get_pa_ba_info(ip,givenLembdaDir,Constants.BA)
        
    
    else:
        print("Unable to get Wavelength Direction.")  
    print("--------ADD NODE [%s] CONFIGURATION END.----------"%ip)      
    return   givenLembdaDir; 

#ADD NODE CONFIGURATION _END_

#PASS THROUGH CONFIGURATION _START_
def pass_through_configuration(currNodeIp,prevNodeIp,givenLembdaDir):

    ip=currNodeIp
    GlobalVars.dataPath.insert(GlobalVars.dataPathHopCount, prevNodeIp)
    nextNodeIp=currNodeIp
    recvDir=givenLembdaDir
    
    while (ip!=GlobalVars.destIP and ip!=GlobalVars.destIP2) and ip!=GlobalVars.DEFAULT_IP:
        print("Pass through configuration START")
        GlobalVars.nodeCounter+=1
        data('NODE',str(GlobalVars.nodeCounter),GlobalVars.iP2ToiP1Mapping.get(str(ip)))
        GlobalVars.dataPathHopCount+=GlobalVars.dataPathHopCount
        GlobalVars.dataPath.insert(GlobalVars.dataPathHopCount, ip)
        
        if ip !=GlobalVars.DEFAULT_IP:
            print("Get cards Info of node %s.."%ip)
            get_card_info(ip,GlobalVars.CARD_INFO_OID)
            #cardInfo=json_normalize(GlobalVars.cardDetailsDict)
            #print(cardInfo)
            endIP,ErrorState=get_end_ip(ip)
            recvDir=get_receive_direction(ip,prevNodeIp)
            #Get PA INFO
            print("Get PA Configuration")
            get_pa_ba_info(ip,recvDir,Constants.PA)
            wssTxDir=0
            #Get WSS RX Configuration
            print("Get WSS RX Configuration")
            cardDetailList,wssRxDir,ErrorState=get_wss_direction_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.20',recvDir)

            if ErrorState!=Constants.EMPTY_WSS_DIR_CONFIG and ErrorState!=Constants.GIVEN_DIR_CARD_UNAVAILABLE:
                print("Direction=%d WSS cardDetailList =%d"%(wssRxDir,int(cardDetailList[0])))
                #Get WSS current Configuration
                get_wss_current_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.29.1.8.'+str(cardDetailList[0])+'.'+str(cardDetailList[1])+'.'+str(cardDetailList[2])+'.'+str(cardDetailList[3])+'.'+str(cardDetailList[4])+'.'+str(wssRxDir)+'.'+str(Constants.WSS_RX_DIR),0)
                print("recvDir MPN=%d"%wssRxDir)  
            else:
                print("Could not fetch WSS Current Config.Wss Card List is EMPTY.")  
                print("Get WSS Channle Configuration..")
                wssTxDir=get_wss_channle_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.21.1.2.'+str(wssRxDir),GlobalVars.waveLength)
                print("wssTxDir=%d"%wssTxDir)
                
                #Get WSS channle Configuration
            if (currNodeIp in GlobalVars.iP2ToiP1Mapping):    
                if (int(GlobalVars.iP2ToiP1Mapping.get(currNodeIp)[3])> Constants.TWO_D_NODE):   
                    if int(wssTxDir)!=Constants.DEFAULT:
                        #Get WSS TX Configuration
                        print("wssTxDir=%d"%wssTxDir)
                        recvDir=wssTxDir
                        print("Get WSS TX Configuration")
                        cardDetailList,wssTxDir,ErrorState=get_wss_direction_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.20',wssTxDir)
                        if cardDetailList:
                            print("Direction=%d WSS cardDetailList =%d"%(wssTxDir,int(cardDetailList[0])))
                            #Get TX WSS current Configuration
                            get_wss_current_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.29.1.8.'+str(cardDetailList[0])+'.'+str(cardDetailList[1])+'.'+str(cardDetailList[2])+'.'+str(cardDetailList[3])+'.'+str(cardDetailList[4])+'.'+str(wssTxDir)+'.'+str(Constants.WSS_TX_DIR),0)
                            #TODO Get Channel Configuration
                        else:
                            print("Wss Card List is EMPTY.UNKNOWN TRANSMIT DIRECTION")
                            
                    else:
                        print("Transmit Direction Not Found")
                             
                else:
                    print("NON CDC NODE FOUND!!") 
                    if recvDir==1:
                        recvDir=2
                        print("Transmit Direction is %d"%recvDir)
                        
                    elif  recvDir==2:
                        recvDir=1
                        print("Transmit Direction is %d"%recvDir)
                
                #Get BA INFO
                print("Get BA Configuration")
                get_pa_ba_info(ip,recvDir,Constants.BA) 
            else:
                print("Node is Not Reachable")                  
            

        else:
            print("Next Node IP is Not Valid Exiting...")
            break;
        #Find Next Node Ip
        prevNodeIp=ip
        nextNodeIp=get_next_node_ip(ip,recvDir)
        ip=nextNodeIp
       
        print("Pass through configuration END")
    
    return recvDir,prevNodeIp,nextNodeIp;
    
#PASS THROUGH CONFIGURATION _END_


#DROP NODE CONFIGURATION _START_
def drop_node_configuration(ip,prevNodeIp,waveLength):
    print("--------DROP NODE CONFIGURATION START.----------")
    GlobalVars.nodeCounter+=1
    data('NODE',str(GlobalVars.nodeCounter),GlobalVars.iP2ToiP1Mapping.get(str(ip)))
    
    GlobalVars.dataPathHopCount+=GlobalVars.dataPathHopCount
    GlobalVars.dataPath.insert(GlobalVars.dataPathHopCount, ip)
    print("Get cards Info of node %s.."%ip)
    get_card_info(ip,GlobalVars.CARD_INFO_OID)
    #cardInfo=json_normalize(GlobalVars.cardDetailsDict)
    #print(cardInfo)
    endIP,ErrorState=get_end_ip(ip)
    recvDir=get_receive_direction(ip,prevNodeIp)
        
    if recvDir!=0:
        #Get PA INFO
        print("Get PA Configuration")
        get_pa_ba_info(ip,recvDir,Constants.PA)
        #Get WSS Direction
        cardDetailList,wssTxDir,ErrorState=get_wss_direction_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.20',recvDir)
        if ErrorState!=Constants.EMPTY_WSS_DIR_CONFIG and ErrorState!=Constants.GIVEN_DIR_CARD_UNAVAILABLE:
            print("Direction=%d WSS cardDetailList =%d"%(recvDir,int(cardDetailList[0])))
            #Get WSS current Configuration
            get_wss_current_configuration(ip,GlobalVars.CM_OID+str(endIP)+'.12.1.6.'+str(cardDetailList[0])+'.'+str(cardDetailList[1])+'.'+str(cardDetailList[2])+'.'+str(cardDetailList[3])+'.'+str(cardDetailList[4])+'.'+str(recvDir)+'.'+str(Constants.WSS_TX_DIR),waveLength)
            print("recvDir MPN=%d"%recvDir)
        else:
            print("Wss Card List is EMPTY")    
        #Get direction of Lembda from TPN configuration
        print("Get TPN Configuration")
        get_mpn_card(ip,GlobalVars.CM_OID+str(endIP)+'.12.1.6.1.0.0.0.0',waveLength,recvDir)
    else:
        print("Unable to get Wavelength Direction.")  
    
    #To Close Trap Receiver
    GlobalVars.END_TRAP_LISTENER=1    
    return HttpResponse()
    print("--------DROP NODE CONFIGURATION END.----------")      
    

#DROP NODE CONFIGURATION _END_

#GET_MPN_CONFIGURATION _START_
def fetch_mpn_configuration(ip,endIP):
    #Get TPN configuration Tx Power and Rx Power
    print("Get TPN Configuration")
    log("SUCCESS",'Get TPN Configuration...')
    mpnCard,ErrorState=get_mpn_card(ip,GlobalVars.CM_OID+str(endIP)+'.12.1.6',GlobalVars.waveLength,GlobalVars.direction)
    #print(mpnCard)
    if mpnCard:
        get_mpn_tx_power(mpnCard,endIP)
        get_mpn_sfp_status(mpnCard,endIP)
        
#GET_MPN_CONFIGURATION _END_

#NEXT NODE IP _START_
def get_next_node_ip(currNodeIp,givenLembdaDir):
    print("Get Next Node IP START")
    nextNodeIp=GlobalVars.DEFAULT_IP
    if givenLembdaDir!=Constants.DEFAULT:
        print("retrieving next node of %s in direction %s.."%(currNodeIp,givenLembdaDir)) 
        if GlobalVars.gneIP2subStr not in currNodeIp:
            currNodeIp1=GlobalVars.iP2ToiP1Mapping.get(currNodeIp)[1]
        else:
            currNodeIp1=currNodeIp
            
        nextNodeIp=GlobalVars.nodeDirectionDict.get(currNodeIp1).get(int(givenLembdaDir))
        if not nextNodeIp:
            nextNodeIp=GlobalVars.DEFAULT_IP    
        print(GlobalVars.nodeDirectionDict.get(currNodeIp1).get(int(givenLembdaDir)))
        print("Get Next Node IP END")
    return  nextNodeIp;   

#NEXT NODE IP _END_

#GET PA/BA INFO _START_
def get_pa_ba_info(currNodeIp,givenLembdaDir,amplifierType):
    cardType=Constants.AMPLIFER[0]
    cardSubType=Constants.AMPLIFER[1]
    if GlobalVars.gneIP2subStr not in currNodeIp:
        ip=GlobalVars.iP2ToiP1Mapping.get(currNodeIp)[1]
    else:
        ip=currNodeIp
            
    endIP,ErrorState=get_end_ip(currNodeIp)
    if ip in GlobalVars.cardDetailsDict:
        if str(cardType) in GlobalVars.cardDetailsDict.get(ip):
            if str(cardSubType) in GlobalVars.cardDetailsDict.get(ip).get(str(cardType)):
                cardInfo=GlobalVars.cardDetailsDict.get(ip).get(str(cardType)).get(str(cardSubType))
                for info in cardInfo:
                    rack=info[0]
                    subRack=info[1]
                    slot=info[2]
                    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
                    retStr,ErrorState=api.snmp_get(GlobalVars.gneIP1,GlobalVars.AMPLIFIER_INFO_OID+'.'+str(endIP)+'.24.1.7.'+str(rack)+'.'+str(subRack)+'.'+str(slot)+'.'+str(cardType)+'.'+str(cardSubType)+'.'+str(amplifierType)) 
                    if not retStr:
                        print("Error!!!!!")
                        continue
 
                    else: 
                        print("PA/BA info=%s"%str(retStr))
                        amplfierInfo=str(retStr).split("#")
                        if int(amplfierInfo[3])==int(givenLembdaDir):
                            print("PA/BA card info for Given Lembda=%s"%str(retStr))
            else:
                print("Card Sub Type %d Not Found.."%int(cardSubType))                 
        else:
            print("Card Type %d Not Found.."%int(cardType))                    
    else:
        print("Card info dictionary in EMPTY!!!")       
#GET PA/BA INFO _END_

#GET RECEIVE DIRECTION _START_
def get_receive_direction(currNodeIp1,prevNodeIp1):
    print("Fetching receive direction..")
    receiveDir=0
    if currNodeIp1!=GlobalVars.DEFAULT_IP and GlobalVars.gneIP2subStr not in prevNodeIp1:
        prevNodeIp=GlobalVars.iP2ToiP1Mapping.get(prevNodeIp1)[1]
    else:
        prevNodeIp=prevNodeIp1    
    
    if currNodeIp1!=GlobalVars.DEFAULT_IP and GlobalVars.gneIP2subStr not in currNodeIp1 :
        currNodeIp=GlobalVars.iP2ToiP1Mapping.get(currNodeIp1)[1]
    else:
        currNodeIp=currNodeIp1
    if  currNodeIp in   GlobalVars.nodeDirectionDict:
        for key, value in GlobalVars.nodeDirectionDict.get(currNodeIp).iteritems():
            if value==prevNodeIp:
                receiveDir=key
    else:
        print("Node Entry not available")        
    print("Receive Direction=%d"%receiveDir)        
    return receiveDir;
#GET RECEIVE DIRECTION _END_



#GET CARD INFO _START_
def get_card_info(currNodeIp,oid):
    endIP,ErrorState=get_end_ip(currNodeIp)
    oid=oid+str(endIP)+'.4.1.3.'
    for rack in range(Constants.MAX_RACKS):
        for subRack in range(Constants.MAX_SUBRACKS):
            print ". ",
            oid1=''
            oid1=oid+str(endIP)+'.4.1.3.'
            oid1=oid1+str(rack+1)+"."+str(subRack+1)
            card_info(currNodeIp,oid1,rack+1,subRack+1)
    
    print("\n------------------------------------------------------")
    print("            Rack/SubRak/Card Details Table  ")
    print("------------------------------------------------------")
    printTabularData(GlobalVars.cardDetailsDict,['NODE','CardType','CardSubType','Rack','SubRack','Slot','State','Status'])
            
    
def card_info(currNodeIp1,oid,rack,subRack):
    
    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
    retStr,ErrorState=api.snmp_get(GlobalVars.gneIP1,oid) 
    if not retStr:
        #print("Error!!!!!")
        return Constants.DEFAULT;
    
    else: 
        #ControllerCardStatus1-State1-IP1-MAC1-UUID1-SlotIndex1-CardType1-CardSubType1#ControllerCardStatus2-State2-IP2-MAC2-UUID2
        #-SlotIndex2-CardType2-CardSubType2$CardState1-SlotIndex1-CardType1-CarfdSubType1#Cardtate2-SlotIndex2-CardType2-CarfdSubType2#..#UP TO 12   
        #print("CardInfo=%s"%str(retStr)) 
        cards=str(retStr).split("$")
        controllerCards=cards[0].split("#")
        lineCards=cards[1].split("#")
        if GlobalVars.gneIP2subStr not in currNodeIp1:
            currNodeIp=GlobalVars.iP2ToiP1Mapping.get(currNodeIp1)[1]
        else:
            currNodeIp=currNodeIp1    
        #---Adding Controller Cards _START_
        for controllerCard in controllerCards:
            controllerCardInfo=controllerCard.split("-")
            slot=controllerCardInfo[5]
            cardType=controllerCardInfo[6]
            cardSubType=controllerCardInfo[7]
            state=controllerCardInfo[1]
            status=controllerCardInfo[0]
            if state == Constants.ACTIVE :
                tmpList=[int(rack),int(subRack),int(slot),int(state),int(status)]
                if currNodeIp not in GlobalVars.cardDetailsDict:
                    GlobalVars.cardDetailsDict[currNodeIp]={} 
                
                if cardType not in GlobalVars.cardDetailsDict.get(currNodeIp):
                    GlobalVars.cardDetailsDict.get(currNodeIp)[cardType]={}
                
                if cardSubType not in GlobalVars.cardDetailsDict.get(currNodeIp).get(cardType):
                    GlobalVars.cardDetailsDict.get(currNodeIp).get(cardType)[cardSubType]=[]             
            
                GlobalVars.cardDetailsDict.get(currNodeIp).get(cardType).setdefault(cardSubType,[]).append(tmpList)     
        #print("ffff %s"%GlobalVars.cardDetailsDict)
        #---Adding Controller Cards _END_
        
        #---Adding Line Cards _START_
        for lineCard in lineCards:
            lineCardInfo=lineCard.split("-")
            slot=lineCardInfo[1]
            cardType=lineCardInfo[2]
            cardSubType=lineCardInfo[3]
            state=lineCardInfo[0]
            status=0
            if state == Constants.READY :
                tmpList=[int(rack),int(subRack),int(slot),int(state),int(status)]
                if currNodeIp not in GlobalVars.cardDetailsDict:
                    GlobalVars.cardDetailsDict[currNodeIp]={} 
                
                if cardType not in GlobalVars.cardDetailsDict.get(currNodeIp):
                    GlobalVars.cardDetailsDict.get(currNodeIp)[cardType]={}
                
                if cardSubType not in GlobalVars.cardDetailsDict.get(currNodeIp).get(cardType):
                    GlobalVars.cardDetailsDict.get(currNodeIp).get(cardType)[cardSubType]=[]             
            
                GlobalVars.cardDetailsDict.get(currNodeIp).get(cardType).setdefault(cardSubType,[]).append(tmpList)     
        #print("hhhh %s"%GlobalVars.cardDetailsDict)
        #---Adding Line Cards _END_
        
       
#GET CARD INFO _END_
#GET NODE LIST _START_
def get_node_list(ip,oid):
    #print("Get subagent info..%s"%oid)
    retStr=get_subagent_info(GlobalVars.gneIP1,oid)
    
    if not retStr:
        #print("Error!!!!!")
        return Constants.UNABLE_TO_GET_SUBAGENTINFO;
 
    else:  
        #print(str(retStr))            
        lst=str(retStr).split("#")

        for idx,subLst in enumerate(lst[1:]):
            nodeInfo=subLst.split("-") 
            GlobalVars.nodeList.append(nodeInfo[6])
        #print(GlobalVars.nodeList)
        return Constants.NO_ERROR
#GET NODE LIST _END_
#GET NODE DIRECTION _START_
def get_node_direction(ip,oid):  
    for node in GlobalVars.nodeList: 
        oid1=oid   
        endIP,ErrorState=get_end_ip(node)
        oid1=oid1+str(endIP)+'.1.0'
        #print("Get subagent info..%s"%oid1)
        retStr=get_subagent_info(GlobalVars.gneIP1,oid1)
    
        if retStr==Constants.GET_REQUEST_FAILED:
            print("Error!!!!!")
            
        else:  
            #print(str(retStr))            
            lst=str(retStr).split("#")
        
            nodeSeq=[]
            for idx,subLst in enumerate(lst[1:]):
                nodeInfo=subLst.split("-") 
                nodeSeq.append(nodeInfo[6])
            #print(nodeSeq) 
        
            if  lst[1]:
                nodeInfo=lst[1].split("-")  
                #print(lst[1])
                egressNodeDic={}           
                for idx,connectionMatrix in enumerate(nodeInfo[7:]):
                    info=connectionMatrix.split("$")
                    #print("idx=%d,info[0]=%d,info[1]=%d,IP=%s" %(idx,int(info[0]),int(info[1]),nodeInfo[6]))
                    if int(info[0])!=0 :
                        egressNodeDic[int(info[1])]=nodeSeq[idx]                  
                    
            GlobalVars.nodeDirectionDict[nodeInfo[6]] =egressNodeDic   
               
            #print(GlobalVars.nodeDirectionDict)    
    return   GlobalVars.nodeDirectionDict ;      
#GET NODE DIRECTION _END_  

#GET MPN CARD _START_
def get_mpn_card(ip,oid,givenLembda,givenLembdaDir):
    for rack in range(1,Constants.MAX_RACKS+1):
        for subRack in range(1,Constants.MAX_SUBRACKS+1):
            tmpOid=oid+'.'+str(rack)+'.'+str(subRack)+'.0.0.0'
            api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
            retStr,ErrorState=api.snmp_get(GlobalVars.gneIP1,tmpOid) 
            #print("givenLembda:%d %d"%(givenLembda,givenLembdaDir))
            if len(retStr)<=2 or ErrorState==Constants.GET_REQUEST_FAILED:
                print("Error!!!!!")
                return Constants.DEFAULT_LIST,Constants.GET_REQUEST_FAILED;
 
            else: 
                tpnCardDetail=[]
                print(str(retStr))            
                tpnConf=str(retStr).split("$")
                lst=tpnConf[1].split("#")
        
                for subLst in lst:
                    tpnInfo=subLst.split("-")
                    #print("tpnInfo[6]=%d %d"%(int(tpnInfo[6]),int(tpnInfo[5])))
                    if int(tpnInfo[6])==int(givenLembda) and int(tpnInfo[5])==int(givenLembdaDir):
                        tpnCardDetail.insert(0,rack)
                        tpnCardDetail.insert(1,subRack)
                        tpnCardDetail.insert(2,tpnInfo[0])
                        tpnCardDetail.insert(3,tpnInfo[1])
                        tpnCardDetail.insert(4,tpnInfo[2])
                        print(tpnCardDetail)
                        break
                print(tpnCardDetail)
                return tpnCardDetail,Constants.TPN_CARD_DETAIL_NOT_FOUND;
        
           
#GET MPN CARD _END_  

#GET WSS CHANNLE CONFIGURATION _START_
def get_wss_channle_configuration(ip,oid,givenLembda):
    print("Get WSS channle Configuration for wavelength %d"%givenLembda)
    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
    retStr,ErrorState=api.snmp_get(GlobalVars.gneIP1,oid) 
    if not retStr:
        print("Error!!!!!")
        return Constants.DEFAULT;
 
    else: 
        wssTxDir=0  
        info=str(retStr).split("$")
        subInfo=info[1].split("#")
        
        for subSubInfo in subInfo:
            print(subSubInfo)
            channleInfo=subSubInfo.split("-")
            if channleInfo[0]==str(givenLembda):
                wssTxDir=channleInfo[1]
                break
        
        print(str(retStr))  
               
        return int(wssTxDir);  
#GET WSS CHANNLE CONFIGURATION _END_ 

#GET WSS CURRENT CONFIGURATION _START_
def get_wss_current_configuration(ip,oid,givenLembda):
    print("Get WSS Current Configuration")
    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
    retStr,ErrorState=api.snmp_get(GlobalVars.gneIP1,oid) 
    if not retStr:
        print("Error!!!!!")
        return Constants.DEFAULT;
 
    else: 
        print(str(retStr))   
        info=str(retStr).split("#")
        if(len(info)>2):
            subInfo=info[9+int(givenLembda)-1].split("$")
            if(len(subInfo)>2):
                print("Attenuation=%f,ChannelPower=%f,Action=%d"%(float(subInfo[0]),float(subInfo[1]),int(subInfo[2])))
      
               
              
          
#GET WSS CURRENT CONFIGURATION _END_ 

#GET WSS DIRECTION CONFIGURATION _START_
def get_wss_direction_configuration(ip,oid,givenLembdaDir):
    print("Get WSS Direction Configuration")
    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
    retStr,ErrorState=api.snmp_get(GlobalVars.gneIP1,oid) 
    print("WSSgivenLembdaDir:%s"%givenLembdaDir)
    if not retStr:
        print("Error!!!!!")
        return Constants.DEFAULT_LIST,givenLembdaDir,Constants.EMPTY_WSS_DIR_CONFIG;
 
    else: 
       
        print(str(retStr))            
        lst=str(retStr).split("#")
        if lst[0]=='0':
            return Constants.DEFAULT_LIST,givenLembdaDir,Constants.EMPTY_WSS_DIR_CONFIG;
        cardDetailList=[]
        
        for subLst in lst[1:]:
            tmpDir=givenLembdaDir
            wssDirInfo=subLst.split("-")
            #Adding Direction Offset
            if (wssDirInfo[3]==str(Constants.WSS219[0]) and wssDirInfo[4]==str(Constants.WSS2120[1]) or wssDirInfo[3]==str(Constants.WSS2120[0]) and wssDirInfo[4]==str(Constants.WSS2120[1])) and int(tmpDir)<Constants.WSS219[2]:
                tmpDir=int(givenLembdaDir)+Constants.WSS219[2]
            elif wssDirInfo[3]==str(Constants.WSS19[0]) and wssDirInfo[4]==str(Constants.WSS19[1]) and int(tmpDir)<Constants.WSS19[2]:    
                tmpDir=int(givenLembdaDir)+Constants.WSS19[2]
                
            if int(wssDirInfo[5])==tmpDir:
                cardDetailList.insert(0,wssDirInfo[0])
                cardDetailList.insert(1,wssDirInfo[1])
                cardDetailList.insert(2,wssDirInfo[2])
                cardDetailList.insert(3,wssDirInfo[3])
                cardDetailList.insert(4,wssDirInfo[4])
                print("CardList:%s"%cardDetailList)
                return cardDetailList,tmpDir,Constants.NO_ERROR;
            
        
        return cardDetailList,givenLembdaDir,Constants.GIVEN_DIR_CARD_UNAVAILABLE;
           
#GET WSS DIRECTION CONFIGURATION _END_ 

#GET MPN TX POWER TRAP _START_
def get_mpn_tx_power(mpnCard,endIP):
    oid=GlobalVars.PM_OID+str(endIP)+'.8.1.9.'+str(mpnCard[0])+'.'+str(mpnCard[1])+'.'+str(mpnCard[2])+'.'+str(mpnCard[3])+'.'+str(mpnCard[4])+'.1.3.1'
    
    trapOid=GlobalVars.PM_TRAP_OID+str(endIP)+'.5.5.1.9.'+str(mpnCard[0])+'.'+str(mpnCard[1])+'.'+str(mpnCard[2])+'.'+str(mpnCard[3])+'.'+str(mpnCard[4])+'.1.3.1'
    if trapOid not in GlobalVars.TRAP_OID:
        GlobalVars.TRAP_OID[str(trapOid)]=1
        
    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
    retStr,ErrorState=api.snmp_get(GlobalVars.gneIP1,oid) 
    #print(trapOid)
    if ErrorState ==Constants.GET_REQUEST_FAILED:
        print("Error!!!!!")
        return Constants.UNABLE_TO_GET_SUBAGENTINFO;
    else:
        print("Response will be a trap..")
    
#GET MPN TX POWER TRAP _END_

#GET MPN SFP STATUS _START_
def get_mpn_sfp_status(mpnCard,endIP):
    oid=GlobalVars.CM_OID+str(endIP)+'.17.1.8.'+str(mpnCard[0])+'.'+str(mpnCard[1])+'.'+str(mpnCard[2])+'.'+str(mpnCard[3])+'.'+str(mpnCard[4])+'.1.0'
   
    api=snmpApi.SNMP(Constants.TIMEOUT,Constants.RETRIES)
    retStr,ErrorState=api.snmp_get(GlobalVars.gneIP1,oid) 
   
    if ErrorState ==Constants.GET_REQUEST_FAILED:
        print("Error!!!!!")
        return Constants.UNABLE_TO_GET_SUBAGENTINFO;
    else:
        print("MPN sfp status Received..")
        print("SFP STATUS=%s"%str(retStr))
        
#GET MPN SFP STATUS _END_

 



#GET END IP _START_
def get_end_ip(ip):
    #print("Get end ip[%s].."%ip)
    retStr=""
    if ip in GlobalVars.iP2ToiP1Mapping:
        ret=GlobalVars.iP2ToiP1Mapping.get(ip)
        if len(ret)==4:
            retStr=ret[2] 
            #print("endIP=%s"%retStr)
            
    if not retStr:
        #print("Error!!!!!")
        return str(retStr),Constants.END_IP_NOT_FOUND;
 
    else:     
        return str(retStr),Constants.NO_ERROR;
#GET END IP _END_

#Nested Dictionary Printer _START_
def printTabularData(data,columnList):
    flatten(data,[])
    tmpList=GlobalVars.myList1[:]
    print(GlobalVars.myList1)
    df = pd.DataFrame(GlobalVars.myList1,columns=columnList)
    print(df)
    GlobalVars.myList1=[]
    return tmpList
#Nested Dictionary Printer _END_
#Printer _END_
def flatten(mydict,myList):
    for key,value in mydict.items():
        #print(key)
        if type(value) == dict:
            myList.append(key)
            flatten(value,myList[:])
            myList.pop()
            #print("---------")
        else:
            myList.append(key)
            #print(type(value))
            if type(value) == list:
                if any(isinstance(subVal, list) for subVal in value):
                    for subVal in value:
                        myList=myList+subVal
                        GlobalVars.myList1.append(myList[:])               
                        for i in range(len(subVal)):
                            if myList:
                                myList.pop()
                    myList.pop()            
                else:    
                    myList=myList+value
                    GlobalVars.myList1.append(myList[:])               
                    for i in range(len(value)+1):
                        if myList:
                            myList.pop()
            else:
               
                myList.append(value)
                GlobalVars.myList1.append(myList[:])
                myList.pop()
                myList.pop()
                
                
            #print(GlobalVars.myList1)
                #print(myList)
            


    return myList
#Printer _END_