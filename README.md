# Bike Rentals Data Analyst

## Setup environment

    conda create --name data-analyst
    conda activate data-analyst
    pip install numpy pandas scipy matplotlib seaborn streamlit

## Run streamlit app

    cd dashboard
    streamlit run main.py

## How to use

Guide on how to use the website for your bike rental data analysis:

- Date Input: This input allows you to set the range of data you want to analyze. You can select a specific start and end date, and the website will display data only within this range.

- Season Select Box: This dropdown menu allows you to filter the data based on the season. You can select a specific season, and the website will display data only for that season.

- Weather Select Box: This dropdown menu allows you to filter the data based on the weather conditions. You can select a specific weather condition, and the website will display data only for that condition.

You can combine these three inputs to visualize data based on a specific date range, season, and weather condition. For example, if you want to analyze bike rentals during the summer season on clear days, you would set the date range to cover the summer months, select ‘Summer’ from the Season Select Box, and ‘Clear’ from the Weather Select Box.

The main area of the website displays various graphs of bike rental data. These graphs will update based on the inputs you select, allowing you to visualize and analyze different aspects of the data.
