from flask import Flask, jsonify, render_template, request
from utils.rasters_utils import read_tif_as_df
from utils.fire_spread import generate_fire_spread
import rasterio
import numpy as np
import os
import pickle
from flask import send_file
import pandas as pd
import geojson
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# ✅ Load model once at startup
import joblib

MODEL_PATH = 'model/fire_risk_model.pkl'
model = None

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully.")
else:
    print("⚠️ Model not found! Please run train_model.py first.")
    model = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/api/merged-data')
def merged_data():
    try:
        files = [
            'data/raw/modis_ndvi_uttarakhand_2023.tif',
            'data/raw/era5_temp_uttarakhand_jan2023.tif',
            'data/raw/srtm_uttarakhand_2023.tif',
            'data/raw/burned_area_2023.tif',
            'data/raw/viirs_fire_uttarakhand_2023.tif'
        ]
        for file in files:
            if not os.path.exists(file):
                print(f"⚠️ File not found: {file}")
                return jsonify({'error': f'File not found: {file}'}), 500

        df_ndvi = read_tif_as_df('data/raw/modis_ndvi_uttarakhand_2023.tif', 'ndvi')
        df_temp = read_tif_as_df('data/raw/era5_temp_uttarakhand_jan2023.tif', 'temp')
        df_elev = read_tif_as_df('data/raw/srtm_uttarakhand_2023.tif', 'elevation')
        df_burned = read_tif_as_df('data/raw/burned_area_2023.tif', 'burned')
        df_viirs = read_tif_as_df('data/raw/viirs_fire_uttarakhand_2023.tif', 'viirs_fire')

        print(f"✅ Loaded shapes - NDVI: {df_ndvi.shape}, Temp: {df_temp.shape}, Elev: {df_elev.shape}, Burned: {df_burned.shape}, VIIRS: {df_viirs.shape}")

        df_final = df_ndvi.merge(df_temp, on=['x', 'y']) \
                         .merge(df_elev, on=['x', 'y']) \
                         .merge(df_burned, on=['x', 'y']) \
                         .merge(df_viirs, on=['x', 'y'])
        print(f"✅ Merged DataFrame columns: {df_final.columns.tolist()}")
        print(f"✅ Rows before dropna: {len(df_final)}")
        df_final.dropna(inplace=True)
        print("✅ Returning", len(df_final), "records after dropping NA")
        return df_final.to_json(orient='records')
    except Exception as e:
        print("❌ Error in /api/merged-data:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/fire-spread')
def fire_spread():
    ignition_x, ignition_y = 10, 10
    frames = generate_fire_spread(ignition_x, ignition_y, steps=15)
    return jsonify(frames)

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.get_json()
        features = np.array([
            data['ndvi'],
            data['temp'],
            data['elevation']
        ]).reshape(1, -1)
    except (KeyError, TypeError):
        return jsonify({'error': 'Invalid input format'}), 400

    prediction = model.predict(features)[0]
    return jsonify({'fire_risk': int(prediction)})

@app.route('/api/simulate-spread', methods=['POST'])
def simulate_spread():
    from collections import deque
    import math

    data = request.get_json()
    start_x = data['x']
    start_y = data['y']
    threshold = data.get('threshold', 0.5)
    max_steps = data.get('steps', 10)
    wind_speed = data.get('windSpeed', 10)
    wind_dir = data.get('windDir', 90)
    humidity = data.get('humidity', 30)

    wind_dx = round(math.cos(math.radians(wind_dir)))
    wind_dy = round(math.sin(math.radians(wind_dir)))

    df = read_tif_as_df('data/raw/viirs_fire_uttarakhand_2023.tif', 'viirs_fire')
    df = df.merge(read_tif_as_df('data/raw/modis_ndvi_uttarakhand_2023.tif', 'ndvi'), on=['x', 'y'])
    df = df.merge(read_tif_as_df('data/raw/era5_temp_uttarakhand_jan2023.tif', 'temp'), on=['x', 'y'])
    df = df.merge(read_tif_as_df('data/raw/srtm_uttarakhand_2023.tif', 'elevation'), on=['x', 'y'])

    fire_map = {}
    for _, row in df.iterrows():
        fire_map[(int(row['x']), int(row['y']))] = {
            'ndvi': row['ndvi'],
            'temp': row['temp'],
            'elevation': row['elevation'],
            'burned': False
        }

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    queue = deque()
    queue.append((start_x, start_y, 0))
    spread_path = []

    while queue:
        x, y, step = queue.popleft()
        key = (x, y)

        if key not in fire_map or fire_map[key]['burned']:
            continue

        fire_map[key]['burned'] = True
        spread_path.append({'x': x, 'y': y, 'step': step})

        if step >= max_steps:
            continue

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            nkey = (nx, ny)

            if nkey in fire_map and not fire_map[nkey]['burned']:
                ndvi_val = fire_map[nkey]['ndvi']
                temp_val = fire_map[nkey]['temp']

                wind_boost = 1.0
                if dx == wind_dx and dy == wind_dy:
                    wind_boost += wind_speed / 20.0

                humidity_penalty = 1.0 - (humidity / 100.0)
                adjusted_ndvi = ndvi_val * wind_boost * humidity_penalty

                if adjusted_ndvi > threshold and temp_val > 20:
                    queue.append((nx, ny, step + 1))

    return jsonify(spread_path)

@app.route('/api/predict-point')
def predict_point():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except:
        return jsonify({'error': 'Missing or invalid lat/lon'}), 400

    origin_lat, origin_lon = 30.0668, 79.0193
    resolution = 0.01
    x = int((lon - origin_lon) / resolution)
    y = int((lat - origin_lat) / resolution)

    def sample_value(file_path):
        try:
            with rasterio.open(file_path) as src:
                return float(src.read(1)[y, x])
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    ndvi = sample_value('data/raw/modis_ndvi_uttarakhand_2023.tif')
    temp = sample_value('data/raw/era5_temp_uttarakhand_jan2023.tif')
    elev = sample_value('data/raw/srtm_uttarakhand_2023.tif')
    viirs = sample_value('data/raw/viirs_fire_uttarakhand_2023.tif')

    features = [ndvi, temp, elev]
    prediction = "Model not loaded"

    if model and all(f is not None for f in features):
        prediction = model.predict([features])[0]

    return jsonify({
        "ndvi": round(ndvi, 2) if ndvi else None,
        "temp": round(temp, 2) if temp else None,
        "elevation": round(elev, 2) if elev else None,
        "viirs_fire": round(viirs, 2) if viirs else None,
        "prediction": prediction
    })

@app.route('/download/fire-risk')
def download_fire_risk():
    df = pd.read_csv("merged_data.csv")
    csv_io = io.StringIO()
    df.to_csv(csv_io, index=False)
    csv_io.seek(0)
    return send_file(
        io.BytesIO(csv_io.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="fire_risk_data.csv"
    )

@app.route('/download/fire-spread')
def download_fire_spread():
    spread_data = [
        {"x": 10, "y": 12},
        {"x": 11, "y": 12},
        {"x": 11, "y": 13},
    ]

    features = []
    for pt in spread_data:
        lat = 30.0668 + pt["y"] * 0.01
        lon = 79.0193 + pt["x"] * 0.01
        features.append(geojson.Feature(geometry=geojson.Point((lon, lat))))

    geo = geojson.FeatureCollection(features)
    geo_io = io.StringIO()
    geojson.dump(geo, geo_io)
    geo_io.seek(0)

    return send_file(
        io.BytesIO(geo_io.getvalue().encode()),
        mimetype="application/geo+json",
        as_attachment=True,
        download_name="fire_spread.geojson"
    )

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=10000)

