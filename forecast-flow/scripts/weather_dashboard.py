import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import plotly.express as px
import sys

forecast_file = sys.argv[1]


WEATHER_EMOJI = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌧️", 53: "🌧️", 55: "🌧️",
    56: "🌨️", 57: "🌨️",
    61: "🌦️", 63: "🌧️", 65: "🌧️",
    66: "🌨️", 67: "🌨️",
    71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
    80: "🌧️", 81: "🌧️", 82: "🌧️",
    85: "❄️", 86: "❄️",
    95: "⛈️", 96: "⛈️", 99: "⛈️"
}

# WMO code → human-readable condition text
WMO_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    56: "Light freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}

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

# Original code block for 7 day
#==============================
# Build HTML table
table_html = "<table><tr>"
for date in df["Date"]:
    table_html += f"<th>{date}</th>"
table_html += "</tr><tr>"
for code in df["Weather Code"]:
    url = get_owm_icon_url(code)
    table_html += f'<td><img src="{url}"</td>'
table_html += "</tr></table>"
#st.markdown(table_html, unsafe_allow_html=True)
#=================================


def build_7day_forecast_table_flipped(df: pd.DataFrame) -> str:
    """
    Simple flipped table: Day | Emoji | Condition | High/Low | Precip
    """
    # Sort by date
    df_sorted = df.copy()
    df_sorted["__dt__"] = pd.to_datetime(df_sorted["Date"], errors="coerce")
    df_sorted = df_sorted.sort_values("__dt__").drop(columns="__dt__")

    # Labels
    dt = pd.to_datetime(df_sorted["Date"], errors="coerce")
    weekdays = dt.dt.strftime("%a").fillna(df_sorted["Date"])
    dates    = dt.dt.strftime("%b %d").fillna("")

    # Build HTML
    html = """
<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
<thead>
<tr style="background-color: #f8f9fa; font-weight: bold;">
  <th style="text-align:left; padding:8px;">Day</th>
  <th style="text-align:left; padding:8px;">Emoji</th>
  <th style="text-align:left; padding:8px;">Condition</th>
  <th style="text-align:left; padding:8px;">High / Low (°F)</th>
  <th style="text-align:left; padding:8px;">Precip (%)</th>
</tr>
</thead>
<tbody>
"""
    for w, d, code, hi, lo, p in zip(
        weekdays, dates,
        df_sorted["Weather Code"],
        df_sorted["Max Temperature (°F)"],
        df_sorted["Min Temperature (°F)"],
        df_sorted["Precipitation Probability (%)"]
    ):
        c = int(code) if pd.notna(code) else None
        emoji = WEATHER_EMOJI.get(c, "❓")
        cond  = WMO_DESCRIPTIONS.get(c, "Unknown")
        hi_str = f"{round(hi)}°" if pd.notna(hi) else "—"
        lo_str = f"{round(lo)}°" if pd.notna(lo) else "—"
        p_str  = f"{int(round(p))}%" if pd.notna(p) else "—"

        html += f"""
<tr>
  <td style="padding:8px;">{w} · {d}</td>
  <td style="padding:8px;">{emoji}</td>
  <td style="padding:8px;">{cond}</td>
  <td style="padding:8px;">{hi_str} / {lo_str}</td>
  <td style="padding:8px;">{p_str}</td>
</tr>
"""
    html += "</tbody></table>"
    return html

html = build_7day_forecast_table_flipped(df)
with open("7day.html", 'w') as f:
    f.write(html)
st.html(html)

# Temperature chart
fig_temp = px.line(df, x="Date", y=["Max Temperature (°F)", "Min Temperature (°F)"],
                   title="Daily Max and Min Temperatures")
st.plotly_chart(fig_temp)

# Precipitation chart
fig_precip = px.bar(df, x="Date", y="Precipitation Probability (%)",
                    title="Daily Precipitation Probability")
st.plotly_chart(fig_precip)
