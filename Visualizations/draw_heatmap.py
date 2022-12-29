from PIL import Image
import sys
import math
import numpy
import json
import psycopg2
import geopandas as gp
import pandas as pnd
from shapely.geometry import Point
import timeit

# set boundaries in query_padmapper
# antalya da
MIN_LAT = 36.825
MAX_LAT = 36.985
MIN_LON = 30.572
MAX_LON = 30.857

# change these to change how detailed the generated image is
# (1000x1000 is good, but very slow)
MAX_X = 100
MAX_Y = 100

DRAW_DOTS = True

# at what distance should we stop making predictions?
IGNORE_DIST = 0.01


def create_connection():
    conn = psycopg2.connect(  # to do - move to common config file
        host="localhost",
        database="emlak",
        user="postgres",
        password="123"
    )
    return conn


def load_prices():
    raw_prices = []
    try:
        connection = create_connection();
        read_emlak_sql = "SELECT  eml.id, eml.room, eml.is_furnished, eml.price, eml.sqm_netsqm, " \
                         "eml.price/eml.sqm_netsqm as sqm_price, eml.maplocation_lon, eml.maplocation_lat  " \
                         "FROM public.f_emlak eml " \
                         "WHERE eml.price/eml.sqm_netsqm between 40 and 500 " \
                         "and eml.room between 1 and 5" \
                         " and eml.is_furnished"
        cursor = connection.cursor()
        cursor.execute(read_emlak_sql)
        output = cursor.fetchone()
        while output is not None:
            # print(output)
            row = cursor.fetchone()
            apt_id, bedrooms, rent,   lon, lat = (int(row[0]), int(row[1]), row[5], float(row[6]), float(row[7]))
            raw_prices.append((bedrooms, rent, lat, lon))

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    slope, y_intercept = linear_regression([(bedrooms, rent) for (bedrooms, rent, lat, lon) in raw_prices])
    print("slope = %s" % slope)
    print("y intercept = %s" % y_intercept)
    x_intercept = -(y_intercept) / slope
    print("x intercept =", x_intercept)
    num_phantom_bedrooms = -x_intercept  # positive now

    # prices = [(rent / (bedrooms + num_phantom_bedrooms), lat, lon, bedrooms) for (bedrooms, rent, lat, lon) in raw_prices] comm dk
    prices = [(rent, lat, lon, bedrooms) for (bedrooms, rent, lat, lon) in raw_prices]
    return prices, num_phantom_bedrooms

    # For each point, use the linear regression to convert to an estimate of
    # what a 2br would cost instead.
    def est_2br(rent, bedrooms):
        estimated_rent_for_this_size = y_intercept + slope * bedrooms
        proportion_of_expected_rent = rent / estimated_rent_for_this_size
        return proportion_of_expected_rent * (y_intercept + slope * 2)

    prices = [(est_2br(rent, bedrooms), lat, lon, bedrooms) for (bedrooms, rent, lat, lon) in raw_prices]
    return prices, slope, y_intercept


def pixel_to_ll(x, y, long_first=False):
    delta_lat = MAX_LAT - MIN_LAT
    delta_lon = MAX_LON - MIN_LON

    # x is lon, y is lat
    # 0,0 is MIN_LON, MAX_LAT

    x_frac = float(x) / MAX_X
    y_frac = float(y) / MAX_Y

    lon = MIN_LON + x_frac * delta_lon
    lat = MAX_LAT - y_frac * delta_lat

    calc_x, calc_y = ll_to_pixel(lat, lon)

    if abs(calc_x - x) > 1 or abs(calc_y - y) > 1:
        print
        "Mismatch: %s, %s => %s %s" % (
            x, y, calc_x, calc_y)
    if long_first:
        return lon, lat
    else:
        return lat, lon


def ll_to_pixel(lat, lon):
    adj_lat = lat - MIN_LAT
    adj_lon = lon - MIN_LON

    delta_lat = MAX_LAT - MIN_LAT
    delta_lon = MAX_LON - MIN_LON

    # x is lon, y is lat
    # 0,0 is MIN_LON, MAX_LAT

    lon_frac = adj_lon / delta_lon
    lat_frac = adj_lat / delta_lat

    x = int(lon_frac * MAX_X)
    y = int((1 - lat_frac) * MAX_Y)

    return x, y


def linear_regression(pairs):
    xs = [x for (x, y) in pairs]
    ys = [y for (x, y) in pairs]

    A = numpy.array([xs, numpy.ones(len(xs))])
    w = numpy.linalg.lstsq(A.T, ys)[0]
    return w[0], w[1]


def distance_squared(x1, y1, x2, y2):
    return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)


def distance(x1, y1, x2, y2):
    return math.sqrt(distance_squared(x1, y1, x2, y2))


def greyscale(price):
    grey = int(256 * float(price) / 3000)
    return grey, grey, grey


def color(val, buckets):
    if val is None:
        return (255, 255, 255, 0)

    colors = [(255, 0, 0),
              (255, 91, 0),
              (255, 127, 0),
              (255, 171, 0),
              (255, 208, 0),
              (255, 240, 0),
              (255, 255, 0),
              (218, 255, 0),
              (176, 255, 0),
              (128, 255, 0),
              (0, 255, 0),
              (0, 255, 255),
              (0, 240, 255),
              (0, 213, 255),
              (0, 171, 255),
              (0, 127, 255),
              (0, 86, 255),
              (0, 0, 255),
              ]

    for price, color in zip(buckets, colors):
        if val > price:
            return color
    return colors[-1]


gaussian_variance = IGNORE_DIST / 2
gaussian_a = 1 / (gaussian_variance * math.sqrt(2 * math.pi))
gaussian_negative_inverse_twice_variance_squared = -1 / (2 * gaussian_variance * gaussian_variance)


def gaussian(prices, lat, lon, ignore=None):
    num = 0
    dnm = 0
    c = 0

    for price, plat, plon, _ in prices:
        if ignore:
            ilat, ilon = ignore
            if distance_squared(plat, plon, ilat, ilon) < 0.0001:
                continue

        weight = gaussian_a * math.exp(distance_squared(lat, lon, plat, plon) *
                                       gaussian_negative_inverse_twice_variance_squared)

        num += price * weight
        dnm += weight

        if weight > 2:
            c += 1

    # don't display any averages that don't take into account at least five data points with significant weight
    if c < 5:
        return None

    return num / dnm


def start():
    print
    "loading data..."
    priced_points, num_phantom_bedrooms = load_prices()

    print
    "computing #bedroom adjustments..."

    # compute what the error would be at each data point if we priced it without being able to take it into account
    # do this on a per-bedroom basis, so that we can compute correction factors
    bedroom_categories = list(sorted(set(bedrooms for _, _, _, bedrooms in priced_points)))
    adjustments = {}

    # don't need that part of code - as we not investigating anything about bedroom_category
    # for bedroom_category in bedroom_categories:
    #    print "  %sbr..." % (bedroom_category)
    #    total_actual = 0
    #    total_predicted = 0

    #    for i, (price, plat, plon, bedroom) in enumerate(priced_points):
    #        if bedroom != bedroom_category:
    #            continue

    #        x, y = ll_to_pixel(plat, plon)
    #        predicted_price = gaussian(priced_points, plat, plon, ignore=(plat, plon))

    #        if predicted_price:
    #            total_actual += price
    #            total_predicted += predicted_price

    #    if total_predicted == 0:
    #        # we might not make any predictions, if we don't have enough data
    #        adjustment = 1.0
    #    else:
    #        adjustment = total_actual / total_predicted

    adjustments[1] = 1

    "pricing all the points..."
    prices = {}
    gf = get_geo_frame()
    for ind, r in gf.iterrows():
        xys = r['xys']
        prices[xys] = gaussian(priced_points, r['lat'], r['lon'])

    # determine buckets
    # we want 18 buckets (17 divisions) of equal area
    all_priced_areas = [x for x in prices.values() if x is not None]

    all_priced_areas.sort()
    total_priced_area = len(all_priced_areas)

    buckets = []
    divisions = 17.0
    stride = total_priced_area / (divisions + 1)
    next_i = int(stride)
    error_i = stride - next_i
    for i, val in enumerate(all_priced_areas):
        if i == next_i:
            buckets.append(val)
            delta_i = stride + error_i
            next_i += int(delta_i)
            error_i = delta_i - int(delta_i)

    buckets.reverse()

    # color regions by price
    I = Image.new('RGBA', (MAX_X, MAX_Y))
    IM = I.load()
    for x in range(MAX_X):
        for y in range(MAX_Y):
            IM[x, y] = color(prices.get((x, y)), buckets)

    if DRAW_DOTS:
        for _, lat, lon, _ in priced_points:
            x, y = ll_to_pixel(lat, lon)
            if 0 <= x < MAX_X and 0 <= y < MAX_Y:
                IM[x, y] = (0, 0, 0)

    out_fname = "Output/myoutput.phantom." + str(MAX_X)
    I.save(out_fname + ".png", "PNG")
    with open(out_fname + ".metadata.json", "w") as outf:
        outf.write(json.dumps({
            "num_phantom_bedrooms": num_phantom_bedrooms,
            "buckets": buckets,
            "n": len(priced_points),
            "adjustments": adjustments}))

def get_geo_frame():
    med_sea = gp.read_file("Input/iho.zip", encoding='utf-8')
    # mseb = med_sea[med_sea['id'] == '28B']  # .iloc[0]  # Mediterranean Sea - Eastern Basin
    xys = []
    for x in range(MAX_X):
        row = [(x, y) for y in range(MAX_Y)]
        xys.extend(row)
    lon_lat = [pixel_to_ll(*xy, True) for xy in xys]  # list of pairs (longitude, latitude)
    lst_lst = list(zip(*lon_lat))  # list of 2 lists, - first one is for long, second one - for lat
    df = pnd.DataFrame({'xys': xys,'lon': lst_lst[0], 'lat': lst_lst[1], 'coords': lon_lat})  #
    df['coords'] = df['coords'].apply(Point)
    points = gp.GeoDataFrame(df, geometry='coords', crs=med_sea.crs)
    # print(points)
    df2sea = gp.tools.sjoin(points, med_sea, predicate="within", how='left')
    df2sea.drop(df2sea[df2sea['index_right'] >= 0].index, inplace=True) # dropping rows related to the sea # pd.isna(np.nan)

    return df2sea[['xys', 'lon', 'lat']]


if __name__ == "__main__":
    # if len(sys.argv) != 2:        print("usage: python draw_heatmap.py apts.txt")
    # fname = sys.argv[1]
    timer = timeit.timeit(start, number=1)
    print(timer)