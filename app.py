from flask import Flask, request, jsonify
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling

app = Flask(__name__)

# Load your SRTM GeoTIFF once
tiff_path = "srtm_cog.tif"
src = rasterio.open(tiff_path)

# Open dataset and create a VRT for reprojection/resampling if necessary
src = rasterio.open(tiff_path)
vrt = WarpedVRT(src, resampling=Resampling.bilinear)

@app.route("/elevation", methods=["POST"])
def get_elevation():
    try:
        data = request.get_json()
        coords = data.get("points", [])  # Expect [{"lat": ..., "lon": ...}, ...]

        if not coords:
            return jsonify({"error": "No coordinates provided"}), 400

        # Convert to [(lon, lat), ...] as rasterio uses (x, y) = (lon, lat)
        points = [(pt["lon"], pt["lat"]) for pt in coords]

        # Sample elevations at the given points
        elevations = list(vrt.sample(points))
        # Convert numpy int16 to float and round to 2 decimals
        values = [float(round(val[0], 2)) if val[0] is not None else None for val in elevations]

        return jsonify({"elevations": values})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
