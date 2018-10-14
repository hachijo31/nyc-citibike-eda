#!/usr/bin/python3
# written by Hyunjoon Kim
import csv
import os
import datetime as dt
import station_info
import matplotlib
#for cli
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def filepath(year, month, city='nyc', data_dir='data'):
    """
    return filepath
    """
    if city == 'nyc':
        return os.path.join(data_dir, filename_nyc(year, month))
    else:
        raise ValueError("Undefined City! : ", city)


def filename_nyc(year, month):
    """
    input:
        year, month : int
    return:
        string
    ~ 2014-08
    "YYYY-MM - Citi Bike trip data.csv"
    2014-09 ~ 2017-12
    "YYYYMM-citibike-tripdata.csv"
    2018-01 ~
    "YYYYMM-citibike-tripdata.csv"
    """
    if int(year) < 2014 or ((int(year) == 2014) and (int(month) <= 8)):
        filename = "{0:04d}-{1:02d} - Citi Bike trip data.csv".format(year, month)
    else:
        filename = "{0:04d}{1:02d}-citibike-tripdata.csv".format(year, month)
    return filename


def refresh_station_dict(station_id, name, latitude, longitude, year, month, station_dict):
    latest_use = dt.date(year, month, 1)
    if station_id in station_dict:
        station_dict[station_id].refresh(name, latitude, longitude, latest_use)
    else:
        station_dict[station_id] = station_info.station_info(station_id, name, latitude, longitude, latest_use)
    return station_dict


def append_station_dict(year, month, station_dict):
    with open(filepath(year, month)) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            station_dict = refresh_station_dict(row[3], row[4], row[5], row[6], year, month, station_dict)
            station_dict = refresh_station_dict(row[7], row[8], row[9], row[10], year, month, station_dict)
    return station_dict


def make_station_dict(start_year, start_month, end_year, end_month):
    station_dict = {}
    start = dt.date(start_year, start_month, 1)
    end = dt.date(end_year, end_month, 1)
    tmp = start
    while tmp < end:
        print("append_station_dict {}-{}".format(tmp.year, tmp.month))
        station_dict = append_station_dict(tmp.year, tmp.month, station_dict)
        if tmp.month == 12:
            tmp = dt.date(tmp.year + 1, 1, 1)
        else:
            tmp = dt.date(tmp.year, tmp.month + 1, 1)
    return station_dict


def add_stations_list_in_buffer(station_dict, buffer_length):
    for i1, v1 in station_dict.items():
        for i2, v2 in station_dict.items():
            if i1 != i2:
                v1.add_station_in_buffer(v2, buffer_length)
    for i1, v1 in station_dict.items():
        print(v1.stations_in_buffer)


def save_station_dict_csv(station_dict):
    with open("station_info.csv", "w") as f:
        fn = [
            'station id', 'station name', 'latitude', 'longitude',
            'first use', 'latest use',
            'number of relocation of the station', 'maximum of relocation distance',
            'distance to city hall',
            'number of stations in buffer',
            'closest station distance', 'closest station id',
            'closest station name', 'closest station first use',
            'closest station latest use'
        ]
        writer = csv.DictWriter(f, fieldnames=fn)
        writer.writeheader()
        for i, station in station_dict.items():
            #print(station.export())
            writer.writerow(station.export())


def make_tripduration_list(year, month):
    with open(filepath(year, month)) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        td = []
        for row in reader:
            td.append(int(row[0]))
    '''
    with open(filepath(year, month)) as csvfile:
        reader = csv.DictReader(csvfile)
        td = []
        for row in reader:
            try:
                td.append(int(row["tripduration"]))
            except:
                td.append(int(row["Trip Duration"]))
    #print(td[0:6])
    '''
    return td


def plot_month_tripduration(year, month):
    td = make_tripduration_list(year, month)
    filename = 'tripduration_{0:d}{1:02d}.png'.format(year, month)

    fig = plt.figure()
    plt.title("Trip distribution {0:d}-{1:02d}".format(year, month))
    ax = fig.add_subplot(1, 1, 1)
    ax.hist(td, bins=60, range=(0, 2500))
    ax.set_xlabel("Trip duration (s)")
    ax.set_ylabel("Counts")

    plt.savefig(filename)
    print(" End to plot '{}'".format(filename))

if __name__ == "__main__":
    buffer_length = 300
    #station_dict = make_station_dict(2013, 7, 2013, 12)
    station_dict = make_station_dict(2013, 7, 2018, 9)
    print("Make stations in buffer length list")
    add_stations_list_in_buffer(station_dict, buffer_length)
    save_station_dict_csv(station_dict)
    """
    for j in range(2015, 2017):
        for i in range(12):
            plot_month_tripduration(j, i+1)
    """
