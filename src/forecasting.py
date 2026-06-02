import pandas as pd
from sklearn.linear_model import LinearRegression

def forecast_revenue(monthly_df, periods=6):
    df = monthly_df.copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values("month")

    df["time_index"] = range(len(df))

    X = df[["time_index"]]
    y = df["revenue"]

    model = LinearRegression()
    model.fit(X, y)

    future_indexes = list(range(len(df), len(df) + periods))

    future_dates = pd.date_range(
        df["month"].max() + pd.DateOffset(months=1),
        periods=periods,
        freq="MS"
    )

    future_df = pd.DataFrame({
        "month": future_dates,
        "time_index": future_indexes
    })

    future_df["forecasted_revenue"] = model.predict(future_df[["time_index"]])

    return future_df[["month", "forecasted_revenue"]]
