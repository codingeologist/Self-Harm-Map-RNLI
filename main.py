import folium
import sqlite3
import pandas as pd
import geopandas as gpd
from folium.plugins import Draw
from folium.plugins import HeatMap


def get_data():

    gdf = gpd.read_file('./data/RNLI_Returns_of_Service.geojson')

    gdf.set_index('OBJECTID')

    gdf['Latitude'] = gdf.geometry.y
    gdf['Longitude'] = gdf.geometry.x

    gdf.drop(['GlobalID',
              'CreationDate',
              'Creator',
              'EditDate',
              'Editor',
              'geometry'], axis=1, inplace=True)

    gdf1 = gdf[(gdf.Activity == 'SUSPECTED SELF HARM')
               & (gdf.AIC != 'Hoax and false alarm')]

    con = sqlite3.connect('./data/rnli_data.db')

    gdf.to_sql(name='all_data', con=con, schema='rnli',
               if_exists='replace', index=False)
    gdf1.to_sql(name='harm_data', con=con, schema='rnli',
                if_exists='replace', index=False)


def read_db():

    con = sqlite3.connect('./data/rnli_data.db')
    sql_str = 'SELECT * FROM harm_data'

    df = pd.read_sql(sql=sql_str, con=con, index_col='OBJECTID')

    lat = df.Latitude.tolist()
    lon = df.Longitude.tolist()

    return lat, lon


def basemap_lyrs():

    esri_imagery = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    esri_attr = '<a href="https://rnli.org/">&copy; RNLI</a> | <a href="https://www.esri.com">&copy; ESRI</a>'

    cartodb_imagery = 'http://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'
    cartodb_attr = '<a href="https://rnli.org/">&copy; RNLI</a> | <a href="https://www.carto.com">&copy; Carto</a>'

    osm_imagery = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    osm_attr = '<a href="https://rnli.org/">&copy; RNLI</a> | <a href="https://www.openstreetmap.org">&copy; OSM</a>'

    otm_imagery = 'https://tile.opentopomap.org/{z}/{x}/{y}.png'
    otm_attr = '<a href="https://rnli.org/">&copy; RNLI</a> | <a href="https://www.opentopomap.org">&copy; OTM</a>'

    gh_imagery = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
    g_attr = '<a href="https://rnli.org/">&copy; RNLI</a> | <a href="https://www.google.com">&copy; Google</a>'

    gr_imagery = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'

    gs_imagery = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'

    return esri_imagery, esri_attr, cartodb_imagery, cartodb_attr, osm_imagery, osm_attr, otm_imagery, osm_attr, gh_imagery, gr_imagery, gs_imagery, g_attr


def init_map():

    esri_imagery, esri_attr, cartodb_imagery, cartodb_attr, osm_imagery, osm_attr, otm_imagery, otm_attr, gh_imagery, gr_imagery, gs_imagery, g_attr = basemap_lyrs()

    lat, lon = read_db()

    start_coords = (50.90, -1.40)
    m = folium.Map(location=start_coords,
                   zoom_start=10,
                   tiles=None)

    folium.TileLayer(tiles=esri_imagery,
                     attr=esri_attr,
                     name='ESRI World Imagery',
                     control=True,
                     show=True).add_to(m)

    folium.TileLayer(tiles=cartodb_imagery,
                     attr=cartodb_attr,
                     name='CartoDB Dark Imagery',
                     control=True,
                     show=True).add_to(m)

    folium.TileLayer(tiles=osm_imagery,
                     attr=osm_attr,
                     name='Open Street Map',
                     control=True,
                     show=True).add_to(m)

    folium.TileLayer(tiles=otm_imagery,
                     attr=otm_attr,
                     name='Open Topo Map',
                     control=True,
                     show=True).add_to(m)

    folium.TileLayer(tiles=gh_imagery,
                     attr=g_attr,
                     name='Google Hybrid',
                     control=True,
                     show=True).add_to(m)

    folium.TileLayer(tiles=gr_imagery,
                     attr=g_attr,
                     name='Google Road',
                     control=True,
                     show=True).add_to(m)

    folium.TileLayer(tiles=gs_imagery,
                     attr=g_attr,
                     name='Google Satellite',
                     control=True,
                     show=True).add_to(m)

    hm_lyr = folium.FeatureGroup(name='Heat Map',
                                 overlay=True,
                                 control=True,
                                 show=True).add_to(m)

    HeatMap(list(zip(lat, lon))).add_to(hm_lyr)

    Draw(export=True,
         filename='data.geojson',
         position='topleft',
         draw_options={
             'polyline': True,
             'polygon': True,
             'rectangle': True,
             'circle': True,
             'marker': True,
             'circlemarker': True}).add_to(m)

    folium.LayerControl().add_to(m)

    title = '<title>Self Harm Map - RNLI Data</title>'
    m.get_root().html.add_child(folium.Element(title))
    m.save('index.html')


if __name__ == '__main__':

    init_map()
