#!/usr/bin/env python

import time
import requests
import csv


############################## 
## Definir le dernier Block ##
##############################

Last_Block = requests.get ("https://insight.litecore.io/api/sync")

Last_Block = Last_Block.json()

Last_Block = Last_Block["height"]

##############################
## Definir le premier Block ##
##############################

First_Block = input("how many blocks backwards : ")

First_Block = Last_Block - int(First_Block)

##################################
## Initialisation de la matrice ##
##################################

Bot_Table = []

###########################################
## Creation de la variable current Block ##
###########################################

Current_Block = First_Block

while Current_Block <= Last_Block:
    
    ##############################
    ## Obtenir le hash du block ##
    ##############################
    
    Current_Block_Hash = requests.get ("https://insight.litecore.io/api/block-index/" + str(Current_Block))
    
    Current_Block_Hash = Current_Block_Hash.json()

    Current_Block_Hash = Current_Block_Hash["blockHash"]
    
    ####################################
    ## Obtenir la date Epoch du block ##
    ####################################
    
    Current_Block_Unix_Time = requests.get ("https://insight.litecore.io/api/block/" + str(Current_Block_Hash))
    
    Current_Block_Unix_Time = Current_Block_Unix_Time.json()

    Current_Block_Unix_Time = Current_Block_Unix_Time["time"]
    
    ###############################
    ## Convertir en temps normal ##
    ###############################
        
    Current_Block_Time = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(Current_Block_Unix_Time))
    
    ########################################################
    ## Obtenir le prix au moment d'apparition de ce block ##
    ########################################################
    
    Current_Block_Price = requests.get("https://min-api.cryptocompare.com/data/histominute?fsym=LTC&tsym=BTC&limit=1&aggregate=1&toTs=" + str(Current_Block_Unix_Time))
    
    Current_Block_Price = Current_Block_Price.json()

    Current_Block_Price = Current_Block_Price["Data"][0]["close"]
    
    print(Current_Block_Price)
    
    #######################################   
    ## Obtenir toutes les txs d'un block ##
    #######################################
    
    All_txs_CB = requests.get ("https://insight.litecore.io/api/block/" + str(Current_Block_Hash))
    
    All_txs_CB = All_txs_CB.json()
    
    ###########################
    ## Sauter la tx coinbase ##
    ###########################
    
    All_txs_CB_WC = iter(All_txs_CB["tx"])
    
    next(All_txs_CB_WC) 
    
    ###############################
    ## Initialiser les variables ##
    ###############################
            
    P2PKH_To_P2SH_Volume = 0
    P2PKH_To_P2SH_Txsnumber = 0
      
    P2SH_To_P2PKH_Volume = 0
    P2SH_To_P2PKH_Txsnumber = 0
        
    P2PKH_To_P2PKH_Volume = 0
    P2PKH_To_P2PKH_Txsnumber = 0
         
    P2SH_To_P2SH_Volume = 0
    P2SH_To_P2SH_Txsnumber = 0
    
    
    #############################################    
    ## Aller chercher chaque txhash d'un block ##
    #############################################
              
    for inc in All_txs_CB_WC:
        
        #################################
        ## Initialisation de variables ##
        #################################
        
        VINP2SH = False
        VOUTP2SH = False
        
        #####################################
        #### Obtenit la tx au format JSON ###
        #####################################
        
        print("https://insight.litecore.io/api/tx/" + str(inc))

        Current_Tx_Hash = requests.get("https://insight.litecore.io/api/tx/" + str(inc))
               
        Current_Tx_Hash = Current_Tx_Hash.json()

        #################################
        ## Analyse des VIN de cette tx ##
        #################################
         
        for incVIN in Current_Tx_Hash["vin"]:
            
            try:
            
                if incVIN["addr"][0] == "M":
                
                    VINP2SH = True
            
            except:
                
                print("ici VIN plante")
                            
        ##################################
        ## Analyse des VOUT de cette tx ##
        ##################################
                
        for incVOUT in Current_Tx_Hash["vout"]:
            
            try:
            
                if incVOUT["scriptPubKey"]["addresses"][0][0] == "M":
                
                    VOUTP2SH = True
        
            except:
                
                print("ici VOUT plante")
        
        ###########################
        ## Renseigner le tableau ##
        ###########################   
        
        if VINP2SH == False and VOUTP2SH == True:
            
            P2PKH_To_P2SH_Volume = P2PKH_To_P2SH_Volume + Current_Tx_Hash["valueOut"]
            
            P2PKH_To_P2SH_Txsnumber += 1
        
        if VINP2SH == True and VOUTP2SH == False:
            
            P2SH_To_P2PKH_Volume = P2SH_To_P2PKH_Volume + Current_Tx_Hash["valueOut"]
            
            P2SH_To_P2PKH_Txsnumber += 1
        
        if VINP2SH == False and VINP2SH == False:
            
            P2PKH_To_P2PKH_Volume = P2PKH_To_P2PKH_Volume + Current_Tx_Hash["valueOut"]
            
            P2PKH_To_P2PKH_Txsnumber += 1
    
        if VINP2SH == True and VINP2SH == True:
            
            P2SH_To_P2SH_Volume = P2SH_To_P2SH_Volume + Current_Tx_Hash["valueOut"]
            
            P2SH_To_P2SH_Txsnumber += 1
         
    ###########################
    ## Renseigner le tableau ##
    ###########################
    
    Blockinfo = [Current_Block_Time,Current_Block_Unix_Time,Current_Block,Current_Block_Price,P2PKH_To_P2SH_Txsnumber,P2PKH_To_P2SH_Volume,P2SH_To_P2PKH_Txsnumber,P2SH_To_P2PKH_Volume,P2PKH_To_P2PKH_Txsnumber,P2PKH_To_P2PKH_Volume,P2SH_To_P2SH_Txsnumber,P2SH_To_P2SH_Volume]
        
    Bot_Table.append(Blockinfo)   
    
    ####################
    ## Remplir le CSV ##
    ####################
        
    csvfile = "/home/sapharic/eclipse-workspace/MyBOT/Table.csv"
    
    with open(csvfile, "a") as csvfileobject:
        
        writer = csv.writer(csvfileobject, lineterminator='\n')
            
        writer.writerow(Blockinfo)  
       
                
    Current_Block += 1
    
    



#url = "https://explorer.komodo.services/api/txs/?block=809345"

#data = requests.get(url).json

#print (data)

#print ("gygygy")

#https://explorer.komodo.services/api/txs/?block=809345
#Ici ca détaille toutes les txs du blocks mais ca me donne pas les adresses des UTXO dépensés


# https://explorer.komodo.services/api/block-index/809345
# Ca retrouve juste le hash du block a partir de sa hauteur

#https://explorer.komodo.services/api/blocks?limit=1500&blockDate=2018-04-26
#Ca permet de récupérer les blocks faits depuis une certaine date

#https://explorer.komodo.services/api/tx/163414170454f8b4005b82262c75454fd5ec09e639656df0db9fe7e42a12cde4
# pour avoir les info d'une tx. Mais ca ne donne pas l'adresse d'ou ca provient


#Test LTC
#https://insight.litecore.io/api/txs/?block=01a5f54412ef05d0e2b61f6dafd4e078fc19d82e951a51962f67380ed8341a44


#Explorateur LTC
#https://insight.litecore.io


#Explorateur BTC
#https://insight.bitpay.com


#Aide API
#https://github.com/bitpay/insight-api


#https://api.coinmarketcap.com/v1/ticker/litecoin/


