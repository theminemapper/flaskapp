from flask import Flask, request, jsonify
from flask_cors import CORS
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling

app = Flask(__name__)

# Explicitly allow all origins
CORS(app, resources={r"/elevation": {"origins": "*"}})

# Load SRTM GeoTIFF (ensure it's placed in Render's root folder)
tiff_path = "srtm_cog.tif"
src = rasterio.open(tiff_path)
vrt = WarpedVRT(src, resampling=Resampling.bilinear)

@app.route("/elevation", methods=["POST"])
def get_elevation():
    try:
        data = request.get_json()
        coords = data.get("points", [])

        if not coords:
            return jsonify({"error": "No coordinates provided"}), 400

        points = [(pt["lon"], pt["lat"]) for pt in coords]
        elevations = list(vrt.sample(points))
        values = [float(round(val[0], 2)) if val[0] is not None else None for val in elevations]

        return jsonify({"elevations": values})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
