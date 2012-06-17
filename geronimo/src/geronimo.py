#!/usr/bin/python
# -*- coding: UTF8 -*-

'''
Created on 13.10.2011

@author: Matthias Meisser

Geronimo is a modular data warehouse for maintaining 
all sources of information by the OpenNet Initiative.

Dependencies (can be installed via PIP): 
    Feedparser    http://code.google.com/p/feedparser/
    Wikitools     code.google.com/p/python-wikitools/
    SimpleJSON    http://code.google.com/p/simplejson/

Usage:
1. Create a conf.ini file and adapt data paths within
2. Invoke python geronimo.py
3. register geronimo as WSGI CGI for Apache

released under the GPL
'''

import os
import sys
import logging
import getopt
import pickle
from ConfigParser import SafeConfigParser

#import helpers.wikimonitor as wikimonitor
import helpers.wikicache as wikicache
import helpers.olsrdstats as olsrdstats
from helpers.lastseen import lastSeenImporter
from helpers.expDB import DBimporter
from helpers.olsrdstats import OLSRDimporter
from helpers.cables import cablesImporter
from primitives import APstat

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")
WIKI_CACHE_FILE = os.path.join(BASE_DIR, "wiki_nodes.cache")
LINK_CACHE_FILE = os.path.join(BASE_DIR, "links.cache")

def __configToDictonary(conf, section):
    '''returns dictionary for the options of the log'''
    dictionary = {}
    for opt, val in conf.items(section):
        dictionary[opt] = val
    return dictionary

def __getLogger():
    '''init logger'''
    handler = logging.StreamHandler(sys.stdout)    
    logger = logging.getLogger() 
    logger.addHandler(handler)
    return logger 

def __parseArgs():
    '''parse #arguments'''
    try:
        opts, rest = getopt.getopt(sys.argv[1:], "d", ["debug"])
    except getopt.GetoptError, err:
        print str(err)
        print "Usage: "#TODO Debuglevel über Config einstellen
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-d","--debug"):
            log.setLevel(logging.DEBUG)
        
def __initConfig():
    '''inits conf'''
    conf = SafeConfigParser()
    logging.log(logging.DEBUG, "loading conf")
    conf.read(CONFIG_FILE)
    return conf

def __markUnused(aps):
    '''Identifies APs that are obviously not in use'''
    for ap in aps.values():
        if ap.position is None:
            ap.state=APstat.UNUSED      

def __printStats(aps, links):
    '''prints results in a single line'''
    ap_online = 0
    for ap in aps.values():
        if (ap.state == APstat.ONLINE) :
            ap_online = ap_online + 1
    print "Finished: %(online)u / %(total)u APs online (%(links)u Links)" % {"online":ap_online, "total":len(aps), "links":len(links)}  

def __saveCache(filename, objects):
    '''serialies object container to file'''
    fcache = file(filename,"w")
    pickle.dump(objects, fcache)
    fcache.close()
        
if __name__ == '__main__':
    log = __getLogger()
    __parseArgs()
    config = __initConfig()
    #update AP state
    inits = __configToDictonary(config, "lastseen")
    ls = lastSeenImporter(inits)
    aps = ls.importLastSeen()
    #crawl wiki
    inits = __configToDictonary(config, "wiki")
    wiki = wikicache.wikiImporter(inits)
    aps = wiki.importAPTable(aps)
    #get AP details
    inits = __configToDictonary(config, "DB")
    db = DBimporter(inits)
    aps =db.importDB(aps)
    #Links
    inits = __configToDictonary(config, "olsrd")
    olsrd = OLSRDimporter(inits)
    links = olsrd.importLinks(aps)
    cables = cablesImporter(links)
    links = cables.importCables()
    links = wiki.importBackbones(links)
    #Finish
    __markUnused(aps)
    __printStats(aps, links)    
    __saveCache(WIKI_CACHE_FILE, aps)
    __saveCache(LINK_CACHE_FILE, links)
    '''
    inits=__configToDictonary(conf,"wiki")
    wiki=wikicache.wikiImporter(inits)
    wiki.loadAPTemplates()
    
    monitor=wikimonitor.wikimonitor(inits)
    logging.log(logging.DEBUG, "start Wikimonitoring...")
    for p in monitor.getNewAccessPointPages():
        print p
    '''
    
    

