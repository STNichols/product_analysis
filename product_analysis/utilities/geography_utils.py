# -*- coding: utf-8 -*-

from math import radians
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import haversine_distances

EARTH_RADIUS = 6371000

def linestrings_to_df(linestring, sample_ratio=1):
    """ Convert a pandas Series of linestrings into a pandas DataFrame with all
        individual data points
    """

    longitude_full = []
    latitude_full = []
    line_i_full = []
    for i, ln_str in enumerate(linestring):
        values = list(linestring[i].coords)
        longitude, latitude = zip(*values)
        longitude = np.array(longitude)
        latitude = np.array(latitude)
        
        if sample_ratio < 1:
            sample_idx = np.random.randint(
                0, len(longitude), int(np.ceil(sample_ratio * len(longitude))))
            longitude = longitude[sample_idx]
            latitude = latitude[sample_idx]
        
        longitude_full.extend(list(longitude))
        latitude_full.extend(list(latitude))
        line_i_full.extend([i] * len(longitude))
        
    return pd.DataFrame({'longitude':longitude_full,
                          'latitude':latitude_full,
                          'line_index':line_i_full})

def meshgrid_ll(longitude, latitude, bin_size):
    """ Creates a pandas DataFrame consisting of a meshgrid of the lat/lon
        bounds provided at the 
    """
    
    longitudes = np.arange(min(longitude), max(longitude), bin_size)
    latitudes = np.arange(min(latitude), max(latitude), bin_size)
    
    lon_m, lat_m = np.meshgrid(longitudes, latitudes)
    
    return pd.DataFrame({'longitude':lon_m.flatten(),
                         'latitude':lat_m.flatten()})

def find_closest_ll(input_ll, reference_ll, n=1):
    """ Find the closest pairing of longitude and latitudes from the input set
        to the reference set
    """
    
    nbrs = NearestNeighbors(n_neighbors=n).fit(
        reference_ll[['longitude', 'latitude']].values)
    _ , indices = nbrs.kneighbors(
        input_ll[['longitude', 'latitude']].values)
    
    input_ll['longitude_rad'] = input_ll['longitude'].apply(radians)
    input_ll['latitude_rad'] = input_ll['latitude'].apply(radians)
    loc_1 = input_ll[['longitude_rad', 'latitude_rad']]
    
    reference_ll['longitude_rad'] = reference_ll['longitude'].apply(radians)
    reference_ll['latitude_rad'] = reference_ll['latitude'].apply(radians)
    loc_2 = reference_ll.iloc[indices.flatten()][['longitude_rad',
                                                  'latitude_rad']]
    
    distances = np.array([])
    for l1, l2 in zip(loc_1.values, loc_2.values):
        d = (haversine_distances([l1, l2]) * EARTH_RADIUS / 1000) # km
        distances = np.append(distances, np.max(d))
    
    return distances, indices
    
    