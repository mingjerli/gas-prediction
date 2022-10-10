# main.py

from fastapi import FastAPI
from price_change_all_regions_module import get_all_regions
from price_change_all_regions_module import get_price_change
from price_change_all_regions_module import get_df_long_for_artifact_all_regions_and_downstream

app = FastAPI()

@app.get("/regions/")
def all_regions():
    df_long = get_df_long_for_artifact_all_regions_and_downstream()
    all_regions = get_all_regions(df_long)
    return '|'.join(all_regions)
    
@app.get("/{region}/pricechange/")
def price_change(region):
    df_long = get_df_long_for_artifact_all_regions_and_downstream()
    price_change = get_price_change(df_long, region)
    return f"Gas price in {region} is expected to change {price_change:.2f} next week."
    
