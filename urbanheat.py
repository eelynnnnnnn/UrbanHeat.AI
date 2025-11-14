import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from folium import FeatureGroup, LayerControl
import folium.plugins as plugins
from datetime import datetime, timedelta
from geopy.distance import geodesic

st.set_page_config(layout="wide", page_title="UrbanHeat.AI")
st.sidebar.title("🌡 UrbanHeat.AI")

# Navigation
page = st.sidebar.radio("Navigate", [
    "1. Heat Risk Map",
    "2. Mobile Alerts",
    "3. Vulnerability Index",
    "4. Planner Dashboard"
])

st.title("🌆 UrbanHeat.AI — Smart Urban Heat Risk Platform")
st.markdown("""
An AI-powered urban heat response system using satellite data, socio-economic overlays,
and smart planning tools to improve urban resilience and climate adaptation.
""")

@st.cache_data
def get_mock_lst_data(day):
    data = []
    for _ in range(50):
        lat = np.random.uniform(3.13, 3.17)
        lon = np.random.uniform(101.68, 101.73)
        temp = np.random.uniform(30, 40)
        data.append((lat, lon, temp))
    return data

# Page 1: Heat Risk Map
if page == "1. Heat Risk Map":
    st.header("🔥 Heat Risk Map")
    time_options = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    selected_day = st.select_slider("Select Day for LST Visualization", options=time_options)
    lst_data = get_mock_lst_data(selected_day)

    map_heat = folium.Map(location=[3.15, 101.7], zoom_start=15, tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png", attr='OpenStreetMap')
    cluster = plugins.MarkerCluster().add_to(map_heat)

    for lat, lon, temp in lst_data:
        if temp <= 31:
            color = '#7FFFD4'
        elif temp <= 34:
            color = '#FFD700'
        elif temp <= 37:
            color = '#FF8C00'
        else:
            color = '#FF0000'

        radius = 4 + (temp - 30) / 2
        folium.CircleMarker(
            location=(lat, lon),
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            tooltip=f"{selected_day} — LST: {temp:.1f}°C"
        ).add_to(cluster)

    plugins.Fullscreen(position='topright').add_to(map_heat)
    LayerControl().add_to(map_heat)
    st_folium(map_heat, height=700, use_container_width=True)

# Page 2: Mobile Alerts
elif page == "2. Mobile Alerts":
    st.header("📱 Mobile Alerts")
    region = st.selectbox("Select District in KL", ["Bukit Bintang", "KLCC", "Brickfields", "Cheras"])
    left_col, right_col = st.columns([1, 2], gap="medium")

    with left_col:
        st.subheader("📍 Alert Feed")
        if region == "Bukit Bintang":
            st.markdown("🔥 *High heat warning: Jalan Sultan Ismail — *37.2°C (2PM–4PM)")
            st.markdown("❌ *Avoid*: Jalan Ampang & Jalan Pudu")
            st.markdown("✅ *Suggested Route*: Jalan Imbi → Eco Park → Pavilion KL")
        elif region == "KLCC":
            st.markdown("🔥 *Heat risk: Persiaran KLCC — *36.5°C")
            st.markdown("❌ *Avoid*: Jalan Tun Razak")
            st.markdown("✅ *Suggested Route*: Jalan Binjai → KLCC Park → Avenue K")
        elif region == "Brickfields":
            st.markdown("🔥 *Heat alert: Jalan Tun Sambanthan — *35.9°C")
            st.markdown("❌ *Avoid*: Jalan Travers")
            st.markdown("✅ *Suggested Route*: Jalan Sultan Abdul Samad → Lake Garden")
        else:
            st.markdown("🔥 *Hotspot: Taman Connaught — *35.4°C")
            st.markdown("❌ *Avoid*: Jalan Cheras")
            st.markdown("✅ *Suggested Route*: Jalan Cerdas → Taman Connaught MRT → Leisure Mall")

        show_route = st.toggle("🚶 Show Suggested Route", value=True)
        show_alerts = st.toggle("🔥 Show Heat Risk Alerts", value=True)

    with right_col:
        m = folium.Map(location=[3.15, 101.7], zoom_start=16, tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png", attr='OpenStreetMap')

        if show_alerts:
            for _ in range(15):  # Limit for performance
                lat = np.random.uniform(3.13, 3.17)
                lon = np.random.uniform(101.68, 101.73)
                temp = np.random.uniform(30, 40)
                icon = folium.Icon(color='red', icon='fire', prefix='fa')
                folium.Marker(
                    location=(lat, lon),
                    tooltip=f"🔥 LST: {temp:.1f}°C",
                    icon=icon
                ).add_to(m)

        if show_route:
            if region == "Bukit Bintang":
                route_coords = [[3.1450, 101.7120], [3.1475, 101.7095], [3.1500, 101.7070]]
            elif region == "KLCC":
                route_coords = [[3.1585, 101.7123], [3.1570, 101.7105], [3.1550, 101.7080]]
            elif region == "Brickfields":
                route_coords = [[3.1310, 101.6860], [3.1335, 101.6830], [3.1355, 101.6800]]
            else:
                route_coords = [[3.0800, 101.7430], [3.0815, 101.7405], [3.0830, 101.7380]]

            # Animated route using AntPath
            plugins.AntPath(
                locations=route_coords,
                color='blue',
                weight=6,
                delay=800,
                dash_array=[20, 30]
            ).add_to(m)

            total_distance = sum([geodesic(route_coords[i], route_coords[i+1]).km for i in range(len(route_coords)-1)])
            st.success(f"🚶 Estimated Route Distance: {total_distance:.2f} km | ETA: {int(total_distance * 15)} mins")

        plugins.Fullscreen(position='topright').add_to(m)
        LayerControl().add_to(m)
        st_folium(m, height=600, use_container_width=True)


# Page 3: Vulnerability Index
elif page == "3. Vulnerability Index":
    st.header("📊 Vulnerability Index")

    data = {
        "District": ["Bukit Bintang", "KLCC", "Brickfields", "Cheras", "Setapak", "Sentul", "Wangsa Maju", "Seputeh", "Titiwangsa"],
        "LST_(°C)": [37.2, 36.5, 35.9, 35.4, 36.1, 36.8, 35.7, 36.0, 35.3],
        "NDVI_(Green_%)": [12.5, 18.3, 22.4, 28.7, 19.1, 15.5, 25.2, 20.0, 23.3],
        "Elderly_(%)": [12.3, 9.8, 11.5, 13.2, 10.6, 14.1, 12.0, 13.5, 9.5],
        "Income_Level": ["Low", "High", "Medium", "Low", "Medium", "Low", "High", "Medium", "High"]
    }

    df = pd.DataFrame(data)

    # Scoring logic
    def calculate_score(row):
        score = 0
        if row["LST_(°C)"] > 36:
            score += 2
        elif row["LST_(°C)"] > 35:
            score += 1

        if row["NDVI_(Green_%)"] < 20:
            score += 2
        elif row["NDVI_(Green_%)"] < 25:
            score += 1

        if row["Elderly_(%)"] > 13:
            score += 2
        elif row["Elderly_(%)"] > 10:
            score += 1

        if row["Income_Level"] == "Low":
            score += 2
        elif row["Income_Level"] == "Medium":
            score += 1

        return score

    df["Vulnerability_Score"] = df.apply(calculate_score, axis=1)

    st.dataframe(df, use_container_width=True)

    # Map display
    st.subheader("🗺 Spatial Distribution of Vulnerability")
    district_coords = {
        "Bukit Bintang": (3.145, 101.710),
        "KLCC": (3.157, 101.712),
        "Brickfields": (3.129, 101.685),
        "Cheras": (3.078, 101.740),
        "Setapak": (3.194, 101.714),
        "Sentul": (3.179, 101.696),
        "Wangsa Maju": (3.210, 101.740),
        "Seputeh": (3.120, 101.692),
        "Titiwangsa": (3.172, 101.706),
    }

    map_vul = folium.Map(location=[3.14, 101.70], zoom_start=12)

    for _, row in df.iterrows():
        lat, lon = district_coords[row["District"]]
        score = row["Vulnerability_Score"]
        if score >= 6:
            color = 'red'
        elif score >= 4:
            color = 'orange'
        else:
            color = '#90EE90'  # Light green

        popup_info = f"""
        <b>{row['District']}</b><br>
        LST: {row['LST_(°C)']}°C<br>
        NDVI: {row['NDVI_(Green_%)']}%<br>
        Elderly: {row['Elderly_(%)']}%<br>
        Income: {row['Income_Level']}<br>
        Vulnerability Score: {score}
        """

        folium.CircleMarker(
            location=(lat, lon),
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_info, max_width=250)
        ).add_to(map_vul)

    st_folium(map_vul, height=600, use_container_width=True)




# Page 4: Planner Dashboard
elif page == "4. Planner Dashboard":
    st.header("🧹 Planner Dashboard")
    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        strategy = st.selectbox("Select a planning strategy", ["Tree Planting", "Green Roofs", "Cool Pavement"])
     
    with col2:
           district = st.selectbox("Select Target District", ["Bukit Bintang", "Setapak", "Bangsar", "Cheras"])

    st.markdown(f"📈 Heat mitigation simulation result for *{strategy}* in *{district}*")
    st.line_chart(pd.DataFrame({
        "Before": np.random.rand(10) * 4 + 32,
        "After": np.random.rand(10) * 3 + 28
    }))

    st.markdown("✅ Green interventions can reduce LST by 2–4°C per local zone.")
