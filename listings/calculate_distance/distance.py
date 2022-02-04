from turtle import distance
import geocoder
from haversine import haversine

def calculate_distance(dest_lat, dest_lng):

    g = geocoder.ip('me')
    origin = tuple(g.latlng)

    destination = (dest_lat, dest_lng)

    distance    = haversine(origin, destination)

    return f'{round(distance, 3)} km'

