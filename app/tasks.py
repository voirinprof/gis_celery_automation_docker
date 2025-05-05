from celery import Celery
import sqlite3
from geopandas import GeoDataFrame
from shapely.geometry import Point
import pyproj

app = Celery('tasks')
app.config_from_object('celery_config')

@app.task
def compute_buffers_task():
    # Connexion à la base de données
    conn = sqlite3.connect('/root/db/points.db')
    c = conn.cursor()
    c.execute("SELECT lat, lon, radius FROM points")
    points = [(row[0], row[1], row[2]) for row in c.fetchall()]
    conn.close()

    if not points:
        return {"error": "Aucun point disponible"}

    # Créer un GeoDataFrame
    gdf = GeoDataFrame(
        [{'geometry': Point(lon, lat), 'radius': radius} for lat, lon, radius in points],
        crs="EPSG:4326"
    )

    # Reprojeter en un système de coordonnées projeté (par exemple, UTM) pour des buffers précis
    utm_crs = "EPSG:32632"  # UTM zone 32N, adapté pour l'Europe (Paris)
    gdf = gdf.to_crs(utm_crs)

    # Calculer les tampons
    gdf['geometry'] = gdf.apply(lambda row: row['geometry'].buffer(row['radius']), axis=1)

    # Reprojeter en WGS84 pour Leaflet
    gdf = gdf.to_crs("EPSG:4326")

    # Convertir en GeoJSON
    geojson = gdf.__geo_interface__

    return geojson