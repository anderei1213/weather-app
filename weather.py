import streamlit as st
import requests
from datetime import datetime
import time

# 1. API SETTINGS
API_KEY = "39a81eaad8f4d90734462eed7dfc5413"

# 2. MOBILE DESIGNER
def apply_mobile_design(weather_main, is_day):
    if is_day:
        if "Clear" in weather_main:
            bg = "linear-gradient(to bottom, #4facfe, #00f2fe)"
        elif "Rain" in weather_main or "Thunderstorm" in weather_main:
            bg = "linear-gradient(to bottom, #203a43, #2c5364)"
        else:
            bg = "linear-gradient(to bottom, #757f9a, #d7dde8)"
    else:
        bg = "linear-gradient(to bottom, #0f2027, #203a43, #2c5364)"

    st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; color: white; transition: 0.5s; }}
    
    /* Mobile Glass Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
    }}

    /* Forecast Row Styling */
    .forecast-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# 3. DATA LOGIC (Current + 7 Day Forecast)
def get_full_weather(city):
    try:
        # Current Weather
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        curr_data = requests.get(curr_url).json()
        
        # 5-Day / 3-Hour Forecast (API limitation: Free tier provides 5 days)
        fore_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        fore_data = requests.get(fore_url).json()
        
        forecast_list = []
        total_rain_24h = 0
        
        if fore_data.get("cod") == "200":
            # Calculate 24h rain
            for i in range(8):
                total_rain_24h += fore_data['list'][i].get('rain', {}).get('3h', 0)
            
            # Extract daily data (taking 12:00 PM slot for each day)
            for item in fore_data['list']:
                if "12:00:00" in item['dt_txt']:
                    date_obj = datetime.fromtimestamp(item['dt'])
                    forecast_list.append({
                        "day": date_obj.strftime("%A"),
                        "temp": round(item['main']['temp']),
                        "icon": item['weather'][0]['icon'],
                        "desc": item['weather'][0]['main']
                    })
                    
        return curr_data, total_rain_24h, forecast_list
    except:
        return None, 0, []

# 4. MAIN APP
def main():
    city_name = st.text_input("📍 Search City", value="Guinhawa, Malolos")
    data, total_rain, forecast = get_full_weather(city_name)
    
    if data and data.get("cod") == 200:
        current_time = time.time()
        is_day = data['sys']['sunrise'] < current_time < data['sys']['sunset']
        apply_mobile_design(data['weather'][0]['main'], is_day)
        
        # --- CURRENT WEATHER CARD ---
        with st.container(border=True):
            st.write(f"**{data['name']}** | {datetime.now().strftime('%b %d')}")
            col_t1, col_t2 = st.columns([1, 1])
            with col_t1:
                st.markdown(f"<h1 style='margin:0;'>{round(data['main']['temp'])}°C</h1>", unsafe_allow_html=True)
            with col_t2:
                st.image(f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png", width=70)
            st.write(f"💧 {data['main']['humidity']}% | 💨 {round(data['wind']['speed'] * 3.6)} km/h")

        # --- ADVISORIES ---
        st.subheader("📢 Alerts")
        with st.container(border=True):
            # Rainfall
            if total_rain >= 30: st.error(f"🌧️ Rain: {total_rain}mm (RED)")
            else: st.write(f"🌧️ Rain: {total_rain}mm (Normal)")
            
            # Heat
            temp = data['main']['temp']
            if temp >= 33: st.warning(f"🌡️ Heat: {round(temp)}°C (High)")
            else: st.write(f"🌡️ Heat: {round(temp)}°C (Safe)")

        # --- 1-WEEK FORECAST (Vertical List for Mobile) ---
        st.subheader("🗓️ Next 5 Days")
        with st.container(border=True):
            for day in forecast:
                # Custom HTML row for a clean mobile list look
                st.markdown(f"""
                <div class="forecast-row">
                    <div style="flex: 1; font-weight: bold;">{day['day'][:3]}</div>
                    <div style="flex: 1; text-align: center;">
                        <img src="http://openweathermap.org/img/wn/{day['icon']}.png" width="30">
                    </div>
                    <div style="flex: 1; text-align: right;">{day['temp']}°C</div>
                </div>
                """, unsafe_allow_html=True)

    elif city_name:
        st.error("City not found!")

if __name__ == "__main__":
    main()
