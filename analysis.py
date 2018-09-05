#!/usr/bin/python3
# written by Hyunjoon Kim
import csv
import os
import matplotlib
matplotlib.use('Agg') #for cli
import matplotlib.pyplot as plt

def filepath(year, month, city='nyc', data_dir='data'):
    """
    return filepath
    """
    if city=='nyc' :
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
    2018-01 ~ 2018-03 
    "YYYYMM-citibikenyc_tripdata.csv"
    2018-04 ~
    "YYYYMM-citibike-tripdata.csv"
    """
    if int(year) < 2014 or ((int(year) == 2014) and (int(month)<=8)) :
        filename = "{0:04d}-{1:02d} - Citi Bike trip data.csv".format(year, month) 
    elif year == 2018 and month <= 3 :
        filename = "{0:04d}{1:02d}-citibikenyc_tripdata.csv".format(year, month) 
    else:
        filename = "{0:04d}{1:02d}-citibike-tripdata.csv".format(year, month)
    return filename

def make_tripduration_list(year, month):
    with open(filepath(year, month)) as csvfile:
        reader = csv.DictReader(csvfile)
        td = []
        for row in reader:
            td.append(int(row["tripduration"]))
    #print(td[0:6])
    return td

def plot_tripduration(td_list, filename):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.hist(td_list)
    plt.savefig(filename)

def plot_month_tripduration(year, month):
    td=make_tripduration_list(year, month)
    filename='tripduration_{0:d}{1:02d}.png'.format(year, month)
    plot_tripduration(td, filename)

if __name__ == "__main__":
    print(filename_nyc(2012, 7))
    print(filename_nyc(2014, 8))
    print(filename_nyc(2018, 1))
    print(filename_nyc(2018, 7))
    print(filepath(2012, 7))
    print(filepath(2014, 8))
    print(filepath(2018, 1))
    print(filepath(2018, 7))
    make_tripduration_list(2016, 1)
    plot_month_tripduration(2016, 1)
    plot_month_tripduration(2016, 8)
