import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
from scipy.stats import pearsonr

sns.set(style="dark")


def create_total_daily_rentals(df):
    """
    Create total daily rentals from a given DataFrame.

    Parameters:
    - df: The input DataFrame containing rental data.

    Returns:
    - daily_rentals: A DataFrame with total daily rentals, including the number of unique instances, the sum of rentals, and the count of rentals.
    """
    daily_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "cnt": ["sum", "count"]}
    )
    daily_rentals = daily_rentals.reset_index()

    return daily_rentals


def create_casual_daily_rentals(df):
    """
    Create casual daily rentals dataframe.

    Parameters:
    - df (pandas.DataFrame): The input dataframe containing rental data.

    Returns:
    - casual_rentals (pandas.DataFrame): The dataframe with daily casual rentals data.
    """
    casual_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "casual": ["sum", "count"]}
    )

    casual_rentals = casual_rentals.reset_index()

    return casual_rentals


def create_registered_daily_rentals(df):
    """
    Create registered daily rentals.

    Parameters:
    - df: DataFrame containing rental data.

    Returns:
    - register_rentals: DataFrame with aggregated registered daily rentals.
    """
    register_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "registered": ["sum", "count"]}
    )

    register_rentals = register_rentals.reset_index()

    return register_rentals


categorical_df = pd.read_csv("./dashboard/categorical_df.csv")
numerical_df = pd.read_csv("./dashboard/numerical_df.csv")

monthly_data = numerical_df.groupby("mnth").sum()["cnt"]

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

with st.container():
    st.title("Bike Rentals Dashboard")
    st.divider()
    st.header("Introduction")
    st.markdown(
        """
        The data set in question provides comprehensive information about bike rentals over the course of two years (2011 and 2012). The data is categorized by various factors such as time (year, month, hour), weather conditions (temperature, humidity, wind speed), and user type (casual or registered). This report aims to analyze this data, focusing specifically on the daily data, to identify patterns and correlations that could provide valuable insights for business development.
        """
    )

    st.divider()

with st.container():
    st.header("Daily Bike Rentals")

    col1, col2, col3 = st.columns(3)

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

st.divider()

with st.container():
    st.header("Correlations Between Variables")

    col1, col2 = st.columns(2)

    with col1:
        correlation_temp_hum, _ = pearsonr(main_df["temp"], main_df["hum"])
        st.metric(
            label="Correlation between Temperature and Humidity",
            value=f"{correlation_temp_hum * 100:.2f}%",
        )
    with col2:
        correlation, _ = pearsonr(main_df["temp"], main_df["cnt"])
        st.metric(
            label="Correlation between Temperature and Total Rentals",
            value=f"{correlation * 100:.2f}%",
        )

st.divider()

with st.container():
    st.header(f"Total Rentals")

    st.line_chart(data=main_df, x="dteday", y="cnt")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Max Rentals",
            value=main_df["cnt"].max(),
        )
    with col2:
        st.metric(
            label="Min Rentals",
            value=main_df["cnt"].min(),
        )

st.divider()

with st.container():
    st.header("Total Casual Users Rentals")

    st.line_chart(data=main_df, x="dteday", y="casual")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Max Rentals",
            value=main_df["casual"].max(),
        )
    with col2:
        st.metric(
            label="Min Rentals",
            value=main_df["casual"].min(),
        )

st.divider()

with st.container():
    st.subheader("Total Registered Users Rentals")
    st.line_chart(data=main_df, x="dteday", y="registered")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Max Rentals",
            value=main_df["registered"].max(),
        )

    with col2:
        st.metric(
            label="Min Rentals",
            value=main_df["registered"].min(),
        )

st.divider()

with st.container():
    st.subheader("Seasonal Trends")
    st.line_chart(data=monthly_data)

    cat_col_vis = ["season", "mnth"]

    fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(15, 15))
    i = 0

    for cols in cat_col_vis:
        sns.barplot(
            x=categorical_df[cols],
            y=categorical_df["cnt"],
            ax=ax[i],
            edgecolor="#c5c6c7",
        )

        ax[i].set_xlabel(" ")
        ax[i].set_ylabel(" ")
        ax[i].xaxis.set_tick_params(labelsize=14)
        ax[i].tick_params(left=False, labelleft=False)
        ax[i].set_ylabel(cols, fontsize=16)
        ax[i].bar_label(ax[i].containers[0], size="12")
        i = i + 1

    st.pyplot(plt)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Max Rentals",
            value=monthly_data.max(),
        )

    with col2:
        st.metric(
            label="Min Rentals",
            value=monthly_data.min(),
        )

st.divider()

with st.container():
    st.subheader("Temperature Trends")
    st.line_chart(data=main_df, x="dteday", y="temp")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Max Temperature",
            value=f"{(main_df['temp'].max() * 100):.2f}°C",
        )

    with col2:
        st.metric(
            label="Mean Temperature",
            value=f"{(main_df['temp'].mean() * 100):.2f}°C",
        )

    with col3:
        st.metric(
            label="Min Temperature",
            value=f"{(main_df['temp'].min() * 100):.2f}°C",
        )

with st.container():
    st.subheader("Humidity Trends")
    st.line_chart(data=main_df, x="dteday", y="hum")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Max Humidity", value=f"{(main_df['hum'].max() * 100):.2f}%")

    with col2:
        st.metric(label="Mean Humidity", value=f"{(main_df['hum'].mean() * 100):.2f}%")

    with col3:
        st.metric(label="Min Humidity", value=f"{(main_df['hum'].min() * 100):.2f}%")

with st.container():
    st.subheader("Wind Speed Trends")
    st.line_chart(data=main_df, x="dteday", y="windspeed")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Max Windspeed",
            value=f"{(main_df['windspeed'].max() * 100):.2f} km/h",
        )

    with col2:
        st.metric(
            label="Mean Windspeed",
            value=f"{(main_df['windspeed'].mean() * 100):.2f} km/h",
        )

    with col3:
        st.metric(
            label="Min Windspeed",
            value=f"{(main_df['windspeed'].min() * 100):.2f} km/h",
        )

with st.container():
    st.subheader("Weather Impact")

    plt.figure(figsize=(10, 5))
    sns.boxplot(x="weathersit", y="cnt", data=numerical_df)
    plt.title("Bike Rentals by Weather Situation")
    plt.xlabel("Weather Situation")
    plt.ylabel("Total Rentals")

    st.pyplot(plt)

    st.caption(
        """
        This graph is titled “Bike Rentals by Weather Situation”. The x-axis represents the “Weather Situation” with three categories: 1, 2, and 3. The y-axis represents the “Total Rentals” ranging from 0 to 8000. Weather significantly affects bike rentals in the following ways:

        - Clear, Few clouds, Partly cloudy, Partly cloudy (Weather Situation 1):
            
            This is the most favorable weather for bike rentals with approximately 7500 rentals. Clear or partly cloudy weather is ideal for outdoor activities like biking.

        - Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist (Weather Situation 2):
        
            This weather situation results in a decrease in bike rentals to approximately 5000. The presence of mist or broken clouds might make biking less appealing.

        - Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds (Weather Situation 3):
        
            This weather situation has the least favorable conditions for biking with approximately 2500 rentals. Inclement weather like rain, snow, or thunderstorms can discourage people from outdoor activities like biking due to safety concerns and discomfort.

        These trends suggest that favorable weather conditions (clear or partly cloudy) result in higher bike rentals while unfavorable conditions (rain, snow, thunderstorms) result in fewer rentals.
        """
    )

with st.container():
    st.subheader("User Impact")

    numerical_df["casual_percentage"] = numerical_df["casual"] / numerical_df["cnt"]
    numerical_df["registered_percentage"] = (
        numerical_df["registered"] / numerical_df["cnt"]
    )

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=numerical_df, x="mnth", y="casual_percentage", label="Casual")
    sns.lineplot(
        data=numerical_df, x="mnth", y="registered_percentage", label="Registered"
    )
    plt.title("Casual vs Registered Users Over Time")
    plt.xlabel("Month")
    plt.ylabel("Percentage of Total Rentals")
    plt.legend()

    st.pyplot(plt)

with st.container():
    st.subheader("Conclusion")

    with st.expander("How do bike rentals vary across different seasons and months?"):
        st.caption(
            """
            These trends suggest that weather and temperature play a significant role in influencing bike rental patterns. Warmer months and seasons tend to see higher demand for bike rentals, while colder periods see a decrease in demand.
            """
        )

    with st.expander("How does weather affect bike rentals?"):
        st.caption(
            """
            - Clear, Few clouds, Partly cloudy, Partly cloudy (Weather Situation 1): This is the most favorable weather for bike rentals with approximately 7500 rentals. Clear or partly cloudy weather is ideal for outdoor activities like biking.

            - Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist (Weather Situation 2): This weather situation results in a decrease in bike rentals to approximately 5000. The presence of mist or broken clouds might make biking less appealing.

            - Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds (Weather Situation 3): This weather situation has the least favorable conditions for biking with approximately 2500 rentals. Inclement weather like rain, snow, or thunderstorms can discourage people from outdoor activities like biking due to safety concerns and discomfort.
            """
        )

    with st.expander(
        "What are the differences between casual and registered users in terms of rental patterns?"
    ):
        st.caption(
            """
            - Casual Users: 
                
                The percentage of total rentals by casual users is higher than that of registered users for all months. There is a slight dip around the 6th month, after which it increases again. This suggests that casual users might be more influenced by factors such as weather, holidays, or events that occur around this time.

            - Registered Users:
            
                The percentage of total rentals by registered users is lower than that of casual users. There is a slight increase around the 6th month, after which it decreases again. This could indicate that registered users have more consistent usage patterns throughout the year, but there might be certain times (like the 6th month) when their usage increases.
            """
        )

    with st.expander(
        "Is there a correlation between weather conditions and bike rentals?"
    ):
        st.caption(
            """
            there seems to be a strong correlation between weather conditions and bike rentals, with clear or partly cloudy weather being the most favorable for bike rentals, and adverse weather conditions like light snow or rain being the least favorable.
            """
        )

    with st.expander(
        "How does the time of year affect the behavior of casual versus registered users?"
    ):
        st.caption(
            """
            It appears that both registered and casual users prefer to rent bikes under clear or partly cloudy weather conditions across all seasons. However, registered users seem to be more tolerant of adverse weather conditions compared to casual users. This information could be valuable for predicting bike rental patterns and informing marketing strategies. For instance, additional promotions could be planned for times when the weather is expected to be clear or partly cloudy, which might boost rentals among casual users. Conversely, strategies could be developed to encourage bike rentals among casual users during adverse weather conditions.
            """
        )

    with st.expander(
        "How can we optimize bike availability according to seasonal trends?"
    ):
        st.caption(
            """
            - Increase Availability During Peak Seasons:
            
                The data shows that bike rentals peak during the summer and fall seasons. Therefore, it would be beneficial to increase bike availability during these months to meet the high demand.
            
            - Maintenance and Repair During Off-Peak Seasons:
                
                The winter and spring seasons show a lower demand for bike rentals. This would be a good time to schedule regular maintenance and repairs to ensure that the bikes are in optimal condition for the peak season.

            - Promotional Activities:
                
                To encourage bike rentals during off-peak seasons or months with lower demand, promotional activities such as discounts or loyalty programs could be introduced.

            - Alternative Usage:
                
                During colder months when demand is low, consider alternative uses for the bikes. For example, they could be rented out for longer periods or used in partnership with local tour operators for guided tours.

            - Dynamic Pricing:
                
                Implement a dynamic pricing model where prices are lower during off-peak seasons to encourage usage, and higher during peak seasons when demand is high.

            - Weather-Proof Bikes:
                
                Consider investing in weather-proof bikes or providing additional equipment like rain covers or warmer gear during colder months to attract customers.
            """
        )

    with st.expander("Can we predict bike rental demand based on weather conditions?"):
        st.caption(
            """
            Yes, it is possible to predict bike rental demand based on weather conditions using machine learning models. Weather conditions such as temperature, humidity, wind speed, and weather situation (clear, cloudy, rainy, etc.) can significantly influence the demand for bike rentals.

            Based on the graph you provided, we can see clear trends in bike rentals across different weather situations. For instance, Weather Situation 1 (Clear, Few clouds, Partly cloudy) has the highest number of rentals, followed by Weather Situation 2 (Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds), and then Weather Situation 3 (Light Snow, Light Rain + Thunderstorm + Scattered clouds). This suggests that clear or partly cloudy weather is most favorable for bike rentals, while inclement weather like rain or snow reduces the demand.

            These trends can be used to train a machine learning model to predict bike rental demand based on weather conditions. The model could take in weather data as input and output the predicted number of bike rentals. This could be particularly useful for planning and resource allocation in bike rental services.
            """
        )
