import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import plotly.express as px
import sys

forecast_file = sys.argv[1]

# WMO weather code to emoji mapping
WEATHER_EMOJI = {
    0: "☀️",   # Clear sky
    1: "🌤️",  # Mainly clear
    2: "⛅",   # Partly cloudy
    3: "☁️",   # Overcast
    45: "🌫️",  # Fog
    48: "🌫️",  # Depositing rime fog
    51: "🌦️",  # Drizzle: light
    53: "🌦️",  # Drizzle: moderate
    55: "🌦️",  # Drizzle: dense
    61: "🌧️",  # Rain: slight
    63: "🌧️",  # Rain: moderate
    65: "🌧️",  # Rain: heavy
    80: "🌦️",  # Rain showers: slight
    81: "🌦️",  # Rain showers: moderate
    82: "🌦️",  # Rain showers: violent
    # Add more codes as needed
}


def get_owm_icon_url(wmo_code):
    WMO_OWM_ICON_MAP = {
        0: "01d", 1: "02d", 2: "03d", 3: "04d", 45: "50d", 48: "50d",
        51: "09d", 53: "09d", 55: "09d", 56: "13d", 57: "13d",
        61: "10d", 63: "10d", 65: "10d", 66: "13d", 67: "13d",
        71: "13d", 73: "13d", 75: "13d", 77: "13d",
        80: "09d", 81: "09d", 82: "09d", 85: "13d", 86: "13d",
        95: "11d", 96: "11d", 99: "11d"
    }
    icon_code = WMO_OWM_ICON_MAP.get(wmo_code, "01d")
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"


# Load the JSON data
with open(forecast_file, "r") as f:
    data = json.load(f)

# Build DataFrame
dataframe = {
    "Date": data["daily"]["time"],
    "Max Temperature (°F)": data['daily']['temperature_2m_max'],
    "Min Temperature (°F)": data['daily']['temperature_2m_min'],
    "Precipitation Probability (%)": data['daily']['precipitation_probability_max'],
    "Weather Code": data['daily']['weather_code']
}
df = pd.DataFrame(dataframe)
# Location info
latitude = data['latitude']
longitude = data['longitude']
elevation = data['elevation']


API_KEY = "${OWM_KEY}"  # Replace with your actual API key
CENTER = [latitude, longitude]  # Florida center
ZOOM = 10

# --- Layer Options ---
layer_options = {
    "Precipitation": f"https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}",
    "Clouds": f"https://tile.openweathermap.org/map/clouds_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}",
    "Temperature": f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}"
}

# Map weather codes to emojis
df["Weather Emoji"] = df["Weather Code"].map(lambda x: WEATHER_EMOJI.get(x, "❓"))



# --- Create Map ---
m = folium.Map(location=CENTER, zoom_start=ZOOM)

st.title(f"Current Weather Map for Your Location")
selected_layer = st.selectbox("Choose a weather layer:", list(layer_options.keys()))
# Add selected tile layer
folium.TileLayer(
    tiles=layer_options[selected_layer],
    attr="OpenWeatherMap",
    name=selected_layer,
    overlay=True,
    control=True
).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# --- Display Map ---
st_folium(m, width=700, height=500)


# Location and forecast period
st.markdown(f"**Location:** Latitude {latitude}, Longitude {longitude}, Elevation {elevation} m")
st.markdown(f"**Forecast Period:** {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")

# Map view
st.subheader("7 Day Forecast")
#st.map(pd.DataFrame({"lat": [latitude], "lon": [longitude]}))

# Weather emoji chart
# Build HTML table
table_html = "<table><tr>"
for date in df["Date"]:
    table_html += f"<th>{date}</th>"
table_html += "</tr><tr>"
for code in df["Weather Code"]:
    url = get_owm_icon_url(code)
    table_html += f'<td><img src="{url}"</td>'
table_html += "</tr></table>"
st.markdown(table_html, unsafe_allow_html=True)
#calendar = pd.DataFrame([df["Weather Emoji"].values], columns=df["Date"].values)
#st.table(calendar)

# Temperature chart
fig_temp = px.line(df, x="Date", y=["Max Temperature (°F)", "Min Temperature (°F)"],
                   title="Daily Max and Min Temperatures")
st.plotly_chart(fig_temp)

# Precipitation chart
fig_precip = px.bar(df, x="Date", y="Precipitation Probability (%)",
                    title="Daily Precipitation Probability")
st.plotly_chart(fig_precip)



