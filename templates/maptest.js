function generateMapProp(lat, lng) {
    var location = new google.maps.LatLng(lat,lng,true) 
    var mapProp = {
	center: location,
	zoom:16,
	mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
    
      var marker = new google.maps.Marker({
	position: location,
	map:map,
	title: "test marker on the zip code"
    });
    marker.setMap(map);
    
}
function initialize() {
    var address = '10282';
    geocoder = new google.maps.Geocoder();
    geocoder.geocode({'address':address}, function(results,status) {
	if (status == google.maps.GeocoderStatus.OK) {
	    var lat = results[0].geometry.location.lat();
	    var lng = results[0].geometry.location.lng();
	    generateMapProp(lat,lng);
	} else {
	    alert("Geocode was not successful for the following reason: " + status)
	}
    });

    
}

function loadScript(){
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "http://maps.googleapis.com/maps/api/js?key=&sensor=false&callback=initialize";
    document.body.appendChild(script);
}

window.onload = loadScript;
