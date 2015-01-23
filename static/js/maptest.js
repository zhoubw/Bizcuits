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

function loadScript(){
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "http://maps.googleapis.com/maps/api/js?key=&sensor=false&callback=initialize";
    document.body.appendChild(script);
}

