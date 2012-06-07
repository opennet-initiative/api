# -*- coding: UTF8 -*-
'''
Created on 15.07.2011

@author: Matthias Meisser
'''

import os
import time
import datetime
import logging
from primitives import *
import primitives

class lastSeenImporter:
    def __init__(self,config):
        self.__path=config["path"]

    #get lastonline date by reading /lastseen file dates
    def importLastSeen(self,aps=None):
        logging.log(logging.DEBUG, "lastseen: importing")
        if aps is None:
            aps={}
        files=os.listdir(self.__path)
        for f in files:
            filename=os.path.join(self.__path,f)
            if os.path.isfile(filename) and (f.find("-")>-1): #ignore 
                ip=self.__normaliseIP(f)
                ftime=os.path.getmtime(filename)                
                state=self.__getState(ftime)                
                try:
                    ap = AccesPoint(ip, None)
                except KeyError:                    
                    logging.log(logging.ERROR, "lastseen: miss in DB AP"+ip)
                    ap=aps[ip]                    
                ftime=time.gmtime(ftime)
                ap.lastonline=time.strftime("%d.%m.%Y (%X)",(ftime))
                ap.state=state
                aps[ip]=ap 
        aps=self.__setLegacyStates(aps)
        return aps
      
    def __normaliseIP(self, nodename):
        if nodename.find("-")>-1:
            nodename=nodename.replace("-",".")
        else:
            nodename="1."+nodename
        return "192.168."+nodename
    
    def __getFileDate(self,filepath):
        return os.path.getmtime(filepath)
    
    #determine online state upon lastseen date
    def __getState(self,ftime):
        diff=time.time()-ftime-60*60
        state=APstat.ONLINE
        if diff>=60*30:
            state=APstat.FLAPPING
        if diff>=60*30*24*30:
            state=APstat.DEAD
        return state
    
    #set nodes_online to 'dead' if we have no history log
    def __setLegacyStates(self,nodes_online):
        for n in nodes_online.values():
            if n.state is None:
                logging.log(logging.DEBUG, "lastseen: set to default dead AP"+str(n.id))
                nodes_online[n.id].state=APstat.DEAD
        return nodes_online