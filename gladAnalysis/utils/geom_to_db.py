import os

from shapely.geometry import shape

app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(app_dir)
data_dir = os.path.join(root_dir, 'data')

def get_db_name(geom):

    geom_dict = {
                 'south_america':
                    {"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-127.265625,-58.07787626787517],[-28.4765625,-58.07787626787517],[-28.4765625,40.97989806962013],[-127.265625,40.97989806962013],[-127.265625,-58.07787626787517]]]}},
                 'africa':
                    {"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-4.921875,-21.289374355860424],[52.734375,-21.289374355860424],[52.734375,15.284185114076433],[-4.921875,15.284185114076433],[-4.921875,-21.289374355860424]]]}},
                 'asia':
                    {"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[53.4375,-40],[180,-40],[180,40],[53.4375,40],[53.4375,-40]]]}}
                }

    region_count = 0

    for geom_name, geojson in geom_dict.iteritems():
        geom_shp = shape(geojson['geometry'])

        if geom.intersects(geom_shp):
            region_name = geom_name
            region_count += 1

    if region_count == 1:
        return os.path.join(data_dir, region_name + '.mbtiles')

    else:
        raise ValueError('geometry either too big (multiple regions) or outside of GLAD bounds')
