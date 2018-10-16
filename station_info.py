import csv
import pickle
import geopy.distance
import censusgeocode as cg
#import multiprocessing as mp
#import threading

city_hall_latitude = 40.712772
city_hall_longitude = -74.006058
mesh_pickle_path = "data/mesh.pickle"


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
            p2 = (float(latitude), float(longitude))
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

    def add_station_in_buffer(self, station, buffer_length=300):
        p1 = (self.latitude, self.longitude)
        p2 = (station.latitude, station.longitude)
        distance = geopy.distance.distance(p1, p2).km * 1000
        if distance <= buffer_length:
            self.stations_in_buffer.append([distance, station.id, station.name, station.first_use, station.latest_use])
            self.stations_in_buffer = sorted(self.stations_in_buffer, key=lambda v: v[0])

    #def add_population_in_buffer(self, mesh_pickle_path, census_dict, step=0.0001, buffer_length=300):
    def add_population_in_buffer(self, mesh_pickle_path, step=0.0001, buffer_length=300):
        #default step : 0.0001 (degree)
        self.population_in_buffer = 0
        len_per_lat = 84000
        len_per_lon = 110000
        #lat = int(self.latitude * 10000) / 10000
        #lon = int(self.longitude * 10000) / 10000
        lat_min = float(self.latitude) - buffer_length / len_per_lat
        lat_max = float(self.latitude) + buffer_length / len_per_lat
        lon_min = float(self.longitude) - buffer_length / len_per_lon
        lon_max = float(self.longitude) + buffer_length / len_per_lon
        #mesharea = cal_mesharea(float(self.latitude), float(self.longitude), step)
        #Open mesh_pickle file
        try:
            with open(mesh_pickle_path, "rb") as f:
                mesh = pickle.load(f)
            f.close()
        except:
            mesh = {}
        for i_lat in range(int(lat_min * 10000), int(lat_max * 10000)):
            for i_lon in range(int(lon_min * 10000), int(lon_max * 10000)):
                lat = i_lat / 10000
                lon = i_lon / 10000
                distance = geopy.distance.distance((lat, lon), (self.latitude, self.longitude)).km * 1000
                if distance < buffer_length:
                    if (i_lat, i_lon) not in mesh:
                        mesh[(i_lat, i_lon)] = cg.coordinates(lon, lat)
                        print("Add census geocode lat:", lat, "lon:", lon, "Mesh data.")
                    #if len(mesh[(lat, lon)]['Census Tracts']) > 0:
                        #if
                else:
                    print("lat:", lat, "lon:", lon, " is not in buffer. distance: ", distance)
    #mesh_info = census['Census Tracts'][0]
        with open(mesh_pickle_path, "wb") as f:
            pickle.dump(mesh, f)
        f.close()

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


def make_coordinate_dict(city='nyc'):
    step = 0.0001
    if(city == 'nyc'):
        '''
        min_lat = 40.05
        max_lat = 41.0
        min_lon = -74.2
        max_lon = -73.6
        40.737711   -74.066921
        '''
        min_lat = 40.744
        max_lat = 41.0
        min_lon = -73.976
        max_lon = -73.6
        census_filepath = "data/nyc_census_tracts.csv"
        census_dict = {}
        with open(census_filepath, 'r') as csvfile:
            print("Open success {}".format(census_filepath))
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                census_dict[row[0]] = float(row[3])
    #jobs = []
    mesh = {}
    lat = min_lat
    lon = min_lon
    while lat <= max_lat:
        while lon <= max_lon:
            #jobs.append((log, lon))
            mesh_info = get_mesh_data(lat, lon, step, census_dict)
            if mesh_info != -1:
                print("get infomation ", lat, lon)
                mesh[(lat, lon)] = mesh_info
            lon += step
        lat += step
    return mesh


def get_mesh_data(latitude, longitude, step, census_dict):
    '''
    TODO write description
    return: -1
            -2
            dict
    '''
    census = cg.coordinates(longitude, latitude)
    if len(census['Census Tracts']) == 0:
    # if there are no geocode in the coordinates
        print(latitude, longitude, "is not in census geocode")
        return -1
    mesh_info = census['Census Tracts'][0]
    if mesh_info['GEOID'] not in census_dict:
        print(latitude, longitude, mesh_info['GEOID'], "is not in nyc census tracts")
        return -1
    else:
        geoid = mesh_info['GEOID']
    mesharea = cal_mesharea(latitude, longitude, step)
    mesh_info['MESHAREA'] = mesharea
    #print(census_dict[geoid], mesharea, mesh_info['AREALAND'])
    #print(census_dict[geoid].__class__, mesharea.__class__, mesh_info['AREALAND'].__class__)
    mesh_info['MESHPOP'] = census_dict[geoid] * mesharea / mesh_info['AREALAND']
    print(census_dict[geoid], mesharea, mesh_info['AREALAND'], mesh_info['MESHPOP'])


def cal_mesharea(latitude, longitude, step):
    p1 = (latitude, longitude - step / 2)
    p2 = (latitude, longitude + step / 2)
    x = geopy.distance.distance(p1, p2).km * 1000
    p1 = (latitude - step / 2, longitude)
    p2 = (latitude + step / 2, longitude)
    y = geopy.distance.distance(p1, p2).km * 1000
    print("step, x, y", step, x, y)
    return (x * y)

#if __name__ == '__main__':
    #mesh = make_coordinate_dict()
