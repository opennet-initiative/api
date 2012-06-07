'''
Created on 01.05.2012

@author: matthias

CGI server script, that creates views on the collected informations for web clients
'''

import os
import sys
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, BASE_DIR)

import cherrypy
import pickle
import geojson
#import geronimo
from primitives import *

WIKI_CACHE_FILE = os.path.join(BASE_DIR, "wiki_nodes.cache")
LINK_CACHE_FILE = os.path.join(BASE_DIR, "links.cache")


class Nodes(object):
    def index(self):
        cherrypy.response.headers['Content-Type']= 'text/html'
        return "This is GERNOMIO, a datawarehouse to monitor OpenNet wireless infrastructure."
    index.exposed = True
    
    def online(self,bbox=None):
        aps=loadCache(WIKI_CACHE_FILE)
        bbox=getBBOX(bbox)        
        cherrypy.response.headers['Content-Type']= 'application/json'
        reqAps=filterAPs(aps,[APstat.ONLINE,APstat.FLAPPING])
        reqAps=getAPsinBBOX(reqAps,bbox)
        json=getJSONaps(reqAps)
        json = fixJSON(json)    
        return json
    online.exposed = True
    
    def offline(self,bbox=None):
        aps=loadCache(WIKI_CACHE_FILE)
        bbox=getBBOX(bbox)        
        cherrypy.response.headers['Content-Type']= 'application/json'
        reqAps=filterAPs(aps,[APstat.DEAD])
        reqAps=getAPsinBBOX(reqAps,bbox)        
        json=getJSONaps(reqAps)
        json = fixJSON(json)    
        return json
    offline.exposed = True
    

class Links:
    def index(self):
        cherrypy.response.headers['Content-Type']= 'text/html'
        return "This is GERNOMIO, a datawarehouse to monitor OpenNet wireless infrastructure."
    index.exposed = True
    
    def online(self,bbox=None):
        links=loadCache(LINK_CACHE_FILE)
        aps=loadCache(WIKI_CACHE_FILE)
        bbox=getBBOX(bbox)
        bbox_aps=getAPsinBBOX(aps,bbox)
        links=getLinksinBBOX(links,bbox_aps)        
        cherrypy.response.headers['Content-Type']= 'application/json'
        json=getJSONlinks(links,aps)
        json = fixJSON(json)           
        return json
    online.exposed = True
    
    
#entry point for HTTP API access.
class Root(object):       
    nodes=Nodes()
    links=Links()
    def index(self):
        cherrypy.response.headers['Content-Type']= 'text/html'
        return "This is GERNOMIO, a datawarehouse to monitor OpenNet wireless infrastructure. You can read informations via this API using e.g. api/nodes/online"
    index.exposed = True    


#now backend stuff

def loadCache(filename):
    fcache=file(filename,"r")
    objects=pickle.load(fcache)
    fcache.close()
    return objects

def getJSONaps(nodes):
    items=""
    for ap in nodes.values():
        items=items+getJSONap(ap)+","
    items=items[:len(items)-1]
    return '{ "type": "FeatureCollection","features": ['+items+']}'

def getJSONap(ap):        
    geometry=geojson.dumps(ap.position)
    _tmp=ap.__dict__
    del _tmp["position"]
    properties=str(getJSONProperties(_tmp)).replace("'", '"')
    feature='{ "type": "Feature","geometry": '+geometry+',"properties": '+properties+'}'
    return feature

def getJSONlinks(links,aps):
    items=""
    for link in links.values():
        item=getJSONlink(link,aps)
        if item is not None:
            items=items+item+","
    items=items[:len(items)-1]
    return '{ "type": "FeatureCollection","features": ['+items+']}'

def getJSONlink(link,aps):      
    geometry=geojson.LineString([aps[link.ap1].position.coordinates,aps[link.ap2].position.coordinates])
    if ["",""] in geometry.coordinates:
        return None
    else:
        geometry=geojson.dumps(geometry)
        _tmp=link.__dict__
        properties=str(getJSONProperties(_tmp)).replace("'", '"')
        feature='{ "type": "Feature","geometry": '+geometry+',"properties": '+properties+'}'
    return feature

#Workaround to keep parsing simple
def fixJSON( json):
        json = json.replace("None", "null")
        json = json.replace("True", "true")
        return json

def getBBOX(str):
    if not str==None:
        bbox=[]
        items=str.split(",")
        for i in items:
            bbox.append(float(i))
        return bbox
    else:
        return None

def getAPsinBBOX(aps,bbox):
    if not bbox==None:
        left=bbox[0]
        bottom=bbox[1]
        right=bbox[2]
        top=bbox[3]
        filtered_aps={}
        for ap in aps.values():
            try: #we skip APs without positions
                x=ap.position.coordinates[0]
                y=ap.position.coordinates[1]
                if x!="" and y!="":
                    if x>left and x<right:
                        if y>bottom and y<top: #AP is in BBOX
                         filtered_aps[ap.id]=ap
            except:
                pass
        return filtered_aps
    else:
        return aps
    
def getLinksinBBOX(links,bbox_aps):
    filtered_links={}
    for link in links.values():
        if (link.ap1 in bbox_aps.keys()) or (link.ap2 in bbox_aps.keys()):
            id=link.ap1+"-"+link.ap2
            filtered_links[id]=link
    return filtered_links
    pass

def filterAPs(aps,states):
    filtered_aps={}
    for ap in aps.values():
        if ap.state in states:
            filtered_aps[ap.id]=ap
    return filtered_aps

def getAPsoffline(aps):
    filtered_aps={}
    for ap in aps.values():
        if ap.state==APstat.DEAD:
            filtered_aps[ap.id]=ap
    return filtered_aps
        
def getJSONProperties(props):
    remain={}
    for (k,v) in props.items():
        if v is not None:                
            remain[k]=v
    return remain

current_dir = os.path.dirname(os.path.abspath(__file__))
#config=geronimo.__initConfig()
#inits=geronimo.__configToDictonary(config,"www")
#cherrypy.config.update({'environment': inits["environment"], 'log.screen': True})

conf = {'/www': {'tools.staticdir.on': True, 'tools.staticdir.dir': os.path.join(current_dir, 'www')}}

if __name__ == "__main__":
	if inits["static_path"] is not None:
		cherrypy.quickstart(Root(), '/api/', config=conf)
else:
	application = cherrypy.Application(Root(), script_name=None, config=conf)

