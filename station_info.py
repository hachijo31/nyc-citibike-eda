import geopy.distance

city_hall_latitude = 40.712772
city_hall_longitude = -74.006058


class station_info:
    def __init__(self, station_id, name, latitude, longitude, first_use):
        self.id = station_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.first_use = first_use
        self.latest_use = first_use
        self.relocation_history = []
        self.add_distance_to_city_hall(city_hall_latitude, city_hall_longitude)
        self.stations_in_buffer = []

    def refresh(self, name, latitude, longitude, latest_use):
        if latitude != self.latitude or longitude != self.longitude:
            p1 = (self.latitude, self.longitude)
            p2 = (latitude, longitude)
            distance = geopy.distance.distance(p1, p2).km * 1000
            self.relocation_history.append([distance, self.name, self.latitude, self.longitude])
            self.name = name
            self.latitude = latitude
            self.longitude = longitude
            self.add_distance_to_city_hall(city_hall_latitude, city_hall_longitude)
        if self.latest_use < latest_use:
            self.latest_use = latest_use

    def add_distance_to_city_hall(self, city_hall_latitude, city_hall_longitude):
        #XXX 直線距離にしているが、走行距離に直すべき
        p1 = (self.latitude, self.longitude)
        p2 = (city_hall_latitude, city_hall_longitude)
        distance = geopy.distance.distance(p1, p2).km * 1000
        self.distance_to_city_hall = distance

    def add_station_in_buffer(self, station, buffer_length):
        p1 = (self.latitude, self.longitude)
        p2 = (station.latitude, station.longitude)
        distance = geopy.distance.distance(p1, p2).km * 1000
        if distance <= buffer_length:
            self.stations_in_buffer.append([distance, station.id, station.name, station.first_use, station.latest_use])
            self.stations_in_buffer = sorted(self.stations_in_buffer, key=lambda v: v[0])

    def export(self):
        d = {}
        d['station id'] = self.id
        d['station name'] = self.name
        d['latitude'] = self.latitude
        d['longitude'] = self.longitude
        d['first use'] = self.first_use.strftime('%Y-%m-%d')
        d['latest use'] = self.latest_use.strftime('%Y-%m-%d')
        d['number of relocation of the station'] = len(self.relocation_history)
        if d['number of relocation of the station'] > 0:
            d['maximum of relocation distance'] = max(self.relocation_history, key=lambda v: v[0])[0]
        else:
            d['maximum of relocation distance'] = ""
        d['distance to city hall'] = self.distance_to_city_hall
        d['number of stations in buffer'] = len(self.stations_in_buffer)
        if d['number of stations in buffer'] > 0:
            d['closest station distance'] = self.stations_in_buffer[0][0]
            d['closest station id'] = self.stations_in_buffer[0][1]
            d['closest station name'] = self.stations_in_buffer[0][2]
            d['closest station first use'] = self.stations_in_buffer[0][3].strftime('%Y-%m-%d')
            d['closest station latest use'] = self.stations_in_buffer[0][4].strftime('%Y-%m-%d')
        else:
            d['closest station distance'] = ""
            d['closest station name'] = ""
            d['closest station first use'] = ""
            d['closest station latest use'] = " "

        return d
