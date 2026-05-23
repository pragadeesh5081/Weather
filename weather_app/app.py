import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

api_key = "f0f5d69f1377a16db4ba70ead7859006"

st.set_page_config(page_title="Weather App", page_icon="🌦", layout="wide")

def get_bg_color(description):
    desc = description.lower()
    if "clear" in desc:
        return "linear-gradient(135deg, #f97316, #fb923c)"
    elif "rain" in desc:
        return "linear-gradient(135deg, #1e3a5f, #2563eb)"
    elif "cloud" in desc:
        return "linear-gradient(135deg, #1e1e3f, #4a4a8a)"
    elif "storm" in desc or "thunder" in desc:
        return "linear-gradient(135deg, #1a1a2e, #2d1b69)"
    elif "snow" in desc:
        return "linear-gradient(135deg, #e0f2fe, #7dd3fc)"
    elif "mist" in desc or "fog" in desc:
        return "linear-gradient(135deg, #374151, #6b7280)"
    else:
        return "linear-gradient(135deg, #1e1e3f, #2d2d6b)"

def get_auto_location():
    try:
        res = requests.get("http://ip-api.com/json/", timeout=5)
        data = res.json()
        if data["status"] == "success":
            return data["city"]
    except:
        pass
    return None

st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .weather-card {
        border-radius: 20px;
        padding: 30px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    }
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 15px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #2d2d6b;
    }
    .hour-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #2d2d6b;
        min-width: 80px;
    }
    .section-title {
        color: #a78bfa;
        font-size: 20px;
        font-weight: bold;
        margin: 25px 0 10px 0;
    }
    .updated-time {
        color: #475569;
        font-size: 12px;
        text-align: center;
        margin-top: 5px;
    }
    .day-header {
        color: #a78bfa;
        font-size: 16px;
        font-weight: bold;
        margin: 15px 0 8px 0;
        padding: 8px 12px;
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 10px;
        border-left: 3px solid #a78bfa;
    }
    div[data-testid="stTextInput"] input {
        background-color: #1e1e3f;
        color: white;
        border-radius: 12px;
        border: 1px solid #4a4a8a;
        font-size: 16px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#a78bfa; font-size:40px;'>🌦 Weather App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b; margin-bottom:20px;'>Real-time weather with 3-hour interval forecast</p>", unsafe_allow_html=True)

# --- Stage 1: °C / °F toggle ---
unit = st.radio("", ["🌡 Celsius (°C)", "🌡 Fahrenheit (°F)"], horizontal=True)
api_unit = "metric" if "Celsius" in unit else "imperial"
unit_symbol = "°C" if "Celsius" in unit else "°F"

# --- Stage 2: Search history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Stage 4: Auto-detect location ---
if "auto_city" not in st.session_state:
    detected = get_auto_location()
    st.session_state.auto_city = detected if detected else ""

city = st.text_input("City", placeholder="🔍 Search city... e.g. Erode, Chennai, London",
                     value=st.session_state.auto_city, label_visibility="collapsed")

# Show recent searches
if st.session_state.history:
    st.markdown("<div style='color:#64748b; font-size:13px; margin-bottom:6px;'>🕐 Recent searches:</div>", unsafe_allow_html=True)
    hist_cols = st.columns(len(st.session_state.history))
    for i, hcol in enumerate(hist_cols):
        with hcol:
            if st.button(st.session_state.history[i], key=f"hist_{i}"):
                city = st.session_state.history[i]

if city:
    # Save to history
    if city not in st.session_state.history:
        st.session_state.history.insert(0, city)
        st.session_state.history = st.session_state.history[:5]  # keep last 5

    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={api_unit}"
    response = requests.get(url)
    data = response.json()

    if data["cod"] == "200":
        forecast = data["list"][0]
        city_name = data["city"]["name"]
        country = data["city"]["country"]
        temp = round(forecast["main"]["temp"], 1)
        feels_like = round(forecast["main"]["feels_like"], 1)
        weather_desc = forecast["weather"][0]["description"].title()
        humidity = forecast["main"]["humidity"]
        wind = forecast["wind"]["speed"]
        pressure = forecast["main"]["pressure"]
        rain = round(forecast.get("pop", 0) * 100, 1)
        sunrise = datetime.fromtimestamp(data["city"]["sunrise"]).strftime("%I:%M %p")
        sunset = datetime.fromtimestamp(data["city"]["sunset"]).strftime("%I:%M %p")
        updated = datetime.now().strftime("%d %b %Y, %I:%M %p")

        # --- Stage 3: Rain Alert ---
        today_dt = datetime.strptime(data["list"][0]["dt_txt"], "%Y-%m-%d %H:%M:%S").date()
        rain_alerts = []
        for item in data["list"]:
            item_dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
            if item_dt.date() == today_dt:
                pop = item.get("pop", 0) * 100
                if pop >= 50:
                    rain_alerts.append((item_dt.strftime("%I %p"), round(pop, 1)))

        if rain_alerts:
            alert_times = ", ".join([f"{t} ({p}%)" for t, p in rain_alerts])
            max_rain = max([p for _, p in rain_alerts])
            alert_color = "#7f1d1d" if max_rain >= 70 else "#713f12"
            alert_text_color = "#fca5a5" if max_rain >= 70 else "#fde68a"
            alert_icon = "🔴" if max_rain >= 70 else "🟡"
            st.markdown(f"""
            <div style='background:{alert_color}; border-radius:15px; padding:15px 20px; margin-bottom:15px; border:1px solid {alert_text_color};'>
                <div style='color:{alert_text_color}; font-size:16px; font-weight:bold;'>{alert_icon} Rain Alert! Rain expected at: {alert_times}</div>
                <div style='color:{alert_text_color}; font-size:13px; margin-top:5px;'>🌂 Carry an umbrella today!</div>
            </div>
            """, unsafe_allow_html=True)

        bg = get_bg_color(weather_desc)

        st.markdown(f"""
        <div class='weather-card' style='background: {bg};'>
            <div style='font-size:28px; font-weight:bold; color:#ffffff; margin-bottom:5px;'>📍 {city_name}, {country}</div>
            <div style='font-size:72px; font-weight:bold; color:#ffffff; line-height:1;'>{temp}{unit_symbol}</div>
            <div style='color:rgba(255,255,255,0.8); font-size:20px; margin-top:8px;'>{weather_desc}</div>
            <div style='color:rgba(255,255,255,0.6); font-size:14px; margin-top:4px;'>
                Feels like {feels_like}{unit_symbol}
            </div>
        </div>
        <div class='updated-time'>🕐 Last updated: {updated}</div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-title'>📊 Current Stats</div>", unsafe_allow_html=True)

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        stats = [
            ("💧", "Humidity", f"{humidity}%"),
            ("💨", "Wind", f"{wind} m/s"),
            ("🌧", "Rain", f"{rain}%"),
            ("🔵", "Pressure", f"{pressure} hPa"),
            ("🌅", "Sunrise", sunrise),
            ("🌇", "Sunset", sunset),
        ]
        for col, (icon, label, value) in zip([col1, col2, col3, col4, col5, col6], stats):
            with col:
                st.markdown(f"""
                <div class='stat-card'>
                    <div style='font-size:22px;'>{icon}</div>
                    <div style='color:#94a3b8; font-size:13px; margin-bottom:5px;'>{label}</div>
                    <div style='color:#ffffff; font-size:16px; font-weight:bold;'>{value}</div>
                </div>""", unsafe_allow_html=True)

        all_times = []
        all_temps = []
        all_feels = []
        all_rain = []
        all_humidity = []
        all_wind = []
        all_desc = []

        for item in data["list"]:
            dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
            all_times.append(dt)
            all_temps.append(round(item["main"]["temp"], 1))
            all_feels.append(round(item["main"]["feels_like"], 1))
            all_rain.append(round(item.get("pop", 0) * 100, 1))
            all_humidity.append(item["main"]["humidity"])
            all_wind.append(item["wind"]["speed"])
            all_desc.append(item["weather"][0]["description"].title())

        st.markdown("<div class='section-title'>🕐 Today's 3-Hour Forecast</div>", unsafe_allow_html=True)

        today = all_times[0].date()
        today_slots = [(t, tmp, r, desc) for t, tmp, r, desc in zip(all_times, all_temps, all_rain, all_desc) if t.date() == today]

        cols = st.columns(len(today_slots))
        for col, (t, tmp, r, desc) in zip(cols, today_slots):
            with col:
                st.markdown(f"""
                <div class='hour-card'>
                    <div style='color:#94a3b8; font-size:11px;'>{t.strftime("%I %p")}</div>
                    <div style='color:#ffffff; font-size:16px; font-weight:bold; margin:4px 0;'>{tmp}{unit_symbol}</div>
                    <div style='color:#a78bfa; font-size:10px;'>{desc[:20]}</div>
                    <div style='color:#3b82f6; font-size:11px;'>🌧 {r}%</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>📅 5-Day 3-Hour Interval View</div>", unsafe_allow_html=True)

        df_full = pd.DataFrame({
            "DateTime": all_times,
            "Date": [t.strftime("%a %d %b") for t in all_times],
            "Time": [t.strftime("%I %p") for t in all_times],
            "Temp": all_temps,
            "Feels Like": all_feels,
            "Rain (%)": all_rain,
            "Humidity (%)": all_humidity,
            "Wind (m/s)": all_wind,
            "Condition": all_desc
        })

        days = df_full["Date"].unique()
        for day in days[1:]:
            day_df = df_full[df_full["Date"] == day]
            st.markdown(f"<div class='day-header'>📆 {day}</div>", unsafe_allow_html=True)
            slot_cols = st.columns(len(day_df))
            for col, (_, row) in zip(slot_cols, day_df.iterrows()):
                with col:
                    st.markdown(f"""
                    <div class='hour-card'>
                        <div style='color:#94a3b8; font-size:11px;'>{row["Time"]}</div>
                        <div style='color:#ffffff; font-size:15px; font-weight:bold; margin:4px 0;'>{row["Temp"]}{unit_symbol}</div>
                        <div style='color:#a78bfa; font-size:10px;'>{row["Condition"][:20]}</div>
                        <div style='color:#3b82f6; font-size:11px;'>🌧 {row["Rain (%)"]}%</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>📈 Temperature Trend (5 Days)</div>", unsafe_allow_html=True)

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=all_times, y=all_temps, mode="lines+markers", name=f"Actual Temp ({unit_symbol})", line=dict(color="#a78bfa", width=2), marker=dict(size=5)))
        fig1.add_trace(go.Scatter(x=all_times, y=all_feels, mode="lines+markers", name=f"Feels Like ({unit_symbol})", line=dict(color="#fb923c", width=2, dash="dot"), marker=dict(size=5)))
        fig1.update_layout(paper_bgcolor="#0f0f1a", plot_bgcolor="#1a1a2e", font_color="white", title_font_color="#a78bfa", legend=dict(bgcolor="#1a1a2e"), hovermode="x unified")
        fig1.update_xaxes(gridcolor="#2d2d6b")
        fig1.update_yaxes(gridcolor="#2d2d6b")
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("<div class='section-title'>🌧 Rain Chance (5 Days)</div>", unsafe_allow_html=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=all_times, y=all_rain, name="Rain %", marker_color="#3b82f6"))
        fig2.update_layout(paper_bgcolor="#0f0f1a", plot_bgcolor="#1a1a2e", font_color="white", title_font_color="#a78bfa", hovermode="x unified")
        fig2.update_xaxes(gridcolor="#2d2d6b")
        fig2.update_yaxes(gridcolor="#2d2d6b", range=[0, 100])
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='section-title'>📊 Humidity & Wind (5 Days)</div>", unsafe_allow_html=True)

        col_h, col_w = st.columns(2)

        with col_h:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=all_times, y=all_humidity, mode="lines+markers", name="Humidity", line=dict(color="#06b6d4", width=2), fill="tozeroy", fillcolor="rgba(6,182,212,0.1)"))
            fig3.update_layout(title="Humidity (%)", paper_bgcolor="#0f0f1a", plot_bgcolor="#1a1a2e", font_color="white", title_font_color="#a78bfa")
            fig3.update_xaxes(gridcolor="#2d2d6b")
            fig3.update_yaxes(gridcolor="#2d2d6b")
            st.plotly_chart(fig3, use_container_width=True)

        with col_w:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=all_times, y=all_wind, mode="lines+markers", name="Wind Speed", line=dict(color="#8b5cf6", width=2), fill="tozeroy", fillcolor="rgba(139,92,246,0.1)"))
            fig4.update_layout(title="Wind Speed (m/s)", paper_bgcolor="#0f0f1a", plot_bgcolor="#1a1a2e", font_color="white", title_font_color="#a78bfa")
            fig4.update_xaxes(gridcolor="#2d2d6b")
            fig4.update_yaxes(gridcolor="#2d2d6b")
            st.plotly_chart(fig4, use_container_width=True)

    else:
        st.markdown("""
        <div style='background:#2d1515; border-radius:15px; padding:20px; text-align:center; border:1px solid #7f1d1d;'>
            <div style='font-size:40px;'>❌</div>
            <div style='color:#fca5a5; font-size:18px; margin-top:10px;'>City not found! Please check the spelling.</div>
        </div>
        """, unsafe_allow_html=True)