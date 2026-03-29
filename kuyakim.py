import streamlit as st
import requests

API_KEY = "39a81eaad8f4d90734462eed7dfc5413"

# ================= CURRENT WEATHER =================
def find_current_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    try:
        weather = data['weather'][0]['main']
        icon_id = data['weather'][0]['icon']
        temp = round(data['main']['temp'])
        humidity = data['main']['humidity']

        # 🌧️ Rain (mm)
        rain = data.get('rain', {}).get('1h', 0)

        # 🌪️ Wind speed (convert m/s → km/h)
        wind_speed = data['wind']['speed'] * 3.6

        icon = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
    except:
        st.error("City not found")
        st.stop()

    return weather, temp, humidity, rain, wind_speed, icon


# ================= HEAT =================
def heat_index_classification(temp):
    if temp >= 52:
        return "🔥 Extreme Danger", "Heat stroke likely!"
    elif temp >= 42:
        return "⚠️ Danger", "Heat cramps & exhaustion likely"
    elif temp >= 33:
        return "⚡ Extreme Caution", "Possible heat exhaustion"
    elif temp >= 27:
        return "☀️ Caution", "Fatigue possible"
    else:
        return "✅ Normal", "Safe conditions"


# ================= RAIN (PAGASA STYLE) =================
def rainfall_classification(rain):
    if rain >= 30:
        return "🔴 RED WARNING", "Serious flooding expected — suspend classes!"
    elif rain >= 15:
        return "🟠 ORANGE WARNING", "Flooding threatening"
    elif rain >= 7.5:
        return "🟡 YELLOW WARNING", "Flooding possible"
    else:
        return "☀️ No Warning", "Normal conditions"


# ================= FORECAST =================
def get_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    forecast_list = []

    try:
        for i in range(0, len(data['list']), 8):
            day = data['list'][i]
            temp = round(day['main']['temp'])
            weather = day['weather'][0]['main']
            icon = f"http://openweathermap.org/img/wn/{day['weather'][0]['icon']}@2x.png"

            forecast_list.append((temp, weather, icon))
    except:
        return []

    return forecast_list


# ================= MAIN =================
def main():
    st.title("🌤️ Weather + Heat, Rain & Typhoon Monitor")

    city_input = st.text_input("Enter City", key="city_input")

    if st.button("Check Weather", key="check_btn"):

        if not city_input:
            st.warning("Please enter a city")
            return

        city = city_input.lower()

        weather, temp, humidity, rain, wind, icon = find_current_weather(city)

        st.subheader("Current Weather")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Temperature", f"{temp}°C")
            st.metric("Humidity", f"{humidity}%")
            st.metric("Rain (1h)", f"{rain} mm")
            st.metric("Wind", f"{round(wind)} km/h")

        with col2:
            st.write(weather)
            st.image(icon)

        # 🔥 HEAT
        heat_lvl, heat_msg = heat_index_classification(temp)
        st.subheader("🔥 Heat Index")
        st.warning(f"{heat_lvl} — {heat_msg}")

        if temp >= 40:
            st.error("🚨 TEMP WARNING: ≥40°C — Suspend classes!")

        # 🌧️ RAIN
        rain_lvl, rain_msg = rainfall_classification(rain)
        st.subheader("🌧️ Rain Warning")
        st.info(f"{rain_lvl} — {rain_msg}")

        if rain >= 30:
            st.error("🚨 RAIN WARNING: Heavy rainfall — Suspend classes!")

        if wind >= 121:
            st.error("🚨 TYPHOON WARNING: Signal #3+ — Suspend classes!")

        # 📅 FORECAST
        st.subheader("📅 5-Day Forecast")
        forecast = get_forecast(city)

        if forecast:
            cols = st.columns(len(forecast))
            for i, (f_temp, f_weather, f_icon) in enumerate(forecast):
                with cols[i]:
                    st.image(f_icon)
                    st.write(f"{f_temp}°C")
                    st.write(f_weather)


# RUN
main()