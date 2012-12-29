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
        self.__path = config["path"]
        self.__connect(self.__path)
        
    def __connect(self,path):
        logging.log(logging.DEBUG, "db: connecting")
        self._con = sqlite3.connect(path)
        self.cur = self._con.cursor()
        
    def importDB(self, aps=None):
        logging.log(logging.DEBUG, "db: requesting")
        try:
            self.cur.execute("""SELECT mainip, sys_board, sys_os_type, sys_os_name,
                        sys_os_rel, on_wifidog_status, on_vpn_status, on_ugw_status
                    FROM nodes""")
        except sqlite3.OperationalError:
            logging.log(logging.ERROR, "db: importDB() failed")
            return aps
        for (mainip, sys_board, sys_os_type, sys_os_name, sys_os_rel, 
                on_wifidog_status, on_vpn_status, on_ugw_status) in self.cur.fetchall():
            ip = mainip
            if aps and (ip in aps):
                ap = aps[ip]
            else:
                ap = primitives.AccesPoint(ip, None)
            ap.board = self.__parseBoardID(sys_board)
            ap.os = str(sys_os_type.strip())
            os_details = str("%s %s" % (sys_os_name.strip(), sys_os_rel.strip()))
            # empty strings are removed from start/end via "strip"
            if os_details.strip():
                ap.os += " (%s)" % os_details.strip()
            # TODO: using unicode here silently breaks stuff somewhere else! (all nodes disappear from the map)
            ap.os = str(ap.os)
            ap.wifidog = on_wifidog_status
            ap.vpn = on_vpn_status
            ap.ugw = on_ugw_status
            if aps:
                aps[ip] = ap
        return aps
        
    def __parseBoardID(self,strBoardID):
        board2name={"0x467/00":"Buffalo WHR-G54s",
                    "0x0467/42":"Linksys WRT54GL",
                    "0x0101/42":"Linksys WRT54GS",
                    "0x0708/42":"Linksys WRT54G",
                    "bcm94710dev/asusX":"Asus WL500",
                    "Atheros AR7161 rev 2 Ubiquiti RouterStation Pro":"Ubiquiti Routerstation",
                    "Atheros AR7240 (Python)  NanoStation M5": "Ubiquiti NanoStation M5",
                    "Atheros AR7240 (Python)  NanoBridge M5":"Ubiquiti NanoBridge M5",
                    "Atheros AR7240 rev 2 Ubiquiti Nanostation M":"Ubiquiti Nanostation M",
                    "Atheros AR7241 rev 1 Ubiquiti Bullet M":"Ubiquiti Bullet M",
                    "Atheros AR7241 rev 1 Ubiquiti Nanostation M":"Ubiquiti Nanostation M",
                    "Atheros AR9132 rev 2 TP-LINK TL-WR1043ND": "TP-LINK TL-WR1043ND",
                    "Gateworks Avila Network Platform":"Avila",
                    "Broadcom BCM5352 chip rev 0":"Linksys WRT54G",
                    "Broadcom BCM4712 chip rev 1":"Linksys WRT54G",
                    "Broadcom BCM4712 chip rev 2":"Linksys WRT54G",
                    "":"WRAP 2E-E"}
        return board2name.get(strBoardID.strip(),strBoardID.strip().encode("utf8"))

