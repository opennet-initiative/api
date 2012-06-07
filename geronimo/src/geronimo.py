#!/usr/bin/python
# -*- coding: UTF8 -*-

'''
Created on 13.10.2011

@author: Matthias Meisser

Geronimo is a modular data warehouse for maintaining all sources of information by the OpenNet Initiative.

Dependencies: 
    Feedparser    http://code.google.com/p/feedparser/
    Wikitools     code.google.com/p/python-wikitools/

Usage:

Configuration

released under the GPL
'''

import os
import sys
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")
WIKI_CACHE_FILE = os.path.join(BASE_DIR, "wiki_nodes.cache")
LINK_CACHE_FILE = os.path.join(BASE_DIR, "links.cache")

import logging
import getopt
import pickle
from ConfigParser import SafeConfigParser

import helpers.wikimonitor as wikimonitor
import helpers.wikicache as wikicache
import helpers.olsrdstats as olsrdstats
from helpers.lastseen import lastSeenImporter
from helpers.expDB import DBimporter
from helpers.olsrdstats import OLSRDimporter
from helpers.cables import cablesImporter

global logger

def __configToDictonary(config, section):
    dict={}
    for o, v in config.items(section):
        dict[o]=v
    return dict

def __getLogger():
    handler = logging.StreamHandler(sys.stdout)    
    logger = logging.getLogger() 
    logger.addHandler(handler)
    return logger 

def __parseArgs():
    try:
        opts, rest = getopt.getopt(sys.argv[1:],"d", ["debug"])
    except getopt.GetoptError, err:
        print str(err)
        print "Usage: "
        sys.exit(2)
    for o, a in opts:
        if o in ("-d","--debug"):
            logger.setLevel(logging.DEBUG)
        
def __initConfig():
    config = SafeConfigParser()
    logging.log(logging.DEBUG, "loading config")
    config.read(CONFIG_FILE)
    return config        

def __saveCache(filename,objects):
    fcache=file(filename,"w")
    pickle.dump(objects,fcache)
    fcache.close()
        
if __name__ == '__main__':
    global logger
    logger=__getLogger()
    __parseArgs()
    config = __initConfig()
    #update AP state
    inits=__configToDictonary(config,"lastseen")
    ls=lastSeenImporter(inits)
    aps=ls.importLastSeen()
    #crawl wiki
    inits=__configToDictonary(config,"wiki")
    wiki=wikicache.wikiImporter(inits)
    aps=wiki.importAPTable(aps)
    #get AP details
    inits=__configToDictonary(config,"DB")
    db=DBimporter(inits)
    aps=db.importDB(aps)
    #Links
    inits=__configToDictonary(config,"olsrd")
    olsrd=OLSRDimporter(inits)
    links=olsrd.importLinks(aps)
    cables=cablesImporter(links)
    links=cables.importCables()
    links=wiki.importBackbones(links)
    
    
    __saveCache(WIKI_CACHE_FILE,aps)
    __saveCache(LINK_CACHE_FILE,links)
    '''
    inits=__configToDictonary(config,"wiki")
    wiki=wikicache.wikiImporter(inits)
    wiki.loadAPTemplates()
    
    monitor=wikimonitor.wikimonitor(inits)
    logging.log(logging.DEBUG, "start Wikimonitoring...")
    for p in monitor.getNewAccessPointPages():
        print p
    '''

