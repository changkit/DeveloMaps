var map;
var geocoder;
var geostatus;

function initialize() {
    geostatus = google.maps.GeocoderStatus.ZERO_RESULTS;
    geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(36.366203,-95.00);
    var myOptions = {
	zoom: 3,
	center: latlng,
	mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    map = new google.maps.Map(document.getElementById("pmap"), myOptions);
}

function codeAddress() {
    var address = document.proj_upload.proj_addr.value;
    return geocoder.geocode( { 'address' : address }, function(results, status) {

      if (status == google.maps.GeocoderStatus.OK) {
	  geostatus = status;

	map.setCenter(results[0].geometry.location);
	var loc = results[0].geometry.location;

	document.proj_upload.lat.value = ""+loc.lat();
	document.proj_upload.lng.value = ""+loc.lng();

	var marker = new google.maps.Marker({
		map: map, 
		position: results[0].geometry.location
	});
      } else {
	  alert("Geocode was not successful for the following reason: " + status);
      }
  });
}

function submitProj(org_id) {
    document.proj_upload.org_id.value = org_id;
    if(document.proj_upload.proj_addr.value == "") {
	alert("Address not supplied");
	return;
    }
    codeAddress();
    document.getElementById("proj_button").innerHTML = "Geocoding...";
    setTimeout("addrCheck()", 3000);
}

function updateProj(proj_id) {
    document.getElementById("proj_id").value = proj_id;
    if(document.proj_upload.proj_addr.value == "") {
	alert("Address not supplied");
	return;
    }
    codeAddress();
    document.getElementById("proj_button").innerHTML = "Geocoding...";
    setTimeout("addrCheck()", 3000);
}

function addrCheck() {
    if(geostatus != google.maps.GeocoderStatus.OK) {
	return;
    }
    document.proj_upload.submit();
}