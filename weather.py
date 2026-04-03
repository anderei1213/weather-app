import streamlit as st
import requests
from datetime import datetime
import time

# 1. API SETTINGS
API_KEY = "39a81eaad8f4d90734462eed7dfc5413"
st.title("Weather Advisory Web App")
# 2. MOBILE-FIRST DESIGNER
def apply_mobile_design(weather_main, is_day):
    # Background Logic
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
    /* Force mobile-friendly background */
    .stApp {{ 
        background: {bg}; 
        color: white; 
        transition: 0.5s;
    }}
    
    /* Make containers look like sleek mobile cards */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
    }}

    /* Adjust font sizes for mobile screens */
    h1 {{ font-size: 2.2rem !important; }}
    h2 {{ font-size: 1.8rem !important; }}
    h3 {{ font-size: 1.4rem !important; }}
    p {{ font-size: 1rem !important; }}

    /* Hide Streamlit header/footer for 'App' feel */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# 3. DATA LOGIC
def get_weather_data(city):
    try:
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
    except:
        return None, 0

# 4. MAIN APP
def main():
    # Search bar at the very top
    city_name = st.text_input("Search City", value="Malolos")
    
    data, total_rain = get_weather_data(city_name)
    
    if data and data.get("cod") == 200:
        # Day/Night Check
        current_time = time.time()
        is_day = data['sys']['sunrise'] < current_time < data['sys']['sunset']
        
        apply_mobile_design(data['weather'][0]['main'], is_day)
        
        # --- CARD 1: MAIN WEATHER ---
        with st.container(border=True):
            # On mobile, we stack these or use small columns
            st.markdown(f"**{data['name']}**")
            st.write(datetime.now().strftime('%A, %B %d'))
            
            # Big Temp and Icon side-by-side
            col_t1, col_t2 = st.columns([1, 1])
            with col_t1:
                st.markdown(f"<h1 style='margin:0;'>{round(data['main']['temp'])}°C</h1>", unsafe_allow_html=True)
            with col_t2:
                icon_code = data['weather'][0]['icon']
                st.image(f"http://openweathermap.org/img/wn/{icon_code}@2x.png", width=80)
            
            st.write(f"💧 {data['main']['humidity']}% | 💨 {round(data['wind']['speed'] * 3.6)} km/h")

        # --- CARD 2: RAINFALL ---
        with st.container(border=True):
            st.markdown(f"### 🌧️ 24h Rainfall")
            st.markdown(f"**{total_rain} mm**")
            if total_rain >= 30:
                st.error("🔴 RED: Suspend Classes")
            elif total_rain >= 15:
                st.warning("🟠 ORANGE: Flooding Threat")
            else:
                st.write("✅ Rainfall is normal")

        # --- CARD 3: HEAT INDEX ---
        with st.container(border=True):
            temp = data['main']['temp']
            st.markdown(f"### 🌡️ Heat Index")
            st.markdown(f"**{round(temp)}°C**")
            if temp >= 42:
                st.error("🔥 Extreme Danger")
            elif temp >= 33:
                st.warning("⚠️ High Heat")
            else:
                st.write("✅ Temperature safe")

    else:
        st.error("City not found. Try again!")

if __name__ == "__main__":
    main()
