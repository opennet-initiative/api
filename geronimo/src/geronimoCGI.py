# -*- coding: UTF8 -*-
'''
Created on 01.05.2012

@author: matthias

CGI server script, that creates views on the collected informations
'''

import os
import sys
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, BASE_DIR)

import cherrypy
from cherrypy.lib.static import serve_file
import pickle
import geojson
import geronimo
from primitives import APstat

WIKI_CACHE_FILE = os.path.join(BASE_DIR, "wiki_nodes.cache")
LINK_CACHE_FILE = os.path.join(BASE_DIR, "links.cache")


class Nodes(object):
    '''/nodes subdomain for accesspoints'''
    def index(self):
        '''bring up the about page'''
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return getAboutPage()
    index.exposed = True
    
    def online(self, bbox=None):
        '''returns all online nodes with details'''
        aps = loadCache(WIKI_CACHE_FILE)
        bbox = getBBOX(bbox)        
        cherrypy.response.headers['Content-Type'] = 'application/json'
        reqAps = filterAPs(aps, [APstat.ONLINE, APstat.FLAPPING])
        reqAps = getAPsinBBOX(reqAps, bbox)
        json = getJSONaps(reqAps)
        json = fixJSON(json)    
        return json
    online.exposed = True
    
    def offline(self, bbox=None):
        '''returns all  nodes that are not online'''
        aps = loadCache(WIKI_CACHE_FILE)
        bbox = getBBOX(bbox)        
        cherrypy.response.headers['Content-Type'] = 'application/json'
        reqAps = filterAPs(aps , [APstat.DEAD])
        reqAps = getAPsinBBOX(reqAps, bbox)        
        json = getJSONaps(reqAps)
        json = fixJSON(json)    
        return str(json)
    offline.exposed = True
    

class Links:
    '''/links subdomain for wifi links between 2 APs'''
    def index(self):
        '''bring up the about page'''
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return getAboutPage()
    index.exposed = True
    
    def online(self, bbox=None):
        '''returns all links that are currently visible'''
        links = loadCache(LINK_CACHE_FILE)
        aps = loadCache(WIKI_CACHE_FILE)
        bbox = getBBOX(bbox)
        bbox_aps = getAPsinBBOX(aps, bbox)
        links = getLinksinBBOX(links, bbox_aps)        
        cherrypy.response.headers['Content-Type'] = 'application/json'
        json = getJSONlinks(links, aps)
        json = fixJSON(json)           
        return json
    online.exposed = True
    
    def neighbours(self, ip=None):
        '''returns all links of 1hop neighbours of the node'''        
        aps = loadCache(WIKI_CACHE_FILE)
        links = loadCache(LINK_CACHE_FILE)
        try: 
            accesspoint=aps[ip]
        except:
            raise cherrypy.HTTPError("416 Requested range not satisfiable", "Invalid node IP requested")      
        cherrypy.response.headers['Content-Type'] = 'application/json'
        (reqAps,reqLinks) = getNeighboursNet(aps,links, ip)
        reqAps[ip]=accesspoint;
        json = getJSONlinks(reqLinks,reqAps)
        json = fixJSON(json)    
        return json
    neighbours.exposed = True
    
    def __getIPfromAP(self,ap):
        """ ap=ap123 ap=1.234 ap=123"""
        ap=ap.lower()
        ap=ap.replace("ap","")
        if ap.find(".")>-1:
            ip="192.168."+ap
        else:
            ip="192.168.1."+ap
        return ip
            
    
class Node(object):
    '''/node subdomain for one single accesspoint'''
    def index(self):
        '''bring up the about page'''
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return getAboutPage()
    index.exposed = True
    
    def neighbours(self, ip=None, ap=None):
        '''returns all online 1hop neighbours of the node'''        
        aps = loadCache(WIKI_CACHE_FILE)
        links = loadCache(LINK_CACHE_FILE)
        if ap is not None:
            ip=self.__getIPfromAP(ap)
        try: 
            accesspoint=aps[ip]
        except:
            raise cherrypy.HTTPError("416 Requested range not satisfiable", "Invalid node IP requested")      
        cherrypy.response.headers['Content-Type'] = 'application/json'
        (reqAps,reqLinks) = getNeighboursNet(aps,links, ip)
        reqAps[ip]=accesspoint;
        json = getJSONaps(reqAps)
        json = fixJSON(json)    
        return json
    neighbours.exposed = True
    
    def __getIPfromAP(self,ap):
        """ ap=ap123 ap=1.234 ap=123"""
        ap=ap.lower()
        ap=ap.replace("ap","")
        if ap.find(".")>-1:
            ip="192.168."+ap
        else:
            ip="192.168.1."+ap
        return ip
    
class Root(object):
    '''entry point for HTTP API access.'''       
    nodes = Nodes()
    node = Node()
    links = Links()
    def index(self):
        '''bring up the about page'''
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return getAboutPage()
    index.exposed = True    
  
def getAboutPage():
    '''bring up the about page'''
    return serve_file(os.path.join(current_dir, 'www', "about.html"),
                                    content_type ='text/html')

#now backend stuff

def loadCache(filename):
    '''loads node and link cache'''
    fcache = file(filename,"r")
    objects = pickle.load(fcache)
    fcache.close()
    return objects

def getJSONaps(nodes):
    '''transforms AP list to a geoJSON list'''
    items = ""
    for ap in nodes.values():
        if ap.state != APstat.UNUSED:
            items = items + getJSONap(ap)+","
    items = items[:len(items)-1]
    return '{ "type": "FeatureCollection","features": ['+items+']}'

def getJSONap(ap):
    '''returns geoJSON representation of one node'''
    try:        
        geometry = geojson.dumps(ap.position)
    except:
        print "AP unserialisable: " + ap.id
    _tmp = ap.__dict__
    del _tmp["position"]
    properties = str(getJSONProperties(_tmp)).replace("'", '"')
    feature = '{ "type": "Feature",\
            "geometry": '+geometry+',\
            "properties": '+properties+'}'
    return feature

def getJSONlinks(links , aps):
    '''transforms link list to a geoJSON list'''
    items = ""
    for link in links.values():
        item = getJSONlink(link, aps)
        if item is not None:
            items = items + item + ","
    items = items[:len(items)-1]
    return '{ "type": "FeatureCollection","features": ['+items+']}'

def getJSONlink(link,aps):
    '''returns geoJSON representation of one link'''
    c1 = aps[link.ap1].position.coordinates
    c2 = aps[link.ap2].position.coordinates      
    geometry = geojson.LineString([c1, c2])
    if ["", ""] in geometry.coordinates:
        return None
    else:
        geometry = geojson.dumps(geometry)
        _tmp = link.__dict__
        properties = str(getJSONProperties(_tmp)).replace("'", '"')
        feature = '{ "type": "Feature",\
                    "geometry": ' + geometry + ',\
                    "properties": ' + properties + '}'
    return feature

def fixJSON( json):
    '''Workaround to keep a generic parsing simple'''
    json = json.replace("None", "null")
    json = json.replace("True", "true")
    return json

def getBBOX(strBBox):
    '''transforms BBOX string to list'''
    if not strBBox == None:
        bbox = []
        items = strBBox.split(",")
        for i in items:
            bbox.append(float(i))
        return bbox
    else:
        return None

def getAPsinBBOX(aps, bbox):
    '''search the bbox area for APs within'''
    if not bbox == None:
        left = bbox[0]
        bottom = bbox[1]
        right = bbox[2]
        top = bbox[3]
        filtered_aps = {}
        for ap in aps.values():
            try: #we skip APs without positions
                x = ap.position.coordinates[0]
                y = ap.position.coordinates[1]
                if x != "" and y != "":
                    if x > left and x < right:
                        if y > bottom and y < top: #AP is in BBOX
                            filtered_aps[ap.id] = ap
            except:
                pass
        return filtered_aps
    else:
        return aps
    
def getLinksinBBOX(links,bbox_aps):
    '''returns links touching the BBOX'''
    filtered_links = {}
    for link in links.values():
        if (link.ap1 in bbox_aps.keys()) or (link.ap2 in bbox_aps.keys()):
            LinkID = link.ap1 + "-" + link.ap2
            filtered_links[LinkID] = link
    return filtered_links

def filterAPs(aps, states):
    '''returns list with AP in states [x,y,z]'''
    filtered_aps = {}
    for ap in aps.values():
        if ap.state in states:
            filtered_aps[ap.id] = ap
    return filtered_aps

def getAPsoffline(aps):
    '''returns list with offline APs'''
    filtered_aps = {}
    for ap in aps.values():
        if ap.state == APstat.DEAD:
            filtered_aps[ap.id] = ap
    return filtered_aps

def getNeighboursNet(aps, links, ip):
    neighbour_links={}
    neighbour_aps={}
    for link in links.values():
        if (link.ap1 == ip) or (link.ap2 == ip): #add AP and the link
            LinkID = link.ap1 + "-" + link.ap2
            neighbour_links[LinkID] = link
            if (link.ap1 == ip):
                neighbour_ap = link.ap2
            else:
                neighbour_ap = link.ap1
            neighbour_aps[neighbour_ap]=aps[neighbour_ap]
    return (neighbour_aps,neighbour_links)
            
        
def getJSONProperties(props):
    '''returns JSON string for properties array'''
    remain = {}
    for (k,v) in props.items():
        if v is not None:                
            remain[k] = v
    return remain

current_dir = os.path.dirname(os.path.abspath(__file__))
config=geronimo.__initConfig()
inits=geronimo.__configToDictonary(config,"www")
cherrypy.config.update({'environment': inits["environment"],
                        'log.screen': True})

conf = {'/www': {'tools.staticdir.on': True, 
                 'tools.staticdir.dir': os.path.join(current_dir, 'www')
                 }}

if __name__ == "__main__":
    if inits["static_path"] is not None:
        cherrypy.quickstart(Root(), '/api/', config=conf)
else:
    application = cherrypy.Application(Root(), script_name=None, config=conf)

