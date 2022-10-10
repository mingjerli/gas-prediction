import re

import numpy as np
import pandas as pd
import requests


def get_weekly_gas_price_data():
    response = requests.get(
        "https://www.eia.gov/petroleum/gasdiesel/xls/pswrgvwall.xls"
    )
    df = pd.read_excel(
        response.content,
        sheet_name="Data 12",
        index_col=0,
        skiprows=2,
        parse_dates=["Date"],
    ).rename(
        columns=lambda c: re.sub(
            "\(PADD 1[A-C]\)",
            "",
            c.replace("Weekly ", "").replace(
                " All Grades All Formulations Retail Gasoline Prices  (Dollars per Gallon)",
                "",
            ),
        ).strip()
    )
    df_long = (
        df.reset_index()
        .melt(id_vars=["Date"], var_name="region", value_name="price")
        .rename(columns={"Date": "week"})
        .sort_values(["region", "week"])
        .assign(
            # if we're missing one value, just use the last value
            # (happens twice)
            price=lambda x: x["price"].combine_first(
                x.groupby("region")["price"].shift(1)
            ),
            # we'll forecast log(price) and then transform
            log_price=lambda x: np.log(x["price"]),
            # percentage price changes are approximately the difference in log(price)
            price_change=lambda x: (
                x["log_price"] - x.groupby("region")["log_price"].shift(1)
            ),
        )
        .query("price == price")  # filter out NAs
    )
    return df_long


def run_session_including_weekly_gas_price_data():
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    df_long = get_weekly_gas_price_data()
    artifacts["weekly_gas_price_data"] = copy.deepcopy(df_long)
    return artifacts


def run_all_sessions():
    artifacts = dict()
    artifacts.update(run_session_including_weekly_gas_price_data())
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    artifacts = run_all_sessions()
    print(artifacts)
