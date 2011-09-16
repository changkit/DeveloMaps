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
    map = new google.maps.Map(document.getElementById("map_preview"), myOptions);
}

function showAddress() {
    var addr = document.getElementById("address").value;
    codeAddress(addr);
}

function codeAddress(address) {

    return geocoder.geocode( { 'address' : address }, function(results, status) {

      if (status == google.maps.GeocoderStatus.OK) {
	  geostatus = status;

	map.setCenter(results[0].geometry.location);
	var loc = results[0].geometry.location;

	document.getElementById("lat").value = ""+loc.lat();
	document.getElementById("lng").value = ""+loc.lng();

	var marker = new google.maps.Marker({
		map: map, 
		position: results[0].geometry.location
	});
	map.setZoom(6);

      } else {
	  alert("Geocode was not successful for the following reason: " + status);
      }
  });
}

function submitProj(org_id) {
    document.proj_upload.org_id.value = org_id;

    var address = document.upload.proj_addr.value;

    if(address == "") {
	alert("Address not supplied");
	return;
    }

    codeAddress(address);
    document.getElementById("submit_proj").innerHTML = "<h1>Geocoding...</h1>";
    setTimeout("addrCheck(document.upload)", 3000);
}

function updateProj(proj_id) {
    document.getElementById("proj_id").value = proj_id;

    var address = document.upload.proj_addr.value;
    if(document.proj_upload.proj_addr.value == "") {
	alert("Address not supplied");
	return;
    }
    codeAddress(address);

    document.getElementById("submit_proj").innerHTML = "<h1>Geocoding...</h1>";
    setTimeout("addrCheck(document.upload)", 3000);
}

function submitOrg() {
    var address = document.org_upload.addr.value;

    if(document.org_upload.logo.value == "") {
	alert("Logo not supplied");
	return;
    }
    else if(address == "") {
	alert("Address not supplied");
	return;
    }
    codeAddress(address);
    document.getElementById("org_submit").innerHTML = "Geocoding...";

    //document.org_upload.submit();
    setTimeout("addrCheck(document.org_upload)", 1000);
}

function updateOrg(org_id) {
    document.getElementById("org_id").value = org_id;

    var address = document.upload.addr.value;

    if(document.upload.logo.value == "") {
	alert("Logo not supplied");
	return;
    }

    if(address == "") {
	alert("Address not supplied");
	return;
    }
    codeAddress(address);
    document.getElementById("org_update").innerHTML = "Geocoding...";
    setTimeout("addrCheck(document.upload)", 3000);
}

function addrCheck(upload_form) {
    if(geostatus != google.maps.GeocoderStatus.OK) {
	return;
    }
    upload_form.submit();
}

