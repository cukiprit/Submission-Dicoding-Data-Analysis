import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
from scipy.stats import pearsonr

sns.set(style="dark")


def create_total_daily_rentals(df):
    daily_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "cnt": ["sum", "count"]}
    )
    daily_rentals = daily_rentals.reset_index()

    return daily_rentals


def create_casual_daily_rentals(df):
    casual_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "casual": ["sum", "count"]}
    )

    casual_rentals = casual_rentals.reset_index()

    return casual_rentals


def create_registered_daily_rentals(df):
    register_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "registered": ["sum", "count"]}
    )

    register_rentals = register_rentals.reset_index()

    return register_rentals


categorical_df = pd.read_csv("data/categorical_df.csv")
numerical_df = pd.read_csv("data/numerical_df.csv")

monthly_data = numerical_df.groupby("mnth").sum()["cnt"]
correlation, _ = pearsonr(categorical_df["temp"], categorical_df["cnt"])

categorical_df["casual_percentage"] = categorical_df["casual"] / categorical_df["cnt"]
categorical_df["registered_percentage"] = (
    categorical_df["registered"] / categorical_df["cnt"]
)

categorical_df["dteday"] = pd.to_datetime(categorical_df["dteday"])

min_date = categorical_df["dteday"].min()
max_date = categorical_df["dteday"].max()

with st.sidebar:
    st.header("Portofolio Data Analysis Bike Rental")

    start_date, end_date = st.date_input(
        label="Period",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

    season = st.selectbox(
        label="Select the season",
        options=["All"] + list(categorical_df["season"].unique()),
    )

    weathersit = st.selectbox(
        label="Select the weather",
        options=["All"] + list(categorical_df["weathersit"].unique()),
    )

    if season == "All" and weathersit == "All":
        main_df = categorical_df[
            (categorical_df["dteday"] >= str(start_date))
            & (categorical_df["dteday"] <= str(end_date))
        ]
    elif season == "All":
        main_df = categorical_df[
            (categorical_df["dteday"] >= str(start_date))
            & (categorical_df["dteday"] <= str(end_date))
            & (categorical_df["weathersit"] == weathersit)
        ]
    elif weathersit == "All":
        main_df = categorical_df[
            (categorical_df["dteday"] >= str(start_date))
            & (categorical_df["dteday"] <= str(end_date))
            & (categorical_df["season"] == season)
        ]
    else:
        main_df = categorical_df[
            (categorical_df["dteday"] >= str(start_date))
            & (categorical_df["dteday"] <= str(end_date))
            & (categorical_df["season"] == season)
            & (categorical_df["weathersit"] == weathersit)
        ]

    total_rentals = create_total_daily_rentals(main_df)
    casual_rentals = create_casual_daily_rentals(main_df)
    register_rentals = create_registered_daily_rentals(main_df)

    total_rentals["total_diff"] = total_rentals["cnt"]["sum"].diff()
    casual_rentals["casual_diff"] = casual_rentals["casual"]["sum"].diff()
    register_rentals["register_diff"] = register_rentals["registered"]["sum"].diff()

st.title("Bike Rentals Dashboard")

st.subheader("Introduction")
st.divider()
st.caption(
    "The data set in question provides comprehensive information about bike rentals over the course of two years (2011 and 2012). The data is categorized by various factors such as time (year, month, hour), weather conditions (temperature, humidity, wind speed), and user type (casual or registered). This report aims to analyze this data, focusing specifically on the daily data, to identify patterns and correlations that could provide valuable insights for business development."
)

col1, col2, col3 = st.columns(3)

st.text(("total_diff" in total_rentals.columns))

with col1:
    sum_total_rentals = total_rentals["cnt", "sum"].sum()
    st.metric(
        label="Total Rentals",
        value=sum_total_rentals,
        delta=total_rentals["total_diff"].iloc[-1],
    )

with col2:
    sum_casual_rentals = casual_rentals["casual", "sum"].sum()
    st.metric(
        label="Total Casual Users Rental",
        value=sum_casual_rentals,
        delta=casual_rentals["casual_diff"].iloc[-1],
    )

with col3:
    sum_register_rentals = register_rentals["registered", "sum"].sum()
    st.metric(
        label="Total Registered Users Rental",
        value=sum_register_rentals,
        delta=register_rentals["register_diff"].iloc[-1],
    )

st.subheader("Total Rentals")
st.line_chart(data=main_df, x="dteday", y="cnt")

st.subheader("Total Casual Users Rentals")
st.line_chart(data=main_df, x="dteday", y="casual")

st.subheader("Total Registered Users Rentals")
st.line_chart(data=main_df, x="dteday", y="registered")

st.subheader("Seasonal Trends")
st.line_chart(data=monthly_data)

# Temperature trends over time
st.subheader("Temperature Trends")
st.line_chart(data=main_df, x="dteday", y="temp")

# Humidity trends over time
st.subheader("Humidity Trends")
st.line_chart(data=main_df, x="dteday", y="hum")

# Wind speed trends over time
st.subheader("Wind Speed Trends")
st.line_chart(data=main_df, x="dteday", y="windspeed")

# Correlation between temperature and humidity
correlation_temp_hum, _ = pearsonr(main_df["temp"], main_df["hum"])
st.write(
    f"Correlation between Temperature and Humidity: {correlation_temp_hum * 100:.2f}%"
)
st.write(f"Correlation between temperature and total rentals: {correlation * 100:.2f}%")

# Additional statistics and insights about weather variables
mean_temp = main_df["temp"].mean()
max_wind_speed = main_df["windspeed"].max()
min_humidity = main_df["hum"].min()

st.write(f"Mean Temperature: {mean_temp:.2f}")
st.write(f"Max Wind Speed: {max_wind_speed:.2f}")
st.write(f"Min Humidity: {min_humidity:.2f}")

st.subheader("Weather Impact")
fig = plt.figure(figsize=(10, 5))
sns.boxplot(x="weathersit", y="cnt", data=numerical_df)
st.pyplot(fig)
