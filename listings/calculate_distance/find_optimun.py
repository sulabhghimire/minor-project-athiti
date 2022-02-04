import geocoder
from haversine import haversine

def near_places(dest_lat, dest_lng):
    g = geocoder.ip('me')
    origin = tuple(g.latlng)

    destination = (dest_lat, dest_lng)

    distance    = haversine(origin, destination)

    return distance