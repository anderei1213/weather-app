import streamlit as st
import requests
from datetime import datetime
import time

# 1. API SETTINGS
API_KEY = "39a81eaad8f4d90734462eed7dfc5413"

# 2. THE DESIGNER (Now handles Day, Night, and Stormy backgrounds)
def apply_design(weather_main, is_day):
    # Default Morning/Day Colors
    if is_day:
        if "Clear" in weather_main:
            bg = "linear-gradient(to bottom, #4facfe, #00f2fe)" # Bright Sunny Blue
        elif "Rain" in weather_main or "Thunderstorm" in weather_main:
            bg = "linear-gradient(to bottom, #203a43, #2c5364)" # Gloomy Rainy Day
        else:
            bg = "linear-gradient(to bottom, #757f9a, #d7dde8)" # Cloudy Grey
    
    # Night Colors (Dark Mode)
    else:
        bg = "linear-gradient(to bottom, #0f2027, #203a43, #2c5364)" # Deep Midnight Blue

    st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; color: white; transition: 1s; }}
    
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 20px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. WEATHER & RAINFALL DATA LOGIC
def get_weather_data(city):
    curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    curr_data = requests.get(curr_url).json()
    
    fore_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    fore_data = requests.get(fore_url).json()
    
    total_rain = 0
    if fore_data.get("cod") == "200":
        for i in range(8):
            rain = fore_data['list'][i].get('rain', {}).get('3h', 0)
            total_rain += rain
            
    return curr_data, total_rain

# 4. MAIN APP
def main():
    st.title("🌤️ My Weather App")
    
    city_name = st.text_input("Type a city name:", value="Manila")
    data, total_rain = get_weather_data(city_name)
    
    if data.get("cod") == 200:
        # Check if it is currently Day or Night in that city
        current_time = time.time()
        sunrise = data['sys']['sunrise']
        sunset = data['sys']['sunset']
        is_day = sunrise < current_time < sunset
        
        # Apply the Design
        apply_design(data['weather'][0]['main'], is_day)
        
        # --- DAY/NIGHT STATUS ---
        status_icon = "☀️ Morning" if is_day else "🌙 Night Time"
        st.write(f"Currently: **{status_icon}**")

        # --- BOX 1: CITY & TEMPERATURE ---
        with st.container(border=True): 
            col1, col2 = st.columns(2)
            with col1:
                st.header(data['name'])
                st.write(datetime.now().strftime('%A, %B %d'))
                st.write(f"💧 Humidity: {data['main']['humidity']}%")
                st.write(f"💨 Wind: {round(data['wind']['speed'] * 3.6)} km/h")
            with col2:
                st.markdown(f"<h1 style='text-align: right; font-size: 80px; font-weight: 200;'>+{round(data['main']['temp'])}°C</h1>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📢 Advisories")

        # --- BOX 2: RAINFALL ADVISORY ---
        with st.container(border=True):
            st.markdown(f"### 🌧️ 24h Rainfall: {total_rain} mm")
            if total_rain >= 30:
                st.error("🚨 RED WARNING: Serious flooding - Suspend classes!")
            elif total_rain >= 15:
                st.warning("🟠 ORANGE WARNING: Flooding is threatening.")
            elif total_rain >= 7.5:
                st.info("🟡 YELLOW WARNING: Flooding is possible.")
            else:
                st.markdown("✅ Rainfall is normal.")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- BOX 3: HEAT INDEX ADVISORY ---
        with st.container(border=True):
            temp = data['main']['temp']
            st.markdown(f"### 🌡️ Heat Index: {round(temp)}°C")
            if temp >= 42:
                st.error("🔥 Extreme Danger: Heat stroke likely! Suspend classes.")
            elif temp >= 33:
                st.warning("⚠️ Danger: Heat cramps and exhaustion likely.")
            else:
                st.markdown("✅ Temperature is normal.")

    else:
        st.error("City not found!")

if __name__ == "__main__":
    main()
