# -*- coding: UTF-8 -*-
'''
Created on 13.10.2011

@author: matthias
'''

from wikitools import wiki
from wikitools import api
from wikitools import pagelist
import logging
import urllib
import geojson
import pickle
from primitives import *

class wikiImporter():
    '''Crawls the OpenNet wiki to get and to put informations'''
    __user=""
    __password=""
    __url=""
           
    def __init__(self,config):
        self.__user=config["user"]
        self.__password=config["password"]
        self.__url=config["url"]
        self.__connect()
        
    def __connect(self):
        global site
        logging.log(logging.DEBUG, "wiki login") 
        site = wiki.Wiki(self.__url+"/w/api.php")
        site.login(self.__user,self.__password)
        site.setUserAgent("Geronimo")  

    def loadAPTemplates(self):
        global site
        query=self.__getAPTemplateList(site)
        list=pagelist.listFromQuery(site,query["query"]["embeddedin"])
        for appage in list:
            print appage
              
    def __getAPTemplateList(self, site):
        logging.log(logging.DEBUG, "wiki: load AP list")
        getAllAPTemplates = {'action':'query', 'list':'embeddedin', "eititle":"Template:accesspoint", "eilimit":"500"}
        return api.APIRequest(site, getAllAPTemplates).query()
    
    #http://wiki.opennet-initiative.de/wiki/Opennet_Nodes
    def importAPTable(self,aps=None):
        '''
        APName
        last seen
        place
        Antenna descr.
        device
        owner
        comment
        lonlat
        NextGateWayLQ
        '''
        logging.log(logging.DEBUG, "wiki: import all accesspoints:") 
        if aps is None:
            aps={}
        self.__aps=aps
        source=self.__getWikiSource('Opennet_Nodes')
        tables=source.split("|}")
        for t in tables :
            if t.find("Mobile Teilnehmer")==-1:            
                # now a plain wiki table
                t=self.__removeIntro(t)
                items=t.split("|-")
                for item in items:
                    if item!="\n" and item!="---\n" and len(item)>5:
                        [ip,position]=self.__parseAP(item)
                        try:
                            #update existing AP
                            self.__aps[ip].position=position
                            if (position.coordinates==["",""]):
                                self.__aps[ip].state=APstat.UNUSED
                        except KeyError:
                            #or create new one
                            n=AccesPoint(ip,position)
                            if (position.coordinates==["",""]):
                                n.state=APstat.UNUSED
                            self.__aps[ip]=n
        return self.__aps
    
  
    def __parseAP(self,str):
        attrs=str.split("\n|")
        name=attrs[1]
        name=name[name.find("<OnApStatus>")+len("<OnApStatus>"):name.find("</OnApStatus>")]
        if(name.find(".")==-1):
            ip="192.168.1."+name
        else:
            ip="192.168."+name
        place=attrs[2]
        antenna_descr=attrs[3]
        device=self.__replaceWikiLinks(attrs[4])
        owner=self.__replaceWikiLinks(attrs[5])
        description=attrs[6]
        lonlat=attrs[7]
        try:
            if not lonlat.isspace():
                lonlat=lonlat.replace("N","").replace("E","")
                lonlat=lonlat.split(" ")
                lat=float(lonlat[1].replace(",","."))
                lon=float(lonlat[0].replace(",","."))
            else:
                try:
                    if self.__aps[ip].state is not APstat.DEAD:
                        logging.log(logging.ERROR, "wiki: AP without geolocation:"+name) #frische ungenutzte Plätze
                except KeyError:
                    pass #einfach ein alter unbenutzeter AP Platz
                lat=""
                lon=""
        except:
            logging.log(logging.ERROR, "wiki: AP with bad lonlat"+name)
            lat=""
            lon=""
        p=geojson.Point([lat,lon])
        return [ip,p]
#        
#        node["name"]=name
#        node["ip"]=ip        
#        node["wiki"]="https://wiki.opennet-initiative.de/index.php/AP"+name
#        node["place"]=place
#        node["antenna_descr"]=antenna_descr
#        node["device"]=device
#        node["owner"]=owner
#        node["description"]=description
#        node["lon"]=lon
#        node["lat"]=lat

    def __getWikiSource(self,pageTitle):
            global site
            nodesLists= {'action':'query', 'titles':pageTitle}
            request = api.APIRequest(site, nodesLists)
            result = request.query()
            source=pagelist.listFromQuery(site,result["query"]["pages"])[0].getWikiText(False)
            return source
    
    #only the pure data rows remains
    def __removeIntro(self,source):
        pos=source.find("{|")
        source=source[pos:]
        pos=source.find("|<OnApStatus>")-2
        source=source[pos:]
        return source
    
    def __replaceWikiLinks(self,source):
        start=source.find("[[")
        middle=source.find("|")
        end=source.find("]]")
        if start>-1:
            temp=source[:start]
            if middle==-1:
                temp=temp+'<a href="https://wiki.opennet-initiative.de/wiki/'+source[start+2:end]+'">'+source[start+2:end]+'</a>'
            else:
                temp=temp+'<a href="https://wiki.opennet-initiative.de/wiki/'+source[start+2:middle]+'">'+source[middle+1:end]+" ("+source[start+2+len("Benutzer:"):middle]+")"+'</a>'
            temp=temp+source[end+2:]
        else:
            temp=source
        return temp
    
    #https://wiki.opennet-initiative.de/wiki/Backbone
    def importBackbones(self,links):
        '''
        channel
        SSID
        AP1
        AP2
        '''
        logging.log(logging.DEBUG, "wiki: import backbone") 
        source=self.__getWikiSource('Backbone')
        source=source[source.find("=== Backbone Links ==="):]
        for item in source.split("|-"):
            if item.find("|")!=-1 and item.find("!")==-1:
                item=item.replace("\n","")
                item=item.split("|")
                channel=item[1]
                start=item[2].replace("[[AP","").replace("]]","")
                start="192.168.1."+start
                end=item[4].replace("[[AP","").replace("]]","")
                end="192.168.1."+end
                ssid=item[6]
                id=start+"-"+end
                try:
                    link=links[id]
                    link.backbone=True
                    links[start+"-"+end]=link
                except KeyError:
                    try:
                        link=links[end+"-"+start]
                        link.backbone=True
                        links[start+"-"+end]=link
                    except KeyError:
                        logging.log(logging.ERROR, "Backbones: No such link: "+id) 
        return links
                
    