// Copyright (C) 2015 Francesca Sargent, Dave Griffiths
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

// penryn
var default_lat = 50.169124; 
var default_lon = -5.099244;

// hayle
//var default_lat = 50.187954; 
//var default_lon = -5.424446;
var default_zoom = 15;

function main_map_init_anon (map, options) {
    //If anon
    $('.save_map').hide();
    $('#zone_list').hide();

}

function main_map_init_view (map, options) {
    if (c_longitude) {
	map.setView(new L.LatLng(c_latitude, c_longitude), c_zoom);
    }
    editing = false;
    userid = $('.user_id').val()
    
    if (userid) {
	url = "/json/" + userid
    } else {
	url = "/all-json/"
    }
    
    
    $.ajax({
	type: 'get',
	url: url ,
	success: function(data){
	    
	    var geoJsonLayer = L.geoJson(data).addTo(map);
	    popup = new L.Popup();
	    
	    //console.log(data.features);
	    
	    //$(data.features).each(function(i, d) {
	//	console.log(d.geometry.coordinates[0][0]);
	 //   });
	    
	    geoJsonLayer.eachLayer(function(layer) {
		//console.log(layer.feature.geometry);
		geo_colour = layer.feature.properties.color;
		
		layer.on('click', function() {
		    if (layer.feature.author_id == current_user) {
			open_popup(layer,map)
		    }
		    
		    
		});
		
		
		if (geo_colour != 'none') {
		    var style = {
			fillColor : geo_colour,
			color: geo_colour
		    };
		    
		    layer.setStyle(style);
		}
	    });
	    
	    
	    $('#zone_list span').hover(function() {
		zone_class = $(this).attr('class');
		zone_id = parseInt(zone_class.slice(10));
		
		geoJsonLayer.eachLayer(function(layer) {
		    if (zone_id === layer.feature.id && layer.feature.author_id == current_user) {
			open_popup(layer, map)
		    }
		})
		
	    }, function() {
		close_popup(map);
	    });
	    
	    setup_map(map, options);
	}
    });   
}


// can't pass arguments through leaflet so have to use a lovely global variable
// to store the current editing zone (ignored in viewing mode)
var editing_zone_id = false;

function set_editing_zone(zone_id) {
    editing_zone_id=zone_id;
}

function main_map_init_edit(map, options) {
    editing = true;

    if (c_ghost == "True") {
	$('li:contains("Ghost") input').prop('checked', true);
	$('li:contains("Ghost") input').prop('disabled', true);
	$('#zone_toggle').html('<i class="fa fa-expand"></i></i> Disable Ghost')
    }

    userid = $('.user_id').val()
    if (c_longitude) {
	map.setView(new L.LatLng(c_latitude, c_longitude), c_zoom);
    }

    $.ajax({
	type: 'get',
	url: "/json/" + userid,
	success: function(data){

	    //console.log(data.features);

            // loop over each zone
            data.features.forEach(function(zone) {

            	zone_id = zone.id
                // add the geometry for this zone
		geoJsonLayer = L.geoJson(zone).addTo(map);


                geoJsonLayer.eachLayer(function(layer) {

		    var geo_colour = layer.feature.properties.color;
		    var existing_tags = layer.feature.tags

                    // check the zone id
                    if (zone.id==editing_zone_id) {

                        layer.editing.enable();

                        items = layer.toGeoJSON();

			layer.on('edit', function() {
			    items = layer.toGeoJSON();
			});

			var original_colour = $('#colour').val()
			n_colour = original_colour

			$('#colour').change(function(){
			    n_colour = $(this).val()
			    layer.setStyle({ fillColor : n_colour, color: n_colour})
			})

			$('i.set_default').click(function() {
			    n_colour = original_colour
			    $('#colour').val(n_colour);
			    layer.setStyle({ fillColor : n_colour, color: n_colour})

			})


			if (layer.feature.tags) {
			    $('input[type=checkbox]').each(function() {
				input_name = parseInt(this.name);
				
				for (var i = 0; i < existing_tags.length; i++) {
				    tag_name = existing_tags[i][0]
				    
				    if (input_name === tag_name){
					$('input[name='+input_name+']').prop('checked', true);
				    }
				}
			    })
				} else {
				    var tags = ["No Tags Yet"]
				}
                    } else if (zone.id!=editing_zone_id){
                    	layer.setStyle({ opacity : 0.3})
                    }




		    if (geo_colour != 'none') {
			var style = {
			    fillColor : geo_colour,
			    color: geo_colour
			};

			layer.setStyle(style);
		    }
		    

		});
            });
        }
    });

    setup_map(map, options);

}


function setup_map(map, options) {
    var ghost;

    map.scrollWheelZoom.disable();
    $('.save_map').show();
    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    var drawControl = new L.Control.Draw({
	draw : {
	    polygon: {
		shapeOptions: {
		    color: '#FF6060'
		},
		allowIntersection: false,
		drawError: {
		    color: 'orange',
		    timeout: 1000
		},
		showArea: true,
		metric: false
	    },
	    circle : false,
	    polyline : false,
	    marker: false,
	    rectangle: {
		shapeOptions: {
		    color: '#FF8244'
		},
	    },
	},
	edit: {
	    featureGroup: drawnItems
	}
    });

    //console.log("adding draw control");
    map.addControl(drawControl);

    map.on('draw:created', function (e) {
	var type = e.layerType,
	layer = e.layer;
	drawnItems.addLayer(layer);
	//console.log(drawnItems.toGeoJSON());
	//console.log("added draw control");
    });

    if(editing===true) {
	//console.log("unhiding stuff");
	$('.leaflet-draw').addClass('hide');
	// Get toggling right or move around, then enable editing of existing ghost zones (y) fix zone savin' maybe revert
	$( "#zone_toggle, li:contains('Ghost') input:not(:checked)" ).click(function(e) {
	    $('#zone_toggle').toggleClass('ghost')
	    $('.leaflet-draw').toggleClass('hide');
	    if($('.leaflet-draw:visible').length) {
		//  Ghost enabled

		$('li:contains("Ghost") input').prop('checked', true);
		$('li:contains("Ghost") input').prop('disabled', true);
		$('#zone_toggle').html('<i class="fa fa-expand"></i></i> Disable Ghost')

	    } else {
	   	// Ghost disabled

		$('li:contains("Ghost") input').prop('checked', false);
		$('li:contains("Ghost") input').prop('disabled', false);
		$('#zone_toggle').html('<i class="fa fa-expand"></i></i> Enable Ghost')

		drawnItems.eachLayer(function(e) {
		    map.removeLayer(e);
		})

	    }
	});

    }

    $('.save_map').click(function(e) {
	saveShapes(drawnItems);

    });

    $('.lost').click(function() {
    	map.setView(new L.LatLng(default_lat, default_lon), default_zoom);
    })

    map.on('move', function() {
	zoom = map.getZoom()
	center = map.getCenter();
	latitude = center['lat']
	longitude = center['lng']

	send_data();
    })


}

function saveShapes(layer) {

    if (editing==true) {

	ghost_json = '{"length" : "0"}';

	var shapes = getEditedShapes(items);
	var shape_name = $('#name').val();
	shapes['name'] = shape_name
	shapes['properties']['color'] = n_colour

	var tags_in = []
	var tags_out = []

	$('input[type=checkbox]').each(function() {
	    if (this.checked) {
		tags_in.push(this.name);
	    } else {
		tags_out.push(this.name);
	    }
	});

	shapes['tags_in'] = tags_in;
	shapes['tags_out'] = tags_out;

	var shape_json = JSON.stringify(shapes);

	if ($('#zone_toggle, li:contains("Ghost") input').is(':checked')) {
	    // If this is checked, any items in the drawnItems layer will be added as a new feature layer
	    ghost = layer.toGeoJSON();

	    if (ghost["features"][0] === undefined) {
		//console.log("Undefined")
	    } else {
		if (ghost[0] !== null || ghost[0] != undefined) {
		    // Adding colour parameters etc just for clarity
		    ghost['tags_in'] = tags_in;
		    ghost['tags_out'] = tags_out;
		    ghost['name'] = shape_name;
		    // ghost['properties']['color'] = n_colour;

		    ghost_json = JSON.stringify(ghost);

		} else {
		    //console.log("Null")
		}
	    }
	}


    } else {
	shapes = getShapes(layer);
	shape_json = JSON.stringify(shapes)
	ghost_json = JSON.stringify([{"length" : 0}]);
    }

    $.post( "/json-send/", { shapes: shape_json, ghost: ghost_json})
	.done(function( data ) {
            $('.shapes-saved').show(1000, function() {
        	window.location.replace("/userpage/");
            })
	}).fail(function() {
	    $('.shapes-failed').show(1000, function() {
		$(this).hide(5000)
	    })
	});

}

var getEditedShapes = function(shape_layer) {

    var shapes = shape_layer;

    return shapes
}

var getShapes = function(shape_layer) {

    var shapes = [];

    shape_layer.eachLayer(function(layer) {
	var co_ords_geo = layer.toGeoJSON();

	if (co_ords_geo.geometry.type !== "Point") {
	    var fill_colour = layer._path.attributes.stroke.nodeValue;
	    co_ords_geo.properties.fillColor = fill_colour;
	    co_ords_geo.properties.color = fill_colour;
	    shapes.push(co_ords_geo)
	} else {
	    shapes.push(co_ords_geo)
	}

    });

    return shapes;
};

function open_popup(layer, map) {
    if (layer.feature.name) {
	name = layer.feature.name;
    } else {
	name = "No Name Yet";
    }

    if (layer.feature.tags) {
	all_tags = layer.feature.tags;
	tag_names = []
	for (i = 0; i < all_tags.length; i++) {
	    tag_names.push(all_tags[i][1]);
	}
    } else {
	tag_names = ["No Tags Yet"]
    }


    bounds = layer.getBounds();
    popupContent = "<strong>"+name+"</strong><br/><a href='/zone/"+layer.feature.id+"/'>Edit Zone</a><hr/><strong>Assigned Tags: </strong><br/>" + tag_names.join(",");
    popup.setLatLng(bounds.getCenter());
    popup.setContent(popupContent);
    map.openPopup(popup);
}

function close_popup(map) {
    map.closePopup(popup)
}

function send_data() {
    $.ajax({
	type: 'get',
	url: '/location/' + latitude + '/' + longitude + '/' + zoom
    });
}

///////////////////////////////////////////////////////////////

function do_leaflet_view() {
    $(document).ready(function() {
	var map = L.map('map').setView([default_lat, default_lon], default_zoom);


	//L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
	//    maxZoom: 20,
	//    subdomains:['mt0','mt1','mt2','mt3']
	//}).addTo(map);

	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    maxZoom: 20,
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);

	//L.tileLayer('/media/tiles/esri/{z}/{x}/{y}.jpg',{	    
	//    maxZoom: 19,
	//}).addTo(map);
	
	//console.log("viewing only...");
	editing=false;
	main_map_init_view(map); 

	add_geojson(map,0.2,"hayle-01/temp_points.geojson");	
	add_geojson(map,1,"hayle-lake/temp_points.geojson");	

    });
}

function do_leaflet_edit(zone_id) {
    $(document).ready(function() {
	var map = L.map('map', {drawControl: true}).setView([default_lat, default_lon], default_zoom);


	//L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
	//    maxZoom: 20,
	//    subdomains:['mt0','mt1','mt2','mt3']
	//}).addTo(map);

//	L.tileLayer('/media/tiles/esri/{z}/{x}/{y}.jpg',{	    
//	    maxZoom: 19,
//	}).addTo(map);
	
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    maxZoom: 20,
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);
	
	editing=true;
	//console.log("editing zone id:"+zone_id);
	set_editing_zone(zone_id);
	main_map_init_edit(map); 
	
    });
}

function add_geojson(map,max_expand,filename) {
/*    var mydata = $.ajax({
        url:"/media/geojson/"+filename,
        dataType: "json",
        success: function(data) {
	    console.log("GeoJSON data successfully loaded.")

	    myarray = []
	    min = 9999;
	    max = 0;

            //grab the xyz data from the array
            data.features.forEach(function(feature){
		point_array = []
		point_array.push(feature.geometry.coordinates[1])
		point_array.push(feature.geometry.coordinates[0])
		if (feature.properties.temp<min) min=feature.properties.temp;
		if (feature.properties.temp>max) max=feature.properties.temp;
		point_array.push(feature.properties.temp)
		myarray.push(point_array)
            });

	    max=min+max_expand;

	    console.log(min);
	    console.log(max);
	    

	    //using an array with xyz, plot the hotline
	    var hotlineLayer = L.hotline(myarray, {
		min: min,
		max: max,
		//viridis colour palette
		palette: {
		    0.0: '#440154FF',
		    0.05: '#481567FF',
		    0.1: '#482677FF',
		    0.15: '#453781FF',
		    0.2: '#404788FF',
		    0.25: '#39568CFF',
		    0.3: '#33638DFF',
		    0.35: '#2D708EFF',
		    0.4: '#287D8EFF',
		    0.45: '#238A8DFF',
		    0.5: '#1F968BFF',
		    0.55: '#20A387FF',
		    0.6: '#29AF7FFF',
		    0.65: '#3CBB75FF',
		    0.7: '#55C667FF',
		    0.75: '#73D055FF',
		    0.8: '#95D840FF',
		    0.85: '#B8DE29FF',
		    0.9: '#DCE319FF',
		    1: '#FDE725FF',
		},
		weight: 4.5,
		outlineColor: '#8c8c8c',
		outlineWidth: 1
	    }).addTo(map);


	}
    });
*/    
}
