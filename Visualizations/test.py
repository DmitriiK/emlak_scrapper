import geopandas as gp
import pandas as pnd
from shapely.geometry import Polygon, LineString, Point
import timeit
import numpy as np
import draw_heatmap

pnd.set_option('display.max_columns', None)
med_sea = gp.read_file("Input/iho.zip", encoding='utf-8')
"""
countries = gp.read_file(gp.datasets.get_path('naturalearth_lowres'))
turkey = countries[countries['iso_a3'] == 'TUR']
turkey.reset_index(drop=True, inplace=True)
print(turkey)
"""
 # Index(['pop_est', 'continent', 'name', 'iso_a3', 'gdp_md_est', 'geometry'], dtype='object')
sea = Point(30.680477079336566, 36.88171058294274)
# s = gp.GeoSeries([Point(31.012859188137266, 36.629828895095635)])
# s.crs = "WGS 84"
#
mseb = med_sea[med_sea['id'] == '28B']# .iloc[0]  # Mediterranean Sea - Eastern Basin
# for ind, r in mseb.iterrows():
pol = mseb['geometry']
print(mseb['name'])

def testgeo():
    not_sea = Point(30.676370581303445, 36.883204913105594)
    x = not_sea.within(pol)

def testspatial():
    # antalya da
    MIN_LAT = draw_heatmap.MIN_LAT
    MAX_LAT = draw_heatmap.MAX_LAT
    MIN_LON = draw_heatmap.MIN_LON
    MAX_LON = draw_heatmap.MAX_LON

    MAX_X = draw_heatmap.MAX_X
    MAX_Y = draw_heatmap.MAX_Y
    N= MAX_X * MAX_Y
    xys = []
    for x in range(MAX_X):
        row = [(x, y) for y in range(MAX_Y)]
        xys.extend(row)
    lon_lat = [draw_heatmap.pixel_to_ll(*xy, True) for xy in xys]  # list of pairs (longitude, latitude)
    # lon_lat.append( (30.689010597749384, 36.844581003961416))
    # lst_lst = list(zip(*lon_lat)) # list of 2 lists, - first one is for long, second one - for lat

    # lat = np.random.uniform(MIN_LAT, MAX_LAT, N)
    # lon = np.random.uniform(MIN_LON, MAX_LON, N)

    # Create geodataframe from numpy arrays
    df = pnd.DataFrame({'xys': xys, 'coords': lon_lat})  #,'lon': lst_lst[0], 'lat': lst_lst[1]
    # df['coords'] = lon_lat #  list(zip(df['lon'], df['lat']))
    df['coords'] = df['coords'].apply(Point)
    points = gp.GeoDataFrame(df, geometry='coords', crs=med_sea.crs)
    # print(points)
    pointInPolys = gp.tools.sjoin(points, med_sea, predicate="within", how='left')
    # print(pointInPolys)


# timer = timeit.timeit(testgeo, number=1000)
timer = timeit.timeit(testspatial, number=1)
print(timer)








