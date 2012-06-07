'''
Created on 17.05.2012

@author: matthias
'''

#identifies cable connections
class cablesImporter:
    #very simple approach, might become easier with grouping them with wiki templates
    __cableAPs=["192.168.1.15","192.168.1.25","192.168.1.66","192.168.1.152","192.168.2.8","192.168.2.7","192.168.1.157"]
    def __init__(self,links):
        self.__links=links
    def importCables(self):
        for l in self.__links.values():
            if l.ap1 in self.__cableAPs and l.ap2 in self.__cableAPs:
                l.cable=True
                self.__links[l.ap1+"-"+l.ap2]=l
        return self.__links
                
            
