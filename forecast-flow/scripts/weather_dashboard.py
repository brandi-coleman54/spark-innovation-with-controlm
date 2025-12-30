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


import pandas as pd

def build_7day_forecast_table_flipped(df: pd.DataFrame) -> str:
    """
    Build an HTML table for a 7-day forecast with rows per day.
    Columns: Day (weekday + date), Condition (emoji), High/Low (°F), Precip (%).
    """
    # Validate required columns
    required_cols = [
        "Date", "Weather Code",
        "Max Temperature (°F)", "Min Temperature (°F)",
        "Precipitation Probability (%)"
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column in df: {col}")

    # Parse dates to get weekday + pretty date
    dates_parsed = pd.to_datetime(df["Date"], errors="coerce")
    weekday_labels = dates_parsed.dt.strftime("%a").fillna(df["Date"])
    date_labels = dates_parsed.dt.strftime("%b %d").fillna("")

    # CSS and table header
    html = """
    <style>
      .forecast-table {
          width: 100%;
          border-collapse: collapse;
          table-layout: fixed;
      }
      .forecast-table thead th {
          background: #f8f9fa;
          border-bottom: 2px solid #e6e6e6;
          font-weight: 700;
          text-align: left;
          padding: 10px;
          font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
          font-size: 0.95rem;
      }
      .forecast-table tbody td {
          border-bottom: 1px solid #ececec;
          padding: 10px;
          font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
          font-size: 0.95rem;
          vertical-align: middle;
      }
      .forecast-table tbody tr:nth-child(odd) {
          background: #fcfcfc;
      }
      .col-day { width: 36%; }
      .col-cond { width: 18%; }
      .col-temps { width: 26%; }
      .col-precip { width: 20%; }

      .day-cell .weekday {
          font-weight: 700;
          margin-right: 6px;
      }
      .day-cell .date {
          color: #666;
          font-size: 0.9rem;
      }

      .emoji {
          font-size: 1.35rem;
          line-height: 1;
      }

      .temps {
          white-space: nowrap;
          font-weight: 600;
      }
      .high { color: #d9534f; }  /* red-ish for highs */
      .low { color: #428bca; margin-left: 8px; } /* blue-ish for lows */

      .precip {
          color: #4a4a4a;
          font-size: 0.95rem;
      }
    </style>
    <table class="forecast-table">
      <thead>
        <tr>
          <th class="col-day">Day</th>
          <th class="col-cond">Condition</th>
          <th class="col-temps">High / Low (°F)</th>
          <th class="col-precip">Precip (%)</th>
        </tr>
      </thead>
      <tbody>
    """

    # Build body rows: one per day
    for weekday, date_txt, code, hi, lo, p in zip(
        weekday_labels,
        date_labels,
        df["Weather Code"],
        df["Max Temperature (°F)"],
        df["Min Temperature (°F)"],
        df["Precipitation Probability (%)"]
    ):
        # Emoji from WMO code
        try:
            emoji = WEATHER_EMOJI.get(int(code), "❓")
        except Exception:
            emoji = "❓"

        # Temperatures
        hi_str = f"{round(hi)}°" if pd.notna(hi) else "—"
        lo_str = f"{round(lo)}°" if pd.notna(lo) else "—"

        # Precip prob
        p_str = f"{int(round(p))}%" if pd.notna(p) else "—"

        html += f"""
        <tr>
          <td class="day-cell"><span class="weekday">{weekday}</span><span class="date">· {date_txt}</span></td>
          <td class="emoji">{emoji}</td>
          <td class="temps"><span class="high">{hi_str}</span><span class="low">{lo_str}</span></td>
          <td class="precip">{p_str}</td>
        </tr>
        """

    html += """
      </tbody>
    </table>
    """

    return html

html = build_7day_forecast_table_flipped(df)
with open("7day.html", 'w') as f:
    f.write(html)
st.markdown(html, unsafe_allow_html=True)

# Temperature chart
fig_temp = px.line(df, x="Date", y=["Max Temperature (°F)", "Min Temperature (°F)"],
                   title="Daily Max and Min Temperatures")
st.plotly_chart(fig_temp)

# Precipitation chart
fig_precip = px.bar(df, x="Date", y="Precipitation Probability (%)",
                    title="Daily Precipitation Probability")
st.plotly_chart(fig_precip)
