import streamlit as st

st.set_page_config(page_title = "Intro", page_icon = "👮")

st.title("NYC Historical Crime Data and Future Forecast")

st.markdown(
    """
    There are 3 pages within this app in addition to the intro.\n
    The first page shows a historical crime heatmap of New York City. Users can select a year and a month with the
    slider and see different clusters and hotspots.\n
    The second page shows the top categories of crimes. Users can select different boroughs and demographics and get
    a forecasted number of crimes targeting these individuals on a particular day and a projected monthly plot.\n
    The third page is a route recommender. Users can select from a list of locations and get the shortest or the 
    recommended route avoiding high crime areas.\n
    The dataset used is from [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/NYPD-Complaint-Data-Historic/qgea-i56i)
    """
)
