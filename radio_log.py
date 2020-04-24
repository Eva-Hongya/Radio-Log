import get_info
import pandas as pd
import os.path
import datetime
from bs4 import BeautifulSoup
import requests
import geopy.distance
import re

pd.set_option("display.max_columns", None)
#my coordinates and define how to convert from dms to dd
my_coords = (43.65, -79.43)

#make a empty dataframe of all columns wanted
columns = {"Date":[],
        "Time":[],
        "Day/Night":[],
        "Station ID":[],
        "City":[],
        "Frequency":[],
        "SINPO":[],
        "Content":[],
        "Transmitter Coordinates":[],
        "Distance From Home":[],
        "Power":[],
        "Power/Distance":[]}

# check if there is a log already, creat one if not
if not os.path.exists("/home/eva/Desktop/data/profile/radio/log.csv"):
    log = pd.DataFrame(data=columns, columns=["Date", "Time", "Day/Night", "Station ID", \
                                              "City", "Frequency", "SINPO", "Content", \
                                              "Transmitter Coordinates","Distance From Home", \
                                              "Power", "Power/Distance"])
    log.to_csv("/home/eva/Desktop/data/profile/radio/log.csv")

# define values for new row
date = datetime.datetime.now().date().strftime("%y-%m-%d")
time = datetime.datetime.now().time().strftime("%H:%M:%S")
station_id = input("Station ID:")
print("\n")
sinpo = input("Rate it with SINPO:")
print("\n")
content = input("What is this radio station about?:\n")

# scraping wikipedia for other columns, there are two forms of wiki url, try both
link = "https://en.wikipedia.org/wiki/" + station_id
link_1 = link + "_(AM)"

for link in (link, link_1):
    page = requests.get(link, timeout=5)
    table = BeautifulSoup(page.content, "html.parser").find("table", class_="infobox vcard")
    
    # check if page downloaded succesfully, status_code starts with 2(200) is good, 4 or 5(404) bad
    if table != None:

        print("Looks like we just found the page for you!\n", table.prettify)
        print(list(table.children))
        city = table.find(text="City").findNext("td").text
        frequency = table.find(text="Frequency").findNext("td").text

        # check if there is a cooordinates available
        transmitter_coordinates = table.find(text="Transmitter coordinates")
        if transmitter_coordinates != None:
            transmitter_coordinates = transmitter_coordinates.findNext("td").text

            transmitter_coordinates = transmitter_coordinates[:transmitter_coordinates.find("/")]

            # get coords in dd so to get distance between radio station and home
            radio_coords = get_info.dms2dd(transmitter_coordinates)
            distance = geopy.distance.vincenty(my_coords, radio_coords).km
            distance = float("{0:.2f}".format(distance))

            # day/night and power
            #use coordinates to decide local now_sunrise_sunset, then deicde if is day or night, there decide power
            local_time, sunrise, sunset = get_info.sun(radio_coords)

            if local_time < sunrise or local_time > sunset:
                day_night = "Night"
            else:
                day_night = "Day"
        else:
            transmitter_coordinates = "N/A"
            distance = "N/A"
            day_night = "N/A"


        #power for day and night
        power = table.find(text="Power").findNext("td").text
        if len(power) > 13 and day_night == "Night":
            new = power[power.find(" "):]
            for i in new:
                if i.isdigit():
                    # start here
                    print(i, type(i))
                    power = float(new[new.index(i):new.find(" ", new.index(i))].replace(".", "").replace(",", ""))
                    break
        else:
            power = float(power[:power.find(" ")].replace(".", "").replace(",", ""))


        # new values to new row(append a new row to the log)
        columns["Date"].append(date)
        columns["Time"].append(time)
        columns["Day/Night"].append(day_night)
        columns["Station ID"].append(station_id)
        columns["City"].append(city)
        columns["Frequency"].append(frequency)
        columns["SINPO"].append(sinpo)
        columns["Content"].append(content)
        columns["Transmitter Coordinates"].append(transmitter_coordinates)
        columns["Distance From Home"].append(distance)
        columns["Power"].append(power)
        columns["Power/Distance"].append("{0:.2f}".format(power/distance))

        print(columns)

        log = pd.read_csv("/home/eva/Desktop/data/profile/radio/log.csv")
        row = pd.DataFrame(columns)
        log = log.append(row, ignore_index=True, sort=False)
        log.drop(log.columns[log.columns.str.contains("Unnamed:", case=False)], axis=1, inplace=True)
        print(log)
        log.to_csv("/home/eva/Desktop/data/profile/radio/log.csv")
        break

    elif page.status_code == 404:
        print("Wiki page not found.")
    else:
        print("There is an error. A wikipedia page about " + link + " is found, but not quite about specific radio info.")
