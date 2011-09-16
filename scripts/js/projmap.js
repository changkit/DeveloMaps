/* Functions used for DeveloMaps */

var map;
var geocoder;
var geostatus;

/*
  Array of ProjInfo
    - marker
    - ID
    - title
    - tags
*/
var markersArray = [];
var filtersArray = [];


/*

jQuery ready script

*/

$(document).ready(function() {
  $('#menu ul li strong').click(function() {
    $('#menu ul li ul').slideToggle('fast');
  });
  $('#menu ul li').mouseover(
    function() {$(this).addClass('hover')}
  ).mouseout(
    function() {$(this).removeClass('hover')});

  $('.plink').click(function() {
    alert('poop');
    //show_org($(this).attr("id"));
  });

  $('.data_feed button').click(function() {
    $('#menu ul li ul').slideToggle('fast');
  });
});


var minZoomLevel = 3;

function initialize() {

    var myLatlng = new google.maps.LatLng(13.923404,-84.902344);
    geocoder = new google.maps.Geocoder();
    var myOptions = {
    	zoom: 5,
        center: myLatlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    google.maps.event.addListener(map, 'idle', showMarkers);
    addShortcut();
    
    // Limit Zoom Level
    google.maps.event.addListener(map, 'zoom_changed', function() {
     if (map.getZoom() < minZoomLevel) map.setZoom(minZoomLevel);
    });
}

function showMarkers() {

    // In the AJAX callback, delete the current markers
    // and add new markers.

    // Request Marker data in JSON format    
    var xmlhttp;
    var jsontext;
    xmlhttp = new XMLHttpRequest();
    
    xmlhttp.onreadystatechange = function() {

	if (xmlhttp.readyState==4 && xmlhttp.status==200) {

	    // Delete all current markers

	    clearMarkers();

	    jsontext = xmlhttp.responseText;
	    //alert('jsontext = ' + jsontext);
	    
	    var data = jsontext.evalJSON();
	    var idx;
	    var latlng;
	    var coords;
	    var tag_list;
	    
	    $('#feed_content').html('');
	    
	    for(idx = 0; idx < data.length; idx++) {
		coords = data[idx];
		latlng = new google.maps.LatLng(coords.lat, coords.lng);
		tag_list = coords.tags;
		placeMarker(latlng, coords.title, coords.id, tag_list);

		// Make this a link to the project page
		var content = "<strong onclick=\"show_project(" + coords.id +");\"";
		content += " class=\"plink\"><u>" + coords.title + "</u></strong><br/>";
		content += tag_list + "<br/><br/>";
		
		// Fill project feed with data about markers
		$('#feed_content').append(content);
	    }	    
	}
    }

    // Get the current viewport bounds
    var bounds = map.getBounds();
    var req = "getlocs?bounds=" + bounds.toUrlValue();
    //alert(req);

    // Call server passing it the bounds
    xmlhttp.open("GET", server + req, true);
    xmlhttp.send();
}

// Which marker is bouncing?
//var bouncer = null;

function placeMarker(location, title, id, tags) {

  var marker = new google.maps.Marker({
      position: location, 
      map: map,
      title: title
  });

  // Get the comment
  var title = marker.getTitle();

  // Asynchronous request
  var xmlhttp;

  // Add a click listener for this marker
  google.maps.event.addListener(marker,
				'click',
				function() {     
    show_project(id);
  });

  proj_info = new ProjInfo(marker, tags);
  markersArray.push(proj_info);
  //alert(tags);
}

var tmp_feed = null;

function restore() {
    $('#feed_content').html(tmp_feed);
}

function show_project(id) {

    var xmlhttp = new XMLHttpRequest();
    var old_content = $('#feed_content').html();
    tmp_feed = old_content;

    
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState==4 && xmlhttp.status==200) {      
	    //document.getElementById('feed_content').innerHTML = xmlhttp.responseText;
	    $('#feed_content').html(xmlhttp.responseText);
	    $('#feed_content').append('<button id="restore" onclick=\"restore()\">&laquo Back to List</button>');
        }
    }
    //alert('sending GET');
    xmlhttp.open("GET", server + "getdata?key=" + id, true);
    xmlhttp.send();
}

var search_mode = false;

function search() {
    var query = document.getElementById('query').value;
    //alert(query);
    geocoder.geocode({ 'address' : query }, 
		     function(results, status) {
				
	if (status == google.maps.GeocoderStatus.OK) {
	  geostatus = status;

	  map.fitBounds(results[0].geometry.viewport);

	} else {
	    alert("Geocode was not successful for the following reason: " + status);
	}
    });
    document.getElementById('query').value="";
    //shortcut.add("tab", togglesearch);
    $('#query').blur();
    search_mode = false;
    shortcut.add("f", dropdown);
}

function dropdown() {
    if(document.getElementById("query") != document.activeElement) {
	$("#menu ul li ul").slideToggle('fast');
    }
}

function togglesearch() {
    if(search_mode) {
        search_mode = false;
	shortcut.add("f", dropdown);
        $('#query').blur();
    }
    else {
        search_mode = true;
	shortcut.remove("f");
        $('#query').focus();
    }
}

function addShortcut() {
    shortcut.add("f", dropdown);
    shortcut.add("tab", togglesearch)
}

// ProjInfo class stores metadata about a marker
function ProjInfo(marker, tags) {
    this.marker = marker;
    this.tags = tags;
}

function filter(tag) {
    if(tag.checked == true) {

	// Enable this filter
	filtersArray.push(tag.name);

	//alert('filter on ' + tag.name);

	for(m in markersArray) {
	    var proj_tags = markersArray[m].tags;

	    if(proj_tags.indexOf(tag.name) < 0) {
		//alert(tag.name);
		markersArray[m].marker.setVisible(false);
	    }
	}
    }
    else {
	// Disable this filter

	//alert('disable filter on ' + tag.name);

	// Remove this tag from the filters
	var idx = filtersArray.indexOf(tag.name);
	if(idx >= 0) {
	    filtersArray.splice(idx, 1);
	}

	// Adjust the markers
	var numMarkers = markersArray.length;
	for(var i = 0; i < numMarkers; i++) {

	    var filtered = false;
	    var proj_tags = markersArray[i].tags;

	    // Check if we can now show this marker
	    var numFilters = filtersArray.length;
	    for(var j = 0; j < numFilters; j++) {

		var fl = filtersArray[j];
		
		if(proj_tags.indexOf(fl) < 0) {
		    filtered = true;
		    break;
		}		
	    }
	    if(!filtered) {
		markersArray[i].marker.setVisible(true);
	    }
	}
	
    }
}

function clearMarkers() {
    if(markersArray) {
	var numMarkers = markersArray.length;
	//alert(numMarkers);
	for(var i = 0; i < numMarkers; i++) {
	    markersArray[i].marker.setMap(null);
	}
    }
}
