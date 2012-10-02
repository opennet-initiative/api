/*
functionality for mapping Opennet stuff
*/
<!--  <script src='http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAttEBvEvohslM2ILNmTwbJxQPKwSEMYVQ3izDaG3Nju_GNCI9nhT7SUbfaHxXJyjkky0KCQwOGRERvA'></script>-->	

var map
var baseLayers=new Array();
var aps_online, aps_offline, links, links_descr

//Inits OL map and returns it
initMap = function(fullFunctionality){
	var lonlat = new OpenLayers.LonLat();	        
	var zoom = 13;
	proj4326 = new OpenLayers.Projection("EPSG:4326");
	projmerc = new OpenLayers.Projection("EPSG:900913");       
	map = new OpenLayers.Map("map", {
				units: 'm',
				controls: [
					new OpenLayers.Control.KeyboardDefaults(),
					new OpenLayers.Control.Navigation(),
					new OpenLayers.Control.LayerSwitcher({'ascending':false}),
					new OpenLayers.Control.PanZoomBar(),
					new OpenLayers.Control.MousePosition(),
					new OpenLayers.Control.Attribution(),
					new OpenLayers.Control.ScaleLine()],
				units: 'm',
				projection: projmerc,
				displayProjection: proj4326,
				numZoomLevels:20
	} );
	if(fullFunctionality)
	{
		controlsExt=[new OpenLayers.Control.ArgParser(),
					new OpenLayers.Control.Permalink(),					
					new OpenLayers.Control.KeyboardDefaults()];
					//new OpenLayers.Control.Measure()
		map.addControls(controlsExt);
	}
	return map;
}

//add basic raster layers
addBaseLayers = function(){
	baseLayers.push(new OpenLayers.Layer.XYZ('MapQuest', 'http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png', { lid: 'mapquest',attribution:'Data CC-By-SA by <a href="http://www.openstreetmap.org">OpenStreetMap</a><br>Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png">'}));
	osmmap=new OpenLayers.Layer.OSM("OpenStreetMap");
	osmmap.setOpacity(0.7);
	baseLayers.push(osmmap);
	baseLayers.push(new OpenLayers.Layer.WMS( "Amtliche Luftbilder","http://www.geodaten-mv.de/dienste/adv_dop", {layers: 'adv_dop'} ));
	map.addLayers(baseLayers);
}

//add interactive vector layers
function addOverlays(autoRefresh,autoCenter,dynamicData,apOnlineURLPath,apOfflineURLPath,linksURLPath)
	{
		
		// allow testing of specific renderers via "?renderer=Canvas", etc
		var renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
		renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;
		//------Nodes----
		
	var nodeStyle = new OpenLayers.Style({
		//text
		label: "${getLabel}",
		fontSize: "10px",
		fontFamily: "Calibri, Verdana, Arial, sans-serif",
		labelAlign: "lt",
		title: "${getTitle}",
		//shape
		fill: true,
		fillColor: "#1588eb",
		fillOpacity: 0.8,
		stroke: true,
		strokeColor: "#2004dd",
		strokeOpacity: 0.8,
		strokeDashstyle: 'solid',
		pointRadius: 4,
		strokeWidth: 1
	},{context: {
		getLabel: function(feature) {
			if (showLabels)
			{
                return getID(feature.data.id);
             }
             else return "";
        },
        getTitle: function(feature) {
			return getID(feature.data.id);
        }
	}});
	var statesStyles = {
	    3: { //offline
			fillColor: "grey",
			fillOpacity: 0.5,
			strokeColor: "black",
			strokeOpacity: 0.5
			},
		1: { //flapping
			fillColor: "red",
			strokeOpacity: 0.3
			},
		0:{						
			} // online don't override nodestyle detaults
	}
	var wifidogStyles = {
	    "1": {
			strokeColor: 'green',
			strokeOpacity: 0.5,
			strokeWidth: 30
			}
	} 
	
	var ugwStyles = {
	    "1": {
			strokeColor: 'yellow',
			strokeOpacity: 1.0,
			strokeWidth: 3
			}
	}

/*	//Zeigt APs an, die keine ondataservice Nachrichten per OLSR senden
 * var debugstyle = new OpenLayers.Style({
		//text
		fontSize: "10px",
		fontFamily: "Calibri, Verdana, Arial, sans-serif",
		labelAlign: "lt",
		title: "${getTitle}",
		//shape
		fill: true,
		fillColor: "${getFill}",
		stroke: true,
		strokeColor: "#2004dd",
		strokeOpacity: 0.8,
		strokeDashstyle: 'solid',
		pointRadius: 4,
		strokeWidth: 1
	},{context: {
		getFill: function (feature) {
			if (feature.data.board == null)
			{
				return "red";
			}
			else return "green";
		},
        getTitle: function(feature) {			
			return getID(feature.data.id);
        }
	}});
*/	
//	var nodesStyleMap =new OpenLayers.StyleMap({"default": debugstyle})
	var nodesStyleMap =new OpenLayers.StyleMap({"default": nodeStyle})
	nodesStyleMap.addUniqueValueRules("default", "state", statesStyles);
	nodesStyleMap.addUniqueValueRules("default", "wifidog", wifidogStyles);
	nodesStyleMap.addUniqueValueRules("default", "ugw", ugwStyles);
	//determine behaviour
	if(autoCenter)
	{
		listeners={"featuresadded": allDataLoaded};
	}
	else
	{
		listeners=null;
	}
	if(dynamicData)
	{
		strategies1=[new OpenLayers.Strategy.BBOX()];
		strategies2=[new OpenLayers.Strategy.BBOX()];
		strategies3=[new OpenLayers.Strategy.BBOX()];
	}
	else
	{
			
		strategies1=[new OpenLayers.Strategy.Fixed()];
		strategies2=[new OpenLayers.Strategy.Fixed()];
		strategies3=[new OpenLayers.Strategy.Fixed()];	

	}
	if(autoRefresh)
	{
		timer1=new OpenLayers.Strategy.Refresh({interval:60000,force:true}); //#WORKAROUNG with OL 2.12 you can't use only one single timer for n events
		timer2=new OpenLayers.Strategy.Refresh({interval:60000,force:true});
		timer3=new OpenLayers.Strategy.Refresh({interval:60000,force:true}); 
		strategies1.push(timer1);
		strategies2.push(timer2);
		strategies3.push(timer3);
	}
	
	aps_online=new OpenLayers.Layer.Vector("APs online",{
		renderers: renderer,
		projection:proj4326,
		protocol:new OpenLayers.Protocol.HTTP({
			url: BASE_URL+apOnlineURLPath, //'/nodes/online/',
			format:new OpenLayers.Format.GeoJSON()
		}),
		eventListeners: listeners, //had been set before object is created
		strategies:strategies1,
		styleMap: nodesStyleMap
	});	
	aps_offline=new OpenLayers.Layer.Vector("APs offline",{
		renderers: renderer,
		projection:proj4326,
		protocol:new OpenLayers.Protocol.HTTP({
			url: BASE_URL+apOfflineURLPath, //'/nodes/offline/',
			format:new OpenLayers.Format.GeoJSON()
		}),
		strategies:strategies2,
		styleMap: nodesStyleMap,
		visibility:false
	});
	//Links
	var linksStyle = new OpenLayers.Style({
		strokeOpacity: "${getOpacity}",
		strokeColor: "${getColor}",
		strokeWidth: "${getWidth}"},{
		context: {			
			getOpacity:function(feature) {
				if(feature.data.cable)
				{
						return 0.1;
				};
			},			
			getColor:function(feature) {
				return feature.data.etxcolor;
			},
			getWidth:function(feature) {
				if (feature.data.backbone)
				{
					return 3;
				}
			}
		}
	});
	linksStyleMap=new OpenLayers.StyleMap({"default": linksStyle});
	links=new OpenLayers.Layer.Vector("Links",{
		projection:proj4326,
		protocol:new OpenLayers.Protocol.HTTP({
			url: BASE_URL+linksURLPath,//'/links/online/',
			format:new OpenLayers.Format.GeoJSON()
		}),
		strategies:strategies3,
		styleMap: linksStyleMap,
	});	
		
	
	map.addLayers([aps_online,aps_offline,links]);
	if(autoRefresh)
	{		
		timer1.start();
		timer2.start();
		timer3.start();
	}
	return {
		'aps_online':aps_online,
		'aps_offline':aps_online,
		'links':links		
	}
	}
	
	function initInteraction(){
	//init Interaction
	var select_online = new OpenLayers.Control.SelectFeature(aps_online, {clickout: true,toggle:true,multiple: false,onSelect: nodeSelect,onUnselect:nodeUnselect});
	map.addControl(select_online);
	var select_offline = new OpenLayers.Control.SelectFeature(aps_offline, {clickout: true,toggle:true,multiple: false,onSelect: nodeSelect,onUnselect:nodeUnselect});
	map.addControl(select_offline);		
	select_online.activate();
	select_offline.activate();
}

//make a popup with infos when POI is selected
	function nodeSelect(feature) {
		content=getNodePopupContent(feature.data);
		feature.popup = new OpenLayers.Popup.FramedCloud(null,
							feature.geometry.getBounds().getCenterLonLat(),
							null,
							'<div>'+content+"</div>",
							feature.marker,
							true);
//		feature.popup.minSize=new OpenLayers.Size(250,400);
		feature.popup.autoSize=true;	
		map.addPopup(feature.popup);
    }

	//close popup
	function nodeUnselect(feature) {
		if (feature.popup) {
			map.removePopup(feature.popup);
			feature.popup.destroy();
			feature.popup = null;
		} 
	}
	
	//create popup content for a POI
	function getNodePopupContent(data)
	{
		id=getID(data.id);
		text="<p class='pop_heading'>AP "+id+"</p>";
		text=text+"<div class='pop_text'>"
		text=text+'<table border="0">'
		text=text+getLine("Gerät",getDeviceLink(data.board));
		text=text+getLine("OS",data.os);
		text=text+"</table>"
		text=text+'<br><a href="http://www.opennet-initiative.de/graph/ap.php?ap='+id+'&width=150&height=50&color=001eff&low_color=ff1e00&medium_color=00ff1e&style=AREA&low_style=AREA&medium_style=AREA&lowerlimit=1&range=week"><img src="http://www.opennet-initiative.de/graph/ap.php?ap='+id+'&width=150&height=50&color=001eff&low_color=ff1e00&medium_color=00ff1e&style=AREA&low_style=AREA&medium_style=AREA&lowerlimit=1&range=day" alt="Verlauf ETX (klicken für Wochenübersicht)" title="Verlauf ETX (klicken für Wochenübersicht)" width="247" height="137px"/></a>';
		text=text+'<br>Zuletzt gesehen:<br>'+data.lastonline+"UTC";
		text=text+'<br><br><a href="http://wiki.on-i.de/wiki/AP'+id+'" target="_blank"'+">Wiki</a>"
		text=text+' <a href="http://'+data.id+'" target="_blank"'+">Webinterface</a>"
		text=text+' <a href="http://'+data.id+':8080" target="_blank"'+">OLSRd</a>"
		text=text+"</div>"
		return text;		
	} 
	
	function getLine(cell1,cell2)
	{
		if (cell2==null) cell2="?";
		return "<tr><td>"+cell1+"</td><td>"+cell2+"</td></tr>";
	}
	
	function getID(IP)
	{
		return IP.substr(8);
	}
	
	function getDeviceLink(devStr)
	{
		if (devStr)
		{
			brand=devStr.split(" ")[0];
			remain=devStr.substring(devStr.indexOf(" "));
			return '<a href="http://wiki.on-i.de/wiki/'+brand+'" target="_blank"'+">"+brand+"</a>"+remain;
		}
		else return null;
	}

centerMap = function(){
	pos=new OpenLayers.LonLat(12.12,54.08);//Default: wir zoomen auf Rostock
	if (!map.getCenter())
	{
		map.setCenter(pos.transform(proj4326,projmerc),13)			
	}
}

//add basic raster layers
addBaseLayers = function(){
	baseLayers.push(new OpenLayers.Layer.XYZ('MapQuest', 'http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png', { lid: 'mapquest',attribution:'Data CC-By-SA by <a href="http://www.openstreetmap.org">OpenStreetMap</a><br>Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png">'}));
	osmmap=new OpenLayers.Layer.OSM("OpenStreetMap");
	osmmap.setOpacity(0.7);
	baseLayers.push(osmmap);
	baseLayers.push(new OpenLayers.Layer.WMS( "Amtliche Luftbilder","http://www.geodaten-mv.de/dienste/adv_dop", {layers: 'adv_dop'} ));
	map.addLayers(baseLayers);
}

//autocenter to all APs
function allDataLoaded(event){
            // 'this' is layer
            this.map.zoomToExtent(event.object.getDataExtent());
//            this.map.zoomTo(16);
        }

//returns URL ?x=abc params as dict
function getQueryParams(qs) {

    return OpenLayers.Util.getParameters(window.location.href);
}
