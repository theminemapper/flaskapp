from flask import Flask, request, jsonify
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
import numpy as np

app = Flask(__name__)

# Load your SRTM GeoTIFF once
tiff_path = "d:/cog/srtm_cog.tif"  # Use correct path when deploying

# Open and reproject if needed
src = rasterio.open(tiff_path)
vrt = WarpedVRT(src, resampling=Resampling.bilinear)

@app.route("/elevation", methods=["POST"])
def get_elevation():
    try:
        data = request.get_json()
        coords = data.get("points", [])  # Format: [{"lat": ..., "lon": ...}, ...]

        if not coords:
            return jsonify({"error": "No coordinates provided"}), 400

        # Convert to [(lon, lat), ...]
        points = [(pt["lon"], pt["lat"]) for pt in coords]

        # Sample elevations
        elevations = list(vrt.sample(points))
        values = [round(val[0], 2) if val[0] is not None else None for val in elevations]

        return jsonify({"elevations": values})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

