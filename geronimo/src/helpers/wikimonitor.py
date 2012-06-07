# -*- coding: UTF-8 -*-
'''
Created on 13.10.2011

@author: matthias
'''
import feedparser
import datetime
import time
import sets
import pickle
import logging

class wikimonitor():
    '''Observers the wiki and finds changed Accespoint-Pages'''
    __url=""
    
    def __init__(self,config):
        self.__url=config["url"]
        pass
    
    def getNewAccessPointPages(self):
        pages=[]
        feedparser.USER_AGENT="Geronimo"
        logging.log(logging.DEBUG, "...getting RSS wiki feed") 
        feed = feedparser.parse(self.__url+"/w/index.php?title=Special:Recentchanges&feed=atom")
        for item in feed[ "items" ]:
            if self.__isAfterLastRun(item["date_parsed"]):
                if self.__isAccessPointPage(item["title"]) and not self.__isBotEdit(item["author"]):
                    logging.log(logging.DEBUG, "...found changed page: "+item["title"])
                    pages.append(item["title"])
        logging.log(logging.DEBUG, "...last run saved") 
        self.__saveLastRun()
        return list(sets.Set(pages))
            
    def __isAfterLastRun(self,date):
        itemdate=datetime.datetime.fromtimestamp(time.mktime(date))
        lastRun=self.__loadLastRun()
        if itemdate>lastRun:
            return True
        else:
            return False
        
    def __isAccessPointPage(self, title):
        return title.startswith("AP")
    
    def __isBotEdit(self,author):
        return author=="Geronimo"
    
    def __saveLastRun(self):
        f=open("lastrun.dmp","wb")
        t=datetime.datetime.now()
        pickle.dump(t,f)
        f.close
        
    def __loadLastRun(self):
        f=open("lastrun.dmp","rb")
        old=pickle.load(f)
        return old