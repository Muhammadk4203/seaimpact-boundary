import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString
import pyproj
import os
import numpy as np
import geojson

# Set up file paths for boundary and windmill data 
current_directory = os.path.dirname(os.path.abspath(__file__))
area_filepath = os.path.join(current_directory, 'Khank', 'Boundary.geojson')  # path to boundary file
offshore_filepath = os.path.join(current_directory, 'Khank', 'Offshorewindmills.geojson')  # path to turbine locations

# Convert longitude and latitude into UTM coordinates 
def convert_LatLong_to_utm(long, lat):
    wgs84 = pyproj.CRS('EPSG:4326')  # coordinate reference system for GPS
    utm_zone = int((long + 180) / 6) + 1  # calculate appropriate UTM zone
    hemisphere = 'N' if lat >= 0 else 'S'
    utm_epsg_code = f'EPSG:{32600 + utm_zone if hemisphere == "N" else 32700 + utm_zone}'  # EPSG for UTM
    utm = pyproj.CRS(utm_epsg_code)
    transformer = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)
    easting, northing = transformer.transform(long, lat)
    return (easting, northing)

#  Read the coordinates from a geojson file 
def get_lat_long(filepath):
    with open(filepath, 'r') as file:
        geojson_data = geojson.load(file)
    coordinates = geojson_data["features"][0]["geometry"]["coordinates"]  # assumes first feature
    return coordinates

# Process and convert wind turbine layout into UTM 
def plot_farm_layout(filepath):
    latlon_coords = get_lat_long(filepath)

    wt_x, wt_y = [], []
    for long, lat in latlon_coords:
        utm_x, utm_y = convert_LatLong_to_utm(long, lat)
        wt_x.append(utm_x)
        wt_y.append(utm_y)

    return wt_x, wt_y

# Create the plot showing boundary and turbine layout 
def plot_bound(area_filepath, offshore_filepath):
    fig, ax = plt.subplots()
    D = 220  # unused variable (optional to remove)

    # Load boundary data and plot as a line
    with open(area_filepath, 'r') as file:
        area_data = geojson.load(file)

    area_coords = area_data["features"][0]["geometry"]["coordinates"][0]  # outer ring of polygon
    utm_boundary = [convert_LatLong_to_utm(lon, lat) for lon, lat in area_coords]
    line = LineString(utm_boundary)
    gdf = gpd.GeoDataFrame({"geometry": [line]})
    gdf.plot(ax=ax, color='black', linewidth=2)

    # Load and plot turbine locations
    wt_x, wt_y = plot_farm_layout(offshore_filepath)
    bx = np.asarray(wt_x)
    by = np.asarray(wt_y)
    ax.scatter(bx, by, marker='o', c='red', s=10)

    # Add plot labels and formatting
    ax.set_xlabel("UTM Easting", fontsize=12)
    ax.set_ylabel("UTM Northing", fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=10)
    plt.grid(True)
    plt.show(block=True)

# Start the program 
if __name__ == '__main__':
    plot_bound(area_filepath, offshore_filepath)
