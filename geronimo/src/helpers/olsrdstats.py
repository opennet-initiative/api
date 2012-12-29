# -*- coding: UTF8 -*-
'''
Created on 16.05.2011

@author: Matthias Meisser
'''

import colorsys
import logging
from primitives import *

positions={}

#Parse OLSR txtplugin plugin informations, that come predumped by external commands
#http://www.olsr.org/?q=node/26
class OLSRDimporter():
    def __init__(self,config):
        self.__file=config["file"]
                
    #http://www.olsr.org/?q=node/26
    def importLinks(self,nodes_online):
        global positions
        links={}
        '''
        txtinfo OLSR plugin
        from
        to
        LQ1/LQ2
        ETX
        '''
        logging.log(logging.DEBUG, "olsrd: starting")
#        positions=self.__cacheNodePositions(nodes_online)
        self.__aps=nodes_online
        inp = open(self.__file,'r')
        lines=inp.readlines()
        lines=lines[6:-3] #skip header and empty lines at the end
        for line in lines:
            revID=self.__getLinkIDreverted(line)
            if revID not in links: #add only one link, ignore direction
                try:
                    link=self.__importLink(line)
                    id=link.ap1+"-"+link.ap2
                    links[id]=link
                except:
                    if (line.find("192.168.10.")==-1): #ignore lines with servers
                        if (line.find("192.168.0.254")==-1): #ignore broadcast adresses
                            if (line.find("10.2.0.")==-1): #ignore VPN stuff
                                if (line.find("192.168.33.")==-1): #ignore test APs
                                    if (line.find("192.168.0.")==-1): #ignore Gateways
                                        logging.log(logging.ERROR, "OLSRD: missing AP geoposition: "+self.__getLinkID(line))       
        return links
      
    def __importLink(self,line):
        global positions
        cols=line.split("\t")
        start=cols[0]
        end=cols[1]
        etx=cols[3]  #ETX only stored for one direction
        if (etx=="INFINITE"):
            color=self.__getETXColor(10.0)
        else:
            etx=float(etx)            
            color=self.__getETXColor(etx)
        link=Link(self.__aps[start].id,self.__aps[end].id)
        link.etx=etx
        link.etxcolor=color
        return link


    def __cacheNodePositions(self,nodes_online):
        global positions
        for n in nodes_online.values():
            positions[n.id]=(n.position[0],n.position[1])
        return positions
    
    def __getLinkIDreverted(self,line):
        cols=line.split("\t")
        startIP=cols[0]
        endIP=cols[1]
        return endIP+"-"+startIP

    def __getLinkID(self,line):
        cols=line.split("\t")
        startIP=cols[0]
        endIP=cols[1]
        return startIP+"-"+endIP

    def __getETXColor(self,etx):
      return self.__getETXOrigColor(etx)

    def __getETXOrigColor(self,etx):
        '''return the original colors used in the old map'''
        colors=['#FF0000','#FF0400','#FF0D00','#FF1100','#FF1E00','#FF2200',
          '#FF2600','#FF2B00','#FF3300','#FF3700','#FF3C00','#FF4000','#FF6200',
          '#FF7300','#FF7700','#FF7B00','#FF8400','#FF8800','#FF9100','#FF9500',
          '#FFA600','#FFAE00','#FFB300','#FFB700','#FFCC00','#FFD500','#FFDD00',
          '#FFE100','#FFEE00','#FFF200','#FBFF00','#F2FF00','#D9FF00','#C3FF00',
          '#B2FF00','#AAFF00','#9DFF00','#95FF00','#91FF00','#8CFF00','#80FF00',
          '#77FF00','#73FF00','#5EFF00','#48FF00','#44FF00','#40FF00','#37FF00',
          '#22FF00','#08FF00','#04FF00','#00FF04','#00FF1E','#00FF26','#00FF40',
          '#00FF4D','#00FF59','#00FF5E','#00FF62','#00FF6F','#00FF80','#00FF8C',
          '#00FF91','#00FFA6','#00FFAE','#00FFB7','#00FFBB','#00FFBF','#00FFD0',
          '#00FFD5','#00FFD9','#00FFE6','#00FFF2','#00EEFF','#00DDFF','#00D9FF',
          '#00CCFF','#00C8FF','#00C3FF','#00BBFF','#00B2FF','#00AAFF','#00A6FF',
          '#00A1FF','#0091FF','#008CFF','#0088FF','#0084FF','#007BFF','#0077FF',
          '#0073FF','#0066FF','#0055FF','#004CFF','#0048FF','#0040FF','#002BFF',
          '#001EFF','#0019FF','#0000FF','#0000FF']
        try:
          return colors[int(100/etx)]
        except IndexError:
          return "#FF0000"

    def __getETXNewColor(self,etx):
        '''ETX 1.0 is optimal (blue), 3.0 is acceptable(yellow), > is unusable'''
        hue=(10-etx)/10 #limit to 10 and inverse direction
        hue=hue*0.666 #to become 1.0=blue
        if (etx>3.0):
            hue=hue*0.5 #3.0 yellow
        col=colorsys.hsv_to_rgb(hue,0.9,0.9)
        col=hex(int(col[0]*255))+hex(int(col[1]*255))+hex(int(col[2]*255))
        col="#"+col.replace("0x","")
        return col
    
    
    


        