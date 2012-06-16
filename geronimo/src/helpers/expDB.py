'''
Created on 01.05.2012

@author: matthias

Imports informations from APData database that collects them from the APs via OLSR broadcasting
'''
import logging
import sqlite3
import pickle
import json
import geojson
import primitives


class DBimporter():
    def __init__(self,config):
        self.__path=config["path"]
        self.__connect(self.__path)
        
    def __connect(self,path):
        global con
        global cur
        logging.log(logging.DEBUG, "db: connecting")
        con = sqlite3.connect(path)
        cur = con.cursor()
        
    def importDB(self,aps=None):
        logging.log(logging.DEBUG, "db: requesting")
        cur.execute('SELECT mainip,sys_board,sys_os_type,sys_os_name,sys_os_rel,on_wifidog_status,on_vpn_status,on_ugw_status FROM nodes')
        for row in cur:
            ip=row[0]
            if aps is not None:
                try:
                    ap=aps[ip]
                except KeyError:
                    aps[ip]=ap
            else:
                ap=primitives.AccesPoint(ip,None)
            ap.board=self.__parseBoardID(row[1])
            ap.os=str(row[2]+"("+row[3]+" "+row[4]+")")
            ap.wifidog=row[5]
            ap.vpn=row[6]
            ap.ugw=row[7]
            aps[ip]=ap
        return aps
        
    def __parseBoardID(self,strBoardID):
        board2name={"0x467/00":"Buffalo WHR-G54s",
                    "0x0467/42":"Linksys WRT54GL",
                    "0x0101/42":"Linksys WRT54GS",
                    "0x0708/42":"Linksys WRT54G",
                    "bcm94710dev/asusX":"Asus WL500",
                    "Atheros AR7240 (Python)  NanoStation M5": "Ubiquiti NanoStration M5",
                    "Atheros AR7240 (Python)  NanoBridge M5":"Ubiquiti NanoBridge M5",
                    "Atheros AR9132 rev 2 TP-LINK TL-WR1043ND": "TP-LINK TL-WR1043ND",
                    "Atheros AR7240 rev 2 Ubiquiti Nanostation M":"Ubiquiti Nanostation M",
                    "Atheros AR7241 rev 1 Ubiquiti Bullet M":"Ubiquiti Bullet M",
                    "Atheros AR7241 rev 1 Ubiquiti Nanostation M":"Ubiquiti Nanostation M",
                    "Gateworks Avila Network Platform":"Avila",
                    "Broadcom BCM5352 chip rev 0":"Linksys WRT54G",
                    "Broadcom BCM4712 chip rev 1":"Linksys WRT54G",
                    "Broadcom BCM4712 chip rev 2":"Linksys WRT54G",
                    "":"WRAP 2E-E"}
        strBoardID=strBoardID.rstrip()
        return board2name[strBoardID]
