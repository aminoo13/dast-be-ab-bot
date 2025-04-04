from geopy.distance import geodesic

def calculate_distance(coord1, coord2):
    """
    coord1 و coord2 هر دو به صورت (lat, lon) هستند
    خروجی: فاصله بر حسب کیلومتر (float)
    """
    return geodesic(coord1, coord2).km
