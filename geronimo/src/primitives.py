'''
Created on 19.10.2011

@author: matthias
'''

class APstat():
    ONLINE=0
    FLAPPING=1
    DEAD=3
    UNUSED=4
    
    

class AccesPoint():
    '''Properties of one AP'''
    def __init__(self,id,position):
        self.id=id
        self.position=position
        self.lastonline=None
        self.state=None
        self.ugw=None
        self.wifidog=None

class Nic():
    pass
    
class Link():
    '''Properties of a link between two APs'''
    def __init__(self,ap1,ap2):
        self.ap1=ap1 #we use IPs only, to shrink down the dunp of the links list
        self.ap2=ap2
        self.etx=None
        self.etxcolor=None
        self.cable=None
        self.backbone=None

class Site():
    '''A collection of APs at the same position, that are wired'''
    pass