import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(page_title = "Historical Crime Map", page_icon = "🗺️")

# # read csv files and create dataframe
@st.cache(allow_output_mutation = True)
def fetch_data():
    df = pd.read_csv("Data/NYPD_Complaint_Folium.csv")
    df["start_date_of_event"] = pd.to_datetime(df["start_date_of_event"]) 
    return df

# a function that returns only a subset of the dataframe based on user input
def slice_df(year, month):
    df = crime[(crime["year"] == year) & (crime["month"] == month)]
    return df

crime = fetch_data()

# user input on the sidebar
year = st.sidebar.slider("Select year", min_value = 2006, max_value = 2021)
month = st.sidebar.slider("Select month", min_value = 1, max_value = 12)

crime_sliced = slice_df(year, month)

# create folium map with the user inputs
locations = list(zip(crime_sliced["lat"], crime_sliced["lon"]))
base_map = folium.Map(location = [40.730610, -73.935242], tiles = "cartodbpositron", zoom_start = 11)
heatmap = HeatMap(locations, radius = 10, blur = 2).add_to(base_map)
cluster = MarkerCluster().add_to(base_map)
for row in crime_sliced.iterrows():
    folium.Marker([row[1].lat, row[1].lon]).add_to(cluster)

# display elements on streamlit
st.markdown("### Historical Crime Heatmap of NYC")
st_data = st_folium(base_map, width = 725)

