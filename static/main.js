window.onload = function () {
  const map = L.map('map').setView([30.0668, 79.0193], 9);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18
  }).addTo(map);

  let heatLayer;

  // 🔘 Load a heatmap layer by property
  window.loadLayer = function (property) {
    console.log("👉 Loading property:", property);

    fetch('/api/merged-data')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then(data => {
        console.log("✅ Received merged data sample:", data.slice(0, 5));

        if (!data || data.length === 0) {
          console.warn("⚠️ No data returned from API!");
          alert("⚠️ No data available for " + property);
          return;
        }

        const heatData = data
          .filter(p => p.hasOwnProperty('x') && p.hasOwnProperty('y') && p[property] !== null)
          .map(p => [
            30.0668 + (p.y * 0.01),
            79.0193 + (p.x * 0.01),
            (p[property] || 0) * 5
          ]);

        console.log("📌 HeatData points:", heatData.length);
        if (heatData.length === 0) alert("⚠️ No valid data for " + property);

        if (heatLayer) map.removeLayer(heatLayer);

        heatLayer = L.heatLayer(heatData, {
          radius: 25,
          blur: 20,
          maxZoom: 12,
          gradient: {
            0.2: 'blue',
            0.4: 'lime',
            0.6: 'orange',
            0.8: 'red'
          }
        }).addTo(map);
      })
      .catch(err => {
        console.error("❌ Fetch or processing error for /api/merged-data:", err);
        alert("❌ Failed to load data for " + property + ". Check console for details.");
      });
  };

  // 📊 Load Plotly charts
  function loadCharts() {
    console.log("📊 loadCharts() called");

    fetch('/api/merged-data')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then(data => {
        console.log("✅ Sample chart data:", data.slice(0, 5));

        const ndvi = [], temp = [], elev = [], fire = [];

        data.forEach(d => {
          if (d.ndvi && d.temp && d.elevation && d.viirs_fire) {
            ndvi.push(d.ndvi);
            temp.push(d.temp);
            elev.push(d.elevation);
            fire.push(d.viirs_fire);
          }
        });

        console.log("✅ Points to plot:", ndvi.length, temp.length, elev.length, fire.length);

        if (fire.length === 0) {
          console.warn("⚠️ No valid fire data to plot charts!");
          alert("⚠️ No valid fire data available for charts.");
          return;
        }

        Plotly.newPlot('chart1', [{
          x: ndvi,
          y: fire,
          mode: 'markers',
          type: 'scatter',
          marker: { color: 'green' }
        }], {
          title: 'Fire Intensity vs NDVI',
          xaxis: { title: 'NDVI' },
          yaxis: { title: 'Fire Intensity (VIIRS)' }
        });

        Plotly.newPlot('chart2', [{
          x: temp,
          y: fire,
          mode: 'markers',
          type: 'scatter',
          marker: { color: 'red' }
        }], {
          title: 'Fire Intensity vs Temperature',
          xaxis: { title: 'Temperature (°C)' },
          yaxis: { title: 'Fire Intensity (VIIRS)' }
        });

        Plotly.newPlot('chart3', [{
          x: elev,
          y: fire,
          mode: 'markers',
          type: 'scatter',
          marker: { color: 'purple' }
        }], {
          title: 'Fire Intensity vs Elevation',
          xaxis: { title: 'Elevation (m)' },
          yaxis: { title: 'Fire Intensity (VIIRS)' }
        });
      })
      .catch(err => {
        console.error("❌ Error loading chart data:", err);
        alert("❌ Failed to load chart data. Check console for details.");
      });
  };

  // 📍 Show popup on map click
  map.on('click', function (e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;

    fetch(`/api/predict-point?lat=${lat}&lon=${lon}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then(data => {
        if (!data || Object.keys(data).length === 0) {
          alert("⚠️ No data available for this location.");
          return;
        }
        const popup = L.popup()
          .setLatLng([lat, lon])
          .setContent(`
            <strong>📍 Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}</strong><br/>
            🌿 NDVI: ${data.ndvi || 'N/A'} <br/>
            🌡 Temp: ${data.temp || 'N/A'} °C <br/>
            🏔 Elevation: ${data.elevation || 'N/A'} m <br/>
            🔥 VIIRS Fire: ${data.viirs_fire || 'N/A'} <br/>
            🔥 Predicted Fire Risk: <b>${data.prediction || 'N/A'}</b>
          `)
          .openOn(map);
      })
      .catch(err => {
        console.error("❌ Error fetching point data:", err);
        alert("❌ Failed to fetch point data. Check console for details.");
      });
  });

  // 🌙 Dark Mode Toggle
  const darkModeButton = document.getElementById('darkModeToggle');
  if (darkModeButton) {
    darkModeButton.addEventListener('click', function () {
      document.body.classList.toggle('dark-mode');
      if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
      } else {
        localStorage.setItem('theme', 'light');
      }
    });
  }

  // Load saved theme preference
  if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
  }

  // 🔁 Initial load
  loadLayer('viirs_fire');
  loadCharts();
};

// 🔘 Predict fire risk
function makePrediction() {
  fetch('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ndvi: 7231,
      temp: 27,
      elevation: 560
    })
  })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP error ${res.status}: ${res.statusText}`);
      return res.json();
    })
    .then(result => {
      console.log("🔥 Fire Risk Prediction:", result.fire_risk);
      document.getElementById('predictionResult').textContent =
        `🔥 Predicted Fire Risk: ${result.fire_risk}`;
    })
    .catch(err => {
      console.error("❌ Prediction error:", err);
      document.getElementById('predictionResult').textContent =
        "❌ Failed to fetch prediction.";
    });
}

// 🔥 Simulate fire spread (static)
function simulateFireSpread() {
  const ignitionX = 10;
  const ignitionY = 10;
  const threshold = 0.4;
  const steps = 8;

  const windSpeed = parseFloat(document.getElementById('windSpeed').value);
  const windDir = parseFloat(document.getElementById('windDir').value);
  const humidity = parseFloat(document.getElementById('humidity').value);

  fetch('/api/simulate-spread', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      x: ignitionX,
      y: ignitionY,
      threshold,
      steps,
      windSpeed,
      windDir,
      humidity
    })
  })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP error ${res.status}: ${res.statusText}`);
      return res.json();
    })
    .then(data => {
      const spreadPoints = data.map(d => {
        const lat = 30.0668 + (d.y * 0.01);
        const lon = 79.0193 + (d.x * 0.01);
        return [lat, lon];
      });

      L.heatLayer(spreadPoints, {
        radius: 30,
        blur: 25,
        maxZoom: 13,
        gradient: {
          0.2: 'yellow',
          0.5: 'orange',
          0.8: 'red'
        }
      }).addTo(map);
    })
    .catch(err => {
      alert("🔥 Fire spread simulation failed");
      console.error(err);
    });
}

// 🔁 Animate fire spread (dynamic)
function animateFireSpread() {
  fetch('/api/fire-spread')
    .then(res => {
      if (!res.ok) throw new Error(`HTTP error ${res.status}: ${res.statusText}`);
      return res.json();
    })
    .then(frames => {
      let i = 0;
      let animationInterval;

      function showFrame() {
        if (i >= frames.length) {
          clearInterval(animationInterval);
          return;
        }

        const heatData = frames[i].map(p => [
          30.0668 + (p.y * 0.01),
          79.0193 + (p.x * 0.01),
          p.intensity
        ]);

        if (window.animatedLayer) {
          map.removeLayer(window.animatedLayer);
        }

        window.animatedLayer = L.heatLayer(heatData, {
          radius: 20,
          blur: 15,
          maxZoom: 12,
          gradient: { 0.4: 'orange', 0.7: 'red' }
        }).addTo(map);

        i++;
      }

      animationInterval = setInterval(showFrame, 500);
    })
    .catch(err => {
      alert("❌ Animation failed");
      console.error(err);
    });
}