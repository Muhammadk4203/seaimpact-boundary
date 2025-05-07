import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString
import pyproj
import os
import numpy as np
import geojson


# === Filepaths ===
current_directory = os.path.dirname(os.path.abspath(__file__))
area_filepath = os.path.join(current_directory, 'Khank', 'Boundary.geojson')
offshore_filepath = os.path.join(current_directory, 'Khank', 'Offshorewindmills.geojson')


# === Utility Functions ===
def convert_LatLong_to_utm(long, lat):
    wgs84 = pyproj.CRS('EPSG:4326')
    utm_zone = int((long + 180) / 6) + 1
    hemisphere = 'N' if lat >= 0 else 'S'
    utm_epsg_code = f'EPSG:{32600 + utm_zone if hemisphere == "N" else 32700 + utm_zone}'
    utm = pyproj.CRS(utm_epsg_code)
    transformer = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)
    easting, northing = transformer.transform(long, lat)
    return (easting, northing)


def get_lat_long(filepath):
    with open(filepath, 'r') as file:
        geojson_data = geojson.load(file)
    coordinates = geojson_data["features"][0]["geometry"]["coordinates"]
    return coordinates


def plot_farm_layout(filepath):
    latlon_coords = get_lat_long(filepath)

    wt_x, wt_y = [], []
    for long, lat in latlon_coords:
        utm_x, utm_y = convert_LatLong_to_utm(long, lat)
        wt_x.append(utm_x)
        wt_y.append(utm_y)

    return wt_x, wt_y


# === Main Plot Function ===
def plot_bound(area_filepath, offshore_filepath):
    fig, ax = plt.subplots()
    D = 220

    # Plot boundary (from line_area.geojson)
    with open(area_filepath, 'r') as file:
        area_data = geojson.load(file)

    area_coords = area_data["features"][0]["geometry"]["coordinates"]
    utm_boundary = [convert_LatLong_to_utm(lon, lat) for lon, lat in area_coords]
    line = LineString(utm_boundary)
    gdf = gpd.GeoDataFrame({"geometry": [line]})
    gdf.plot(ax=ax, color='black', linewidth=2)

    # Plot turbine locations (from line_offshore.geojson)
    wt_x, wt_y = plot_farm_layout(offshore_filepath)

    bx = np.asarray(wt_x)
    by = np.asarray(wt_y)

    ax.scatter(bx, by, marker='.', c='red', s=10)

    ax.set_xlabel("X-UTM Coordinates", fontsize=12)
    ax.set_ylabel("Y-UTM Coordinates", fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=10)
    plt.grid(True)
    plt.show(block=True)


# === Main Runner ===
if __name__ == '__main__':
    plot_bound(area_filepath, offshore_filepath)