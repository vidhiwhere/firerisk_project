# firerisk_project
🔥 FireRiskSim
AI/ML-based Forest Fire Prediction, Simulation, and Visualization Tool

📖 Overview
FireRiskSim is a web-based application designed to predict, simulate, and visualize forest fire risks using advanced AI/ML models combined with real-world geospatial data.
The platform helps researchers, environmentalists, and authorities visualize potential fire spread based on environmental factors like vegetation, weather, and terrain.

🚀 Key Features
Upload and process geospatial datasets (TIF, NDVI, MODIS, etc.)

Predict potential fire spread using AI/ML models.

Interactive Leaflet.js map for visualizing outputs.

Animate fire spread progression over time.

Customize simulation inputs: wind, humidity, NDVI threshold, ignition points.

Download predictions as CSV / GeoJSON.

Data visualization with Plotly (graphs, heatmaps).

Simple and intuitive user interface.

🛠 Tech Stack
Component	Technology
Frontend	HTML, CSS, JavaScript, Bootstrap, Leaflet.js
Backend	Python, Flask
Visualization	Plotly, Leaflet.js
Geospatial Data	Rasterio, Pandas, GeoTIFF files
ML / AI	Scikit-learn / Custom Models
Storage	Git LFS for large .tif files

🗂 Project Structure
csharp
Copy
Edit
├── data/
│   └── raw/            # GeoTIFF & related datasets
├── model/              # ML models
├── static/             # CSS, JS, images
├── templates/          # HTML templates (Flask)
├── utils/              # Python utilities (raster, fire spread)
├── app.py              # Main Flask application
├── README.md           # Project overview
└── .gitattributes      # Git LFS tracking
🔧 How to Run Locally
1️⃣ Clone the repo:

bash
Copy
Edit
git clone https://github.com/vidhiwhere/firerisk_project.git
cd firerisk_project
2️⃣ Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
3️⃣ Run the app:

bash
Copy
Edit
python app.py
4️⃣ Visit: http://localhost:5000

📊 Example Outputs
Fire risk maps

Animated spread simulation

Graphs for environmental factors

Downloadable CSV / GeoJSON

🌍 Use Cases
Environmental research

Disaster management authorities

Academic projects on geospatial AI/ML

Educational visualization tools

📢 Acknowledgments
Thanks to open-source datasets: MODIS, ERA5, SRTM, and NASA FIRMS for providing valuable environmental data.

🤝 Contributing
Open to collaboration, contributions, and feedback!
Feel free to create issues or pull requests.

📄 License
This project is licensed under the MIT License.

