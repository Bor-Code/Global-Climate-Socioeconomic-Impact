import duckdb
import polars as pl
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from analyses.src import PROJECT_ROOT

DB_PATH = PROJECT_ROOT / "data" / "climate_wellbeing.duckdb"

def load_data():
    conn = duckdb.connect(str(DB_PATH))
    df = conn.execute("SELECT * FROM main_marts.fct_climate_economy").pl()
    conn.close()
    return df

def run_clustering(df: pl.DataFrame):
    print("\n--- KMeans Clustering: Country Profiles ---")
    latest_year = df['year'].max()
    latest_data = df.filter(pl.col('year') == latest_year).drop_nulls(
        subset=['gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption', 'generosity']
    )
    
    if len(latest_data) < 10:
        print("Not enough data for clustering.")
        return
        
    X = latest_data.select(['gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption', 'generosity']).to_pandas()
    countries = latest_data['country_name'].to_pandas()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    print(f"Clustered {len(X)} countries into 3 groups.")
    
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)
    print(f"PCA explained variance ratio: {pca.explained_variance_ratio_}")

def run_random_forest(df: pl.DataFrame):
    print("\n--- Random Forest Regression (Feature Importance) ---")
    latest_year = df['year'].max()
    latest_data = df.filter(pl.col('year') == latest_year).drop_nulls(
        subset=['happiness_score', 'gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption', 'generosity']
    )
    
    if len(latest_data) < 10:
        print("Not enough data for Random Forest.")
        return
        
    X = latest_data.select(['gdp_per_capita', 'social_support', 'life_expectancy', 'freedom', 'corruption', 'generosity']).to_pandas()
    y = latest_data['happiness_score'].to_pandas()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    
    y_pred_rf = rf_model.predict(X_test_scaled)
    mse_rf = mean_squared_error(y_test, y_pred_rf)
    r2_rf = r2_score(y_test, y_pred_rf)
    
    print(f"Random Forest R2 Score: {r2_rf:.4f}")
    print(f"Random Forest RMSE: {np.sqrt(mse_rf):.4f}")
    
    # Feature importances
    importances = list(zip(X.columns, rf_model.feature_importances_))
    importances.sort(key=lambda x: x[1], reverse=True)
    print("\nFeature Importances:")
    for feature, imp in importances:
        print(f"  {feature}: {imp:.4f}")

def main():
    print("=== PHASE 5: Machine Learning & Clustering ===")
    try:
        df = load_data()
        print(f"Loaded {len(df)} records from main_marts.fct_climate_economy.")
    except Exception as e:
        print(f"Failed to load data: {e}")
        return
        
    run_clustering(df)
    run_random_forest(df)

if __name__ == "__main__":
    main()
