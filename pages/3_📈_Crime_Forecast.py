import streamlit as st
import pandas as pd
import numpy as np
import datetime
from prophet import Prophet

st.set_page_config(page_title = "Crime Forecast", page_icon = "📈")

# read csv files and create dataframe
@st.cache
def fetch_and_clean_data():
    df = pd.read_csv("Data/NYPD_Complaint_Folium.csv")
    df["start_date_of_event"] = pd.to_datetime(df["start_date_of_event"])
    return df

# a function that returns only a subset of the dataframe based on user input
def slice_df(boro, age, race, sex):
    df = crime[(crime["boro"] == boro) & (crime["victim_age"] == age) & (crime["victim_race"] == race) & 
               (crime["victim_sex"] == sex)].copy()
    return df

crime = fetch_and_clean_data()
# top_crime = pd.DataFrame(crime["description"].value_counts())
# top_crime.columns = ["count"]

# Streamlit app elements
# user input on the sidebar
boro = st.sidebar.selectbox("Select borough", ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"])
age = st.sidebar.selectbox("Select age", ["<18", "18-24", "25-44", "45-64", "65+"])
race = st.sidebar.selectbox("Select race", ["White Hispanic", "Black", "Black Hispanic", "White", 
                                            "Asian/Pacific Islander", "American Indian/Alaskan Native"])
sex = st.sidebar.selectbox("Select sex", ["M", "F"])
input_date = st.sidebar.date_input("Select date", min_value = datetime.date(2006, 1, 1), max_value = datetime.date(2023, 12, 31))
date = pd.to_datetime(input_date)

# retrieve only a subset of the dataframe based on user input and preprocess it for forecasting
crime_sliced = slice_df(boro, age, race, sex)
crime_daily = crime_sliced.groupby(["start_date_of_event"]).agg({"id":"count"}).reset_index()
crime_daily.columns = ["ds", "y"]

# monthly
crime_monthly = crime_sliced.groupby(["year", "month"]).agg({"id":"count"}).reset_index()
crime_monthly["year"] = crime_monthly["year"].astype("str")
crime_monthly["month"] = crime_monthly["month"].astype("str")
crime_monthly["ds"] = pd.DatetimeIndex(crime_monthly["year"] + "-" + crime_monthly["month"])
crime_monthly.drop(columns = ["year", "month"], inplace = True)
crime_monthly.columns = ["y", "ds"]

# facebook prophet daily forecasting
model = Prophet(interval_width = 0.9)
trained = model.fit(crime_daily)
future = model.make_future_dataframe(periods = 730, freq = "D")
forecast = model.predict(future)

# facebook prophet monthly forecasting
model_month = Prophet(interval_width = 0.9)
trained_month = model_month.fit(crime_monthly)
future_month = model_month.make_future_dataframe(periods = 24, freq = "M")
forecast_month = model_month.predict(future_month)
plot_month = model_month.plot(forecast_month, xlabel = "Year", ylabel = "No of crimes")

if date <= datetime.date(2021, 12, 31):
    try:
        hist_result = crime_daily[crime_daily["ds"] == date]["y"].values[0]
        if hist_result == 1:
            st.markdown("## There was 1 crime reported on that day against an individual with the selected demographics")
        else:
            st.markdown("## There were {} crimes reported on that day against individuals with the selected demographics".format(hist_result))
    except:
        st.markdown("## There were no crimes reported on that day")
else:
    result = forecast[forecast["ds"] == date]["yhat_upper"].values[0]
    result = round(result, 2)
    st.markdown("## With a 90% confidence interval, our model forecasts a total between 0 and {} crimes on {} in {} against individuals with the selected demographics".format(result, input_date, boro))
    
st.markdown("### Historical and projected monthly crime plot")
st.pyplot(plot_month)
