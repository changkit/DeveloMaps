//var server = "http://localhost:8081";
var map;

function expand() {
    addProj();
    document.reload();
}

function initialize() {
    alert('init');
    geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(36.366203,-95.00);
    var myOptions = {
	zoom: 3,
	center: latlng,
	mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    map = new google.maps.Map(document.getElementById("map_preview"), myOptions);
}

function addProj() {
    alert('addproj');
    // Get Project add form from server
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (xmlhttp.readyState==4 && xmlhttp.status==200) {
	  document.getElementById("add_proj").innerHTML = xmlhttp.responseText;
	  document.getElementById("add_button").style.display = 'none';
      }
    }
    xmlhttp.open("GET", server + "/getprojform", true);
    xmlhttp.send();
}