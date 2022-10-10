import argparse

import numpy as np
import pandas as pd
from statsforecast.models import AutoARIMA


def get_df_long_for_artifact_all_regions_and_downstream():
    df_long = pd.read_csv("weekly_gas_price_data_long.csv", parse_dates=["week"])
    return df_long


def get_all_regions(df_long):
    all_regions = df_long["region"].unique().tolist()
    return all_regions


def get_price_change(df_long, region):
    H = 13
    CI = 80
    cutoff_date = pd.Timestamp.today().strftime("%Y-%m-%d")
    region_df = df_long.query(f"region == '{region}'")
    train = region_df.query(f"week <= '{cutoff_date}'")
    m_aa = AutoARIMA()
    m_aa.fit(train["log_price"].values)
    raw_forecast = m_aa.predict(h=H, level=(CI,))
    raw_forecast_exp = {key: np.exp(value) for key, value in raw_forecast.items()}
    forecast = pd.DataFrame(raw_forecast_exp).assign(
        week=pd.date_range(train["week"].max(), periods=H, freq="W")
        + pd.Timedelta("7 days")
    )
    current_price = train.price.iloc[-1]
    forecast_price = forecast["mean"].iloc[0]
    price_change = forecast_price - current_price
    return price_change


def run_session_including_all_regions(region="U.S."):
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    df_long = get_df_long_for_artifact_all_regions_and_downstream()
    all_regions = get_all_regions(df_long)
    artifacts["all_regions"] = copy.deepcopy(all_regions)
    price_change = get_price_change(df_long, region)
    artifacts["price_change"] = copy.deepcopy(price_change)
    return artifacts


def run_all_sessions(
    region="U.S.",
):
    artifacts = dict()
    artifacts.update(run_session_including_all_regions(region))
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, default="U.S.")
    args = parser.parse_args()
    artifacts = run_all_sessions(
        region=args.region,
    )
    print(artifacts)
