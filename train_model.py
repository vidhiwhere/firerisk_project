import pandas as pd
from utils.rasters_utils import read_tif_as_df
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# 🔹 Step 1: Load and merge data
df_ndvi = read_tif_as_df('data/raw/modis_ndvi_uttarakhand_2023.tif', 'ndvi')
df_temp = read_tif_as_df('data/raw/era5_temp_uttarakhand_jan2023.tif', 'temp')
df_elev = read_tif_as_df('data/raw/srtm_uttarakhand_2023.tif', 'elevation')
df_viirs = read_tif_as_df('data/raw/viirs_fire_uttarakhand_2023.tif', 'viirs_fire')
df_burned = read_tif_as_df('data/raw/burned_area_2023.tif', 'burned')

df = df_ndvi.merge(df_temp, on=['x', 'y'])
df = df.merge(df_elev, on=['x', 'y'])
df = df.merge(df_viirs, on=['x', 'y'])
df = df.merge(df_burned, on=['x', 'y'])

df.dropna(inplace=True)

# 🔹 Step 2: Define features and target
X = df[['ndvi', 'temp', 'elevation', 'viirs_fire']]
y = df['burned'] > 0  # Convert burned area into binary class (fire: True/False)

# 🔹 Step 3: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 Step 4: Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 🔹 Step 5: Evaluate
print("✅ Classification Report:\n")
print(classification_report(y_test, model.predict(X_test)))

# 🔹 Step 6: Save the model
os.makedirs('model', exist_ok=True)
joblib.dump(model, 'model/fire_risk_model.pkl')
print("✅ Model saved to 'model/fire_risk_model.pkl'")

