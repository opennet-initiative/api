var map
var baseLayers=new Array();

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

centerMap = function(){
	pos=new OpenLayers.LonLat(12.12,54.08);//Default: wir zoomen auf Rostock
	if (!map.getCenter())
	{
		map.setCenter(pos.transform(proj4326,projmerc),13)			
	}
}
