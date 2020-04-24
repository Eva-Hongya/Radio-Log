# -*- coding: utf-8 -*-
import re
from datetime import datetime
import pytz
from tzwhere import tzwhere
from dateutil import tz
from bs4 import BeautifulSoup
import requests
import urllib
import json

def dms2dd(dms):
    """(str) -> tuple of float
    Convert a coordinates in degree minute seconds to decimal, returns a tuple of two numbers: lat and lng"""
    
    coords = dms.split(" ")[:2]
    l = []

    for i in coords:
        i = i.strip()
       
        # get degree, minutes, seconds, direction
        parts = re.split("[°′″]+", i)
        parts[-1] = parts[-1][0]
        dd = float(parts[0]) + float(parts[1])/60 + float(parts[2])/(60*60)
        if parts[3] == "W" or parts[3] == "S":
            dd = dd*-1
        l.append(dd)

    
    return (l[0], l[1])


def sun(location_in_dd):
    """(tuple of float) -> tuple of datetime object
    Takes a tuple of decimal coordinates, returns a tuple of local time now (of radio station) sunrise and sunset."""
    
    rise_set = requests.get("https://api.sunrise-sunset.org/json?lat=" + str(location_in_dd[0]) \
                       + "&lng=" + str(location_in_dd[1]) + "&date=today&formatted=0")

    
    soup = BeautifulSoup(rise_set.content, "html.parser")

    #use json to decode json file from API to a dict
    result = json.loads(str(soup))
    
    sunrise = result["results"]["sunrise"]
    sunset = result["results"]["sunset"]
    sunrise = sunrise[:10] + " " + sunrise[11:19]
    sunset = sunset[:10] + " " + sunset[11:19]
        
    # get time zone and local time
    time_zone = tzwhere.tzwhere().tzNameAt(location_in_dd[0], location_in_dd[1])
    from_zone = tz.gettz("UTC")
    to_zone = tz.gettz(time_zone)

    now = datetime.now(to_zone).time()

    rise_utc = datetime.strptime(sunrise, "%Y-%m-%d %H:%M:%S")
    rise_local = rise_utc.replace(tzinfo=from_zone).astimezone(to_zone).time()
        
    set_utc = datetime.strptime(sunset, "%Y-%m-%d %H:%M:%S")
    set_local = set_utc.replace(tzinfo=from_zone).astimezone(to_zone).time()

    result = (now, rise_local, set_local)

    return result
    
