import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
sns.set(style='dark')

def create_total_daily_rentals(df):
  daily_rentals = df.resample(rule='D', on='dteday').agg({
    'instant': 'nunique',
    'cnt': 'sum'
  })

  daily_rentals = daily_rentals.reset_index()

  return daily_rentals

categorical_df = pd.read_csv('data/merged_categorical_df.csv')

categorical_df['dteday'] = pd.to_datetime(categorical_df['dteday'])

min_date = categorical_df['dteday'].min()
max_date = categorical_df['dteday'].max()

with st.sidebar:
  st.header("Portofolio Data Analisis Rental Sepeda")

  start_date, end_date = st.date_input(
    label="Rentang Waktu",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
  )

  main_df = categorical_df[(categorical_df["dteday"] >= str(start_date)) & 
                   (categorical_df["dteday"] <= str(end_date))]
  
  total_rentals = create_total_daily_rentals(main_df)

st.header("Bike Rentals Dashboard")

col1, col2 = st.columns(2)

with col1:
  total_rentals = total_rentals.instant.sum()
  st.metric(label="Total Rentals", value=total_rentals)

with col2:
  st.dataframe(categorical_df)