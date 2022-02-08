import geocoder
from haversine import haversine

def near_places(orign_lat, origin_lng, dest_lat, dest_lng):
    origin = (orign_lat, origin_lng)

    destination = (dest_lat, dest_lng)

    distance    = haversine(origin, destination)

    return f'{round(distance, 3)} km'