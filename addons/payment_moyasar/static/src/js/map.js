console.log("hello one")
var marker;
var apiID = "AIzaSyC2gtduZdR-zfHJfGUpTgRgvbHVqq2kW4c"
    // function myMap1() {
    //     var mapProp = {
    //         center: new google.maps.LatLng(51.508742, -0.120850),
    //         zoom: 5,
    //     };
    //     var map = new google.maps.Map(document.getElementById("map"), mapProp);
    // }


// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see the error "The Geolocation service
// failed.", it means you probably did not give permission for the browser to
// locate you.
// let map, infoWindow;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 21.4858, lng: 39.1925 },
        zoom: 15,
    });
    infoWindow = new google.maps.InfoWindow();
    //console.log(map.place)
    const locationButton = document.createElement("button");

    locationButton.textContent = "Pan to Current Location";
    locationButton.classList.add("custom-map-control-button");
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(locationButton);
    myLocation()
    locationButton.addEventListener("click", () => {
        // Try HTML5 geolocation.
        myLocation()
    });

    google.maps.event.addListener(map, 'click', function(event) {
        placeMarker(event.latLng);
    });

}

function placeMarker(location) {
    if (marker)
        marker.setMap(null);
    marker = new google.maps.Marker({
        position: location,
        map: map
    });
}

function myLocation() {
    if (marker)
        marker.setMap(null);
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                var latitude = position.coords.latitude
                var longitude = position.coords.longitude
                const myLatLng = { lat: latitude, lng: longitude };
                marker = new google.maps.Marker({
                    position: myLatLng,
                    map,
                    title: placeMarker.name,
                });
                // infoWindow.setPosition(pos);
                // infoWindow.setContent(position.);
                // infoWindow.open(map);
                map.setCenter(pos);

                resolvePlace(pos,
                    function(place) {

                        // var marker = new google.maps.Marker({
                        //     title: place.formatted_address,
                        //     map: map,
                        //     position: pos
                        // });


                        //infoWindow.setPosition(pos);
                        infoWindow.setContent(place.formatted_address);
                        map.setCenter(pos);
                        infoWindow.open(map, marker);

                    },
                    function(status) {
                        infoWindow.setPosition(pos);
                        infoWindow.setContent('Geocoder failed due to: ' + status);
                    });
            },

            () => {
                handleLocationError(true, infoWindow, map.getCenter());
            }
        );
    } else {
        // Browser doesn't support Geolocation
        handleLocationError(false, infoWindow, map.getCenter());
    }
}

function resolvePlace(pos, success, error) {

	var geocoder = new google.maps.Geocoder;
	geocoder.geocode({ 'location': pos }, function (results, status) {
		if (status === google.maps.GeocoderStatus.OK) {
			if (results[0]) {
				success(results[0]);
			} else {
				error('No results found');
			}
		} else {
			error(status);
		}
	});

}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(
        browserHasGeolocation ?
        "Error: The Geolocation service failed." :
        "Error: Your browser doesn't support geolocation."
    );
    infoWindow.open(map);
}

window.initMap = initMap;