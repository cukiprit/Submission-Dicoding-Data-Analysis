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


categorical_df = pd.read_csv("data/categorical_df.csv")
numerical_df = pd.read_csv("data/numerical_df.csv")

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
        The metrics displayed above offer valuable insights into daily bike rentals spanning from January 1, 2011, to December 31, 2012, while considering influential factors such as weather and season. 'Total Rentals' provides a comprehensive overview, aggregating the cumulative count of all bike rentals ('cnt') to present a holistic perspective on overall bike usage. Additionally, 'Total Casual Users Rental' and 'Total Registered Users Rental' offer a detailed segmentation, shedding light on rental preferences among user types ('casual' and 'registered').

        Furthermore, the 'Delta' values accompanying these metrics represent day-to-day rental fluctuations. These variations encapsulate not only daily rental patterns but also account for the dynamic influence of external factors such as weather conditions ('Clear, Few clouds, Partly cloudy, Partly cloudy', 'Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist', 'Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds') and seasonal transitions ('Springer', 'Summer', 'Fall', 'Winter'). By continuously tracking these multifaceted trends over time, we gain profound insights into the intricate dynamics of bike rentals, enabling data-driven decisions related to resource allocation and service enhancements.
        """
    )

    st.divider()

    st.header("Business Questions")

    st.markdown(
        """
        The dataset can be systematically categorized into distinct groups, each offering valuable insights:

        - Temporal Attributes:
          This category encompasses temporal aspects, including the year, month, day. Analyzing these temporal trends allows us to discern patterns related to time-based variations in bike rentals.

        - Weather-Related Metrics:
          Within this group, we consider weather-related parameters such as the prevailing weather conditions, temperature, humidity levels, and wind speed. Examining these variables aids in understanding the impact of weather on bike rental demand and usage patterns.

        - Seasonal Characteristics:
          This category focuses on the seasonal context, identifying the prevailing season at a given time. Seasonal variations are pivotal in discerning how rental patterns evolve throughout the year.

        - User-Related Metrics:
          Here, we delve into user-specific data, comprising the counts of casual users, registered users, and the total number of rental bikes. This segmentation enables a comprehensive analysis of user behavior and preferences.
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

    st.caption(
        f"""
        The metrics displayed above offer valuable insights into daily bike rentals spanning from {start_date} to {end_date}, while considering influential factors such as weather and season. 'Total Rentals' provides a comprehensive overview, aggregating the cumulative count of all bike rentals ('cnt') to present a holistic perspective on overall bike usage. Additionally, 'Total Casual Users Rental' and 'Total Registered Users Rental' offer a detailed segmentation, shedding light on rental preferences among user types ('casual' and 'registered').

        Furthermore, the 'Delta' values accompanying these metrics represent day-to-day rental fluctuations. These variations encapsulate not only daily rental patterns but also account for the dynamic influence of external factors such as weather conditions ('Clear, Few clouds, Partly cloudy, Partly cloudy', 'Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist', 'Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds') and seasonal transitions ('Springer', 'Summer', 'Fall', 'Winter'). By continuously tracking these multifaceted trends over time, we gain profound insights into the intricate dynamics of bike rentals, enabling data-driven decisions related to resource allocation and service enhancements.
        """
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

    st.caption(
        f"""
        The analysis reveals insightful correlations between various factors impacting bike rentals. First, the 'Correlation between Temperature and Humidity' stands at {correlation_temp_hum * 100:.2f}%. This suggests a relatively weak relationship between temperature and humidity, implying that changes in one variable do not significantly affect the other.
        
        On the other hand, the 'Correlation between Temperature and Total Rentals' is notably stronger at {correlation * 100:.2f}%. This indicates a substantial connection between temperature and bike rentals, with higher temperatures generally associated with increased rental activity. As temperature rises, more people are inclined to rent bikes, likely due to favorable weather conditions. Understanding these correlations can help us make informed decisions and predict rental patterns based on temperature changes.
        """
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

    st.caption(
        """
        Analyzing the bike rental data, we observe intriguing statistics regarding the total rental counts ('cnt'). At its peak, we witnessed a remarkable day with a staggering 'Max Rentals' of 8714. On this particular day, bike usage reached its zenith, reflecting exceptional demand, possibly driven by ideal weather conditions or special events.

        Conversely, the dataset also reveals a contrasting scenario. On the other end of the spectrum, we encountered a day with 'Min Rentals' as low as 22. This represents a day of minimal bike rental activity, which could be attributed to adverse weather, holidays, or other factors influencing reduced bike usage.

        These extreme values in rental counts provide valuable insights into the dynamics of bike rentals, helping us identify both peak performance and potential areas for improvement in the bike rental service.
        """
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

    st.caption(
        f"""
        Exploring the data, we uncover intriguing statistics regarding casual bike rentals. At its peak, we observed an exceptional day with 'Max Rentals' reaching {main_df['casual'].max()} casual users. On this remarkable day, the demand for casual bike rentals surged to its highest point, signifying strong interest and potentially favorable weather conditions or special events that attracted users.

        Conversely, our analysis also unveils a contrasting scenario. On the other end of the spectrum, we encountered a day with 'Min Rentals' as low as {main_df['casual'].min()} casual rentals. On this particular day, rental activity among casual users was minimal, which could be attributed to factors like inclement weather or other external influences.

        These extreme values in casual bike rentals offer valuable insights into the dynamics of casual user preferences and the potential impact of external factors on their rental behavior. Understanding these variations can aid in optimizing service strategies to cater more effectively to casual users.
        """
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

    st.caption(
        f"""
        Delving into the dataset, we uncover noteworthy statistics pertaining to registered bike rentals. At its zenith, we observed an exceptional day with 'Max Rentals' peaking at {main_df['registered'].max()} registered users. On this remarkable day, registered bike rentals surged to their highest point, reflecting a robust demand and possibly ideal weather conditions or special events that enticed users to explore casual bike usage extensively.

        Conversely, our analysis also reveals a contrasting scenario. At the other end of the spectrum, we encountered a day with 'Min Rentals' dwindling to as low as {main_df['registered'].min()} registered rentals. On this particular day, rental activity among casual users reached its nadir, possibly influenced by adverse weather conditions or other external factors.

        These extreme values in registered bike rentals provide valuable insights into the dynamic preferences of registered users and underscore the potential impact of external variables on their rental behavior. Understanding these fluctuations can guide strategic decisions aimed at enhancing the service experience for registered riders.
        """
    )

st.divider()

with st.container():
    st.subheader("Seasonal Trends")
    st.line_chart(data=monthly_data)

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

    st.caption(
        """
        The data represents the total number of bike rentals for each month of the year. Here’s a more specific interpretation:

        - The year starts with a moderate number of rentals in January (134,933), which increases slightly in February (151,352).
        - In March, there’s a significant spike to 2,228,920 rentals. This could be due to warmer weather or other seasonal factors that make biking more popular.
        - From April to September, the numbers remain relatively high, ranging from 269,094 to 351,194. This period likely represents the peak biking season.
        - Starting in October, there’s a noticeable decrease in bike rentals, with numbers dropping to 211,036 by December. This could be due to colder weather or other factors that make biking less popular.

        This pattern suggests a strong seasonal trend in bike rentals, with demand peaking in the warmer months and decreasing in the colder months.
        """
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

    st.caption(
        f"""
        Our analysis of temperature data reveals key insights into the weather conditions during the period under examination.

        At its highest point, we observed a 'Max Temperature' of {(main_df['temp'].max() * 100):.2f}°C, signifying the peak temperature experienced during this timeframe. This maximum temperature value serves as an indicator of the hottest days, where individuals might be more inclined to engage in outdoor activities, including bike rentals.

        On average, the 'Mean Temperature' stands at {(main_df['temp'].mean() * 100):.2f}°C, providing an understanding of the typical temperature conditions throughout the dataset. This mean temperature serves as a central reference point, helping us gauge how the temperature typically behaves during the observed period.

        Conversely, we also encountered instances where the temperature reached 'Min Temperature' values as low as {(main_df['temp'].min() * 100):.2f}. These minimum temperature values represent the coldest days within the dataset, potentially influencing user behavior and outdoor activities.

        By examining these temperature metrics, we gain valuable insights into the range of temperature conditions experienced, allowing us to correlate weather patterns with bike rental trends and make data-informed decisions regarding resource allocation and service adjustments.
        """
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

    st.caption(
        f"""
        The humidity data you provided can be particularly insightful for your bike rental data analysis. Here's a more contextual explanation:

        - Maximum Humidity: The peak recorded relative humidity was {(main_df['hum'].max() * 100):.2f}%. Such high humidity levels could potentially deter bike rentals due to the discomfort associated with heavy moisture in the air, often leading to heavy rainfall or dense fog conditions.

        - Mean Humidity: The average relative humidity was {(main_df['hum'].mean() * 100):.2f}%. This moderate level of humidity suggests a balanced weather condition which might not significantly impact the decision to rent bikes.

        - Minimum Humidity: The lowest recorded relative humidity was {(main_df['hum'].min() * 100):.2f}%, indicating extremely dry conditions. While low humidity might make the weather seem more pleasant for outdoor activities like biking, extremely dry conditions can also cause discomfort and could potentially impact bike rental numbers.

        Understanding these humidity levels can help predict bike rental patterns and make informed decisions about resource allocation and marketing strategies. For instance, additional promotions could be planned for times when the weather is expected to have moderate humidity, which might boost rentals.
        """
    )

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
    fig = plt.figure(figsize=(10, 5))
    sns.boxplot(x="weathersit", y="cnt", data=numerical_df)
    st.pyplot(fig)

    st.caption(
        """
        This graph is titled “Bike Rentals by Weather Situation”. The x-axis represents the “Weather Situation” with three categories: 1, 2, and 3. The y-axis represents the “Total Rentals” ranging from 0 to 8000.

        - Weather situation 1 (represented by the blue bar) had approximately 7500 rentals.
        - Weather situation 2 (represented by the orange bar) had approximately 5000 rentals.
        - Weather situation 3 (represented by the green bar) had approximately 2500 rentals.

        Each bar has error bars, indicating the uncertainty in the data. From this graph, it’s clear that the number of bike rentals varies significantly depending on the weather situation. Specifically, weather situation 1 has the most rentals, while weather situation 3 has the least. This suggests that weather has a significant impact on bike rentals
        """
    )

with st.container():
    st.subheader("Conclusion")
    st.caption(
        """
        1. Is there a correlation between weather conditions and bike rentals?

            Here’s a breakdown:

            - For all weather conditions, the maximum number of rentals was 3410 and the minimum was 2. This wide range suggests that weather conditions could significantly impact bike rentals.

            - For cloudy weather conditions (including mist and broken clouds), the maximum number of rentals was 8362 and the minimum was 605. These figures are higher than the overall maximum and minimum, suggesting that these weather conditions might be more favorable for bike rentals.

            - For clear or partly cloudy weather conditions, the maximum number of rentals was even higher at 8714, while the minimum was 431. This suggests that clear or partly cloudy weather is likely the most favorable condition for bike rentals.

            - For adverse weather conditions like light snow or rain, the maximum number of rentals dropped to 4639 and the minimum was as low as 22. This indicates that such weather conditions are likely to deter people from renting bikes.

            In conclusion, there seems to be a strong correlation between weather conditions and bike rentals, with clear or partly cloudy weather being the most favorable for bike rentals, and adverse weather conditions like light snow or rain being the least favorable.
        """
    )
    st.caption(
        """
        2. How does the time of year affect the behavior of casual versus registered users?

            Based on the data provided, it appears that both the season and weather conditions have a significant impact on bike rentals for both registered and casual users. Here’s a breakdown:

            - **For registered users**
                * In the spring season, the maximum number of rentals was highest under clear or partly cloudy weather conditions (45,315 rentals), while the minimum number of rentals was lowest under light snow or rain conditions (432 rentals).
                * In the summer season, the maximum number of rentals was highest under clear or partly cloudy weather conditions (6,456 rentals), while the minimum number of rentals was lowest under light snow or rain conditions (674 rentals).
                * In the fall season, the maximum number of rentals was highest under clear or partly cloudy weather conditions (6,971 rentals), while the minimum number of rentals was lowest under light snow or rain conditions (1,689 rentals).
                * In the winter season, the maximum number of rentals was highest under clear or partly cloudy weather conditions (6,946 rentals), while the minimum number of rentals was lowest under light snow or rain conditions (20 rentals).

            - **For casual users**
                * In the spring season, the maximum number of rentals was highest under misty or cloudy weather conditions (3,155 rentals), while the minimum number of rentals was lowest under light snow or rain conditions (9 rentals).
                * In the summer season, the maximum number of rentals was highest under clear or partly cloudy weather conditions (3,410 rentals), while the minimum number of rentals was lowest under light snow or rain conditions (120 rentals).
                * In the fall season, the maximum number of rentals was highest under clear or partly cloudy weather conditions (3,160 rentals), while the minimum number of rentals was lowest under light snow or rain conditions (118 rentals).
                * In the winter season, the maximum number of rentals was highest under clear or partly cloudy weather conditions (3,031 rentals), while the minimum number of rentals was lowest under light snow or rain conditions (2 rentals).

            In conclusion, it appears that both registered and casual users prefer to rent bikes under clear or partly cloudy weather conditions across all seasons. However, registered users seem to be more tolerant of adverse weather conditions compared to casual users. This information could be valuable for predicting bike rental patterns and informing marketing strategies. For instance, additional promotions could be planned for times when the weather is expected to be clear or partly cloudy, which might boost rentals among casual users. Conversely, strategies could be developed to encourage bike rentals among casual users during adverse weather conditions.
        """
    )
