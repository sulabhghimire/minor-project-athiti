#python script

GOOGLE_MAPS_API_KEY  = 'AIzaSyBOy_NqTd4raZcqkEx7aExmO90dKiABBys'

import geocoder
g = geocoder.ip('me')


from math import sin, cos, sqrt, atan2, radians
lat1 = radians(g.latlng[0])
lon1 = radians(g.latlng[1])

lat1 = radians(28.214032)
lon1 = radians(83.977331)
# approximate radius of earth in km
R = 6373.0

lat2 = radians(28.147677895956406)
lon2 = radians(84.08262946158553)

dlon = lon2 - lon1
dlat = lat2 - lat1

a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
c = 2 * atan2(sqrt(a), sqrt(1 - a))

distance = R * c

print("Result:", distance)
print("Should be:", 14.5, "km")