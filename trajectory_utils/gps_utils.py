# -*- coding: utf-8 -*-

import math
import numpy as np
from datetime import datetime
import pandas as pd
from collections import namedtuple
import gpxpy

# RDP algorithm as long as the rdp package is not iterative.
# See https://github.com/fhirschmann/rdp/issues/5

# For storing stay points
StayPoint = namedtuple('StayPoint', ["longitude", "latitude", "arrivTime", "departTime"])


def create_points_dataframe_from_gpx_file(gpx_file):
    with open(gpx_file) as fh:
        gpx_file = gpxpy.parse(fh)

    data = []
    for track in gpx_file.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append({"lat": point.latitude, "lon": point.longitude, "elev": point.elevation, "ts": point.time})

    return pd.DataFrame(data)


def extract_stay_points(df: pd.DataFrame, lat_col, lon_col, time_col, dist_thres=200, time_thres=20 * 60,
                        time_format='%Y-%m-%d %H:%M:%S'):
    """
    Generates stay points based on distance and time spent based on this algorithm:
    https://gist.github.com/RustingSword/5963008

    Parameters
    ----------
    df : Pandas dataframe with GPS points
    lat_col : Name of latitude column
    lon_col : Name of longitude column
    time_col : Name of datetime column which should be a datetime object
    dist_thres : Distance threshold in meters
    time_thres : time threshold in seconds
    time_format : Time forma

    Returns
    -------
    A list of stay points
    """
    stay_points = []
    num_points = len(df)
    df.sort_values(by=time_col, ascending=True, inplace=True)
    i = 0
    while i < num_points - 1:
        j = i + 1
        while j < num_points:
            loci = df.iloc[i]
            locj = df.iloc[j]
            dist = compute_distance((float(loci[lat_col]), float(loci[lon_col])),
                                    (float(locj[lat_col]), float(locj[lon_col])))

            if dist > dist_thres:
                t_i = loci[time_col]
                t_j = locj[time_col]
                deltaT = (t_j - t_i).total_seconds()
                if deltaT > time_thres:
                    lat_lst = [float(df.iloc[p][lat_col]) for p in range(i, j + 2)]
                    lon_lst = [float(df.iloc[p][lon_col]) for p in range(i, j + 2)]
                    arrivTime, departTime = datetime.strftime(t_i, time_format), datetime.strftime(t_j, time_format)
                    sp = StayPoint(np.mean(lon_lst), np.mean(lat_lst), arrivTime, departTime)
                    stay_points.append(sp)
                break
            j += 1
        i = j
    return stay_points


def compute_distance(coord1, coord2):
    """
    Haversine distance in meters for two (lat, lon) coordinates
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    radius = 6371000  # mean earth radius in meters (GRS 80-Ellipsoid)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c
