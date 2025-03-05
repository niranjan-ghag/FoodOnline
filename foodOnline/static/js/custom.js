// Initialize Google Places Autocomplete
let autocomplete;

function initAutoComplete() {
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode','establishment'],
        componentRestrictions: {'country': ['in']},
    })
    
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged(){
    var place = autocomplete.getPlace();
    console.log(place)
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start Typing..";
    }
    else{
        console.log('place name=>', place.name)
    }
}
