/* Functions used for DeveloMaps form checking */

  var geocoder;
  var map;
  function initialize() {
    geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(36.366203,-95.00);
    var myOptions = {
      zoom: 3,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    map = new google.maps.Map(document.getElementById("map_preview"), myOptions);
  }
 
  function codeAddress() {
    var address = document.org_upload.addr.value;
    //alert(address);
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);
	var loc = results[0].geometry.location;
	document.org_upload.lat.value = ""+loc.lat();
	document.org_upload.lng.value = ""+loc.lng();
        var marker = new google.maps.Marker({
            map: map, 
            position: results[0].geometry.location
        });
      } else {
	  alert("Geocode was not successful for the following reason: " + status);
      }
	});
  }


function submitOrg() {
    if(document.org_upload.logo.value == "") {
	alert("Logo not supplied");
	return;
    }
    else if(document.org_upload.addr.value == "") {
	alert("Address not supplied");
	return;
    }
    //else if(document.org_upload.phone.value == "") {
    //	alert("Phone not supplied");
    //}
    //else if(document.org_upload.email.value == "") {
    //	alert("email not supplied");
    //}
    codeAddress();
    document.org_upload.submit();
}