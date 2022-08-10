import streamlit as st
import pandas as pd
import numpy as np
import folium
import time
from openrouteservice import client
from shapely.geometry import LineString, mapping, Point
from shapely.ops import cascaded_union, unary_union
from streamlit_folium import st_folium, folium_static

st.set_page_config(page_title = "Route Recommendation", page_icon = "🚦")

# function for setting the display style on map
def style_function(color):
    return lambda feature: dict(color = color, opacity = 0.5, weight = 4)

crime_latlon = pd.read_csv("Data/NYPD_Complaint_Latlon.csv")

# create a list of lists with crime location latitude and longitude
crime_start = [list(x) for x in zip(crime_latlon["lon_rnd"], crime_latlon["lat_rnd"])]
crime_end = [list(x) for x in zip(crime_latlon["lon_end"], crime_latlon["lat_end"])]
crime_hotspot = [list(x) for x in list(zip(crime_start, crime_end))]

# basic parameters for the API call
api_key = "5b3ce3597851110001cf624828c58c7587b54329a3344bf85f2df83a"  
ors = client.Client(key = api_key)

base_map = folium.Map(location = [40.776676, -73.971321], tiles = "cartodbpositron", zoom_start = 12)

popup_route = "<h4>{0} route</h4><hr>" \
              "<strong>Duration: </strong>{1:.1f} mins<br>" \
              "<strong>Distance: </strong>{2:.3f} km"

# a dictionary of landmarks for users to choose from
landmarks = {"Flatiron Building": [-73.989723, 40.741112],
             "Grand Central Terminal": [-73.977295, 40.752655],
             "Chrysler Building": [-73.975311, 40.751652],
             "Empire State Building": [-73.985428, 40.748817],
             "Rockefeller Center": [-73.978798, 40.758678],
             "One World Trade Center": [-74.013382, 40.712742],
             "Madison Square Garden": [-73.993324, 40.750298],
             "McGraw Hill Building": [-73.991667, 40.757500],
             "Lincoln Center": [-73.984070, 40.772392],
             "The Metropolitan Museum of Art": [-73.963402, 40.779434],
             "The Guggenheim": [-73.958971, 40.782980],
             "Times Square": [-73.985130, 40.758896],
             "Penn Station": [-73.993584, 40.750580]} 

# dropdown menus on streamlit sidebar for users to select start and end point
landmark_list = list(landmarks.keys())
user_start = st.sidebar.selectbox("Origin", landmark_list)
user_end = st.sidebar.selectbox("Destination", landmark_list)

coordinates = [landmarks[user_start], landmarks[user_end]]

# route_option = st.sidebar.radio("", ("Shortest route", "Recommended route"))
# shortest = st.sidebar.button("Shortest route")
# recommended = st.sidebar.button("Recommended route")
clicked = st.sidebar.button("Calculate route")

# if shortest:

# Request route
if clicked:
    direction_params = {"coordinates": coordinates,
                        "profile": "foot-walking",
                        "format_out": "geojson",
                        "preference": "shortest",
                        "geometry": "true"}
    regular_route = ors.directions(**direction_params)
    # Build popup
    distance, duration = regular_route["features"][0]["properties"]["summary"].values()
    popup = folium.map.Popup(popup_route.format("Regular", duration / 60, distance / 1000))
    folium.GeoJson(regular_route, style_function = style_function("blue")).add_child(popup).add_to(base_map)
    folium.Marker(list(reversed(coordinates[0])), popup = "Origin").add_to(base_map)
    folium.Marker(list(reversed(coordinates[1])), popup = "Destination").add_to(base_map)

    # elif recommended:
    # Add markers for crime locations
    for crime in crime_start[0:51]:
        folium.Marker(list(reversed(crime)), icon = folium.Icon(color = "red"), popup = "Crime Site").add_to(base_map)
    buffer = []
    # Create avoidance zones
    for point in crime_hotspot[0:51]:
        avoid_params = {"coordinates": point,
                        "profile": "foot-walking",
                        "format_out": "geojson",
                        "preference": "shortest",
                        "geometry": "true"}
        avoid_request = ors.directions(**avoid_params)
        time.sleep(1)
        coords = avoid_request["features"][0]["geometry"]["coordinates"]
        # Create geometry buffer
        route_buffer = LineString(coords).buffer(0.001)
        # Simplify geometry for better handling
        simp_geom = route_buffer.simplify(0.005)  
        buffer.append(simp_geom)
    union_buffer = unary_union(buffer)
    # New routing with avoided crime hotspots
    avoid_crime = {"coordinates": coordinates,
                   "format_out": "geojson",
                   "profile": "foot-walking",
                   "preference": "shortest",
                   "instructions": False,
                   "options": {"avoid_polygons": mapping(union_buffer)}}
    route_crimefree = ors.directions(**avoid_crime)
    # Build popup
    distance, duration = route_crimefree["features"][0]["properties"]["summary"].values()
    popup = folium.map.Popup(popup_route.format("Crimefree Route", duration / 60, distance / 1000))
    folium.GeoJson(route_crimefree, style_function = style_function("green")).add_child(popup).add_to(base_map)
    folium.Marker(list(reversed(coordinates[0])), popup = "Origin").add_to(base_map)
    folium.Marker(list(reversed(coordinates[1])), popup = "Destination").add_to(base_map)
    base_map.add_child(folium.map.LayerControl())

# display the folium map on streamlit   
folium_static(base_map)














