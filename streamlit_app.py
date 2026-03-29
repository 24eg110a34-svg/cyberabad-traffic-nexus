"""
CYBERABAD TRAFFIC NEXUS - Streamlit Analytics Dashboard
Advanced ML Predictions, Analytics, and Data Visualization with Pandas & Matplotlib
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import json
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="CYBERABAD Traffic Analytics",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0c0c0e; }
    .css-1d391kg { padding: 1rem; }
    .metric-card {
        background: rgba(18, 18, 22, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    h1, h2, h3 { color: #f4f4f5; }
    .streamlit-expanderHeader { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE = "http://127.0.0.1:5000"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=30)
def fetch_traffic_data():
    """Fetch traffic data from Flask API"""
    try:
        response = requests.get(f"{API_BASE}/api/traffic", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=60)
def fetch_forecast():
    """Fetch forecast data"""
    try:
        response = requests.get(f"{API_BASE}/api/forecast", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=60)
def fetch_analysis():
    """Fetch analysis data"""
    try:
        response = requests.get(f"{API_BASE}/api/analysis", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=60)
def fetch_alerts():
    """Fetch alerts"""
    try:
        response = requests.get(f"{API_BASE}/api/alerts", timeout=5)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def run_ml_prediction(car_count, bike_count, bus_count, truck_count, hour, day, is_holiday, is_raining):
    """Run ML prediction via API"""
    try:
        response = requests.post(
            f"{API_BASE}/predict",
            json={
                "carCount": car_count,
                "bikeCount": bike_count,
                "busCount": bus_count,
                "truckCount": truck_count,
                "hour": hour,
                "day": day,
                "holiday": is_holiday,
                "raining": is_raining
            },
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_situation_color(situation):
    """Get color for situation"""
    colors = {
        "Low": "🟢",
        "Normal": "🟡",
        "Heavy": "🟠",
        "High": "🔴"
    }
    return colors.get(situation, "⚪")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🚦 Navigation")
    
    pages = {
        "📊 Dashboard": "dashboard",
        "🤖 ML Predictor": "predictor",
        "📈 Analytics": "analytics",
        "🚨 Alerts": "alerts",
        "🛣️ Segments": "segments",
        "⚙️ Settings": "settings"
    }
    
    selected_page = st.radio("Go to", list(pages.keys()))
    
    st.divider()
    
    st.markdown("### System Status")
    
    # Check API status
    try:
        response = requests.get(f"{API_BASE}/api/status", timeout=3)
        if response.status_code == 200:
            status = response.json()
            st.success("✅ Flask API Online")
            st.caption(f"Version: {status.get('version', 'N/A')}")
            st.caption(f"Junctions: {status.get('junctions', 0)}")
            st.caption(f"Roads: {status.get('segments', 0)}")
        else:
            st.error("❌ API Error")
    except:
        st.warning("⚠️ API Offline")
        st.caption("Start Flask server to continue")
    
    st.divider()
    
    # Weather info
    st.markdown("### 🌤️ Weather")
    weather_options = ["Clear", "Rain", "Heavy Rain", "Fog", "Hot"]
    selected_weather = st.selectbox("Weather", weather_options)
    
    # Mode toggles
    st.divider()
    st.markdown("### 🎛️ Modes")
    emergency_mode = st.checkbox("🚑 Emergency Mode")
    vip_mode = st.checkbox("👑 VIP Mode")

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

if selected_page == "📊 Dashboard":
    st.title("🚦 CYBERABAD Traffic Dashboard")
    
    # Fetch data
    traffic_data = fetch_traffic_data()
    
    if traffic_data:
        stats = traffic_data.get("stats", {})
        
        # Metrics row
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric(
                "Vehicles/hr",
                f"{stats.get('totalVehicles', 0):,}",
                delta=None
            )
        
        with col2:
            st.metric(
                "Avg Score",
                f"{stats.get('avgScore', 0):.1f}",
                delta=None
            )
        
        with col3:
            st.metric(
                "Critical Roads",
                stats.get('criticalRoads', 0),
                delta=None
            )
        
        with col4:
            st.metric(
                "Green Waves",
                stats.get('activeGreenWaves', 0),
                delta=None
            )
        
        with col5:
            st.metric(
                "Biryani Index",
                f"{stats.get('biryaniIndex', 0):.1f}",
                delta=None
            )
        
        with col6:
            st.metric(
                "CO₂ (kg)",
                f"{stats.get('co2Tracked', 0):.1f}",
                delta=None
            )
        
        st.divider()
        
        # City Overview
        st.subheader("🏙️ City Overview")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Area breakdown chart
            area_data = traffic_data.get("areaBreakdown", {})
            
            if area_data:
                areas = list(area_data.keys())
                scores = [area_data[a]['avgScore'] for a in areas]
                
                fig, ax = plt.subplots(figsize=(10, 4))
                colors = ['#ef4444', '#3b82f6', '#f97316', '#22c55e', '#8b5cf6']
                
                bars = ax.barh(areas, scores, color=colors)
                ax.set_xlabel('Congestion Score')
                ax.set_xlim(0, 100)
                ax.axvline(x=50, color='yellow', linestyle='--', alpha=0.5, label='Normal threshold')
                
                for bar, score in zip(bars, scores):
                    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                           f'{score:.1f}', va='center')
                
                st.pyplot(fig)
        
        with col2:
            # Situation badges
            st.markdown("### Situation by Area")
            
            for area, data in area_data.items():
                situation = data.get('situation', 'Normal')
                score = data.get('avgScore', 0)
                color = {
                    "Low": "green",
                    "Normal": "yellow",
                    "Heavy": "orange",
                    "High": "red"
                }.get(situation, "gray")
                
                st.markdown(f"""
                **{area.replace('_', ' ')}**
                - Score: {score:.1f}
                - Status: :{color}[{situation}]
                """)
        
        st.divider()
        
        # Top Congested Roads
        st.subheader("🔥 Top Congested Roads")
        
        segments = traffic_data.get("segments", [])
        if segments:
            top_segments = sorted(segments, key=lambda x: x.get('score', 0), reverse=True)[:10]
            
            df = pd.DataFrame([
                {
                    "Road": s.get('name', ''),
                    "Area": s.get('area', '').replace('_', ' '),
                    "Score": s.get('score', 0),
                    "Speed": s.get('speed', 0),
                    "Situation": s.get('situation', 'Normal')
                }
                for s in top_segments
            ])
            
            st.dataframe(
                df.style.applymap(
                    lambda x: 'background-color: rgba(239, 68, 68, 0.3)' if isinstance(x, (int, float)) and x > 70 else '',
                    subset=['Score']
                ),
                use_container_width=True,
                hide_index=True
            )
    
    else:
        st.error("Unable to fetch traffic data. Make sure Flask server is running.")

# ============================================================================
# ML PREDICTOR PAGE
# ============================================================================

elif selected_page == "🤖 ML Predictor":
    st.title("🤖 Random Forest Traffic Predictor")
    st.markdown("Adjust parameters to predict traffic conditions using ML model")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📊 Input Parameters")
        
        # Vehicle counts
        car_count = st.slider("🚗 Car Count", 0, 300, 50)
        bike_count = st.slider("🏍️ Bike Count", 0, 100, 30)
        bus_count = st.slider("🚌 Bus Count", 0, 50, 10)
        truck_count = st.slider("🚛 Truck Count", 0, 50, 15)
        
        st.markdown("### ⏰ Time Settings")
        
        hour = st.slider("Hour of Day", 0, 23, 12)
        day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day = st.selectbox("Day of Week", day_options)
        day_num = day_options.index(day)
        
        st.markdown("### 🌤️ Conditions")
        is_holiday = st.checkbox("🎉 Holiday")
        is_raining = st.checkbox("🌧️ Raining")
        
        predict_button = st.button("🚀 Run Prediction", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Prediction Results")
        
        if predict_button:
            with st.spinner("Running ML model..."):
                result = run_ml_prediction(
                    car_count, bike_count, bus_count, truck_count,
                    hour, day_num, is_holiday, is_raining
                )
            
            if result:
                prediction = result.get('prediction', 'Normal')
                confidence = result.get('confidence', 0) * 100
                score = result.get('score', 0)
                speed = result.get('speed', 0)
                delay = result.get('delay', 0)
                
                # Display prediction
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("Prediction", prediction, delta=get_situation_color(prediction))
                
                with col_b:
                    st.metric("Confidence", f"{confidence:.1f}%")
                
                with col_c:
                    st.metric("Congestion Score", f"{score:.1f}")
                
                st.divider()
                
                # Additional metrics
                col_d, col_e, col_f, col_g = st.columns(4)
                
                with col_d:
                    st.metric("Avg Speed", f"{speed:.1f} km/h")
                
                with col_e:
                    st.metric("Expected Delay", f"{delay:.1f} min")
                
                with col_f:
                    st.metric("Total Vehicles", result.get('vehicleCount', 0))
                
                with col_g:
                    biryani = result.get('biryaniIndex', 3.0)
                    st.metric("Biryani Index", f"{biryani:.1f}")
                
                st.divider()
                
                # Signal timing recommendations
                st.markdown("### 🚦 Signal Timing Recommendations")
                
                signal = result.get('signalTiming', {})
                
                sig_col1, sig_col2, sig_col3, sig_col4 = st.columns(4)
                
                with sig_col1:
                    st.metric("N-S Green", f"{signal.get('nsGreen', 45)}s")
                
                with sig_col2:
                    st.metric("E-W Green", f"{signal.get('ewGreen', 35)}s")
                
                with sig_col3:
                    st.metric("Cycle Time", f"{signal.get('cycleTime', 90)}s")
                
                with sig_col4:
                    st.metric("Yellow Time", f"{signal.get('yellowTime', 5)}s")
                
                # Probabilities
                st.markdown("### 📊 Situation Probabilities")
                
                probs = result.get('probabilities', {})
                prob_df = pd.DataFrame([
                    {"Situation": k, "Probability": f"{v*100:.1f}%"}
                    for k, v in probs.items()
                ])
                
                st.dataframe(prob_df, use_container_width=True, hide_index=True)
            else:
                st.error("Prediction failed. Check if Flask server is running.")
        
        else:
            st.info("👆 Adjust parameters and click 'Run Prediction' to get ML predictions")
            
            # Show model info
            st.markdown("### 🧠 Model Information")
            
            model_info = pd.DataFrame({
                "Parameter": ["Algorithm", "Estimators", "Max Depth", "Features", "Training Data"],
                "Value": ["Random Forest", "200", "15", "12", "8,928 records"]
            })
            
            st.dataframe(model_info, use_container_width=True, hide_index=True)

# ============================================================================
# ANALYTICS PAGE
# ============================================================================

elif selected_page == "📈 Analytics":
    st.title("📈 Traffic Analytics")
    
    analysis_data = fetch_analysis()
    
    if analysis_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 24-Hour Traffic Pattern")
            
            hourly = analysis_data.get('hourly', {})
            labels = hourly.get('labels', [])
            vehicles = hourly.get('vehicles', [])
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(range(24), vehicles, marker='o', linewidth=2, color='#3b82f6')
            ax.fill_between(range(24), vehicles, alpha=0.3, color='#3b82f6')
            ax.set_xlabel('Hour')
            ax.set_ylabel('Vehicles')
            ax.set_xticks(range(0, 24, 2))
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
        
        with col2:
            st.markdown("### 🚗 Vehicle Type Distribution")
            
            total_vehicles = sum(vehicles)
            cars = hourly.get('cars', [v * 0.45 for v in vehicles])
            bikes = hourly.get('bikes', [v * 0.35 for v in vehicles])
            buses = hourly.get('buses', [v * 0.10 for v in vehicles])
            trucks = hourly.get('trucks', [v * 0.10 for v in vehicles])
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            sizes = [sum(cars), sum(bikes), sum(buses), sum(trucks)]
            labels_pie = ['Cars', 'Bikes', 'Buses', 'Trucks']
            colors = ['#3b82f6', '#22c55e', '#f97316', '#ef4444']
            explode = (0.05, 0.05, 0.05, 0.05)
            
            ax.pie(sizes, explode=explode, labels=labels_pie, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=90)
            ax.axis('equal')
            
            st.pyplot(fig)
        
        st.divider()
        
        # Weekly Pattern
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("### 📅 Weekly Pattern")
            
            weekly = analysis_data.get('weekly', {})
            week_labels = weekly.get('labels', [])
            week_vehicles = weekly.get('vehicles', [])
            
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(week_labels, week_vehicles, color='#8b5cf6')
            ax.set_ylabel('Vehicles')
            ax.grid(True, alpha=0.3, axis='y')
            
            st.pyplot(fig)
        
        with col4:
            st.markdown("### 🎯 Feature Importance")
            
            feature_imp = analysis_data.get('featureImportance', [])
            
            if feature_imp:
                features = [f['name'] for f in feature_imp]
                values = [f['value'] for f in feature_imp]
                
                fig, ax = plt.subplots(figsize=(8, 5))
                bars = ax.barh(features, values, color='#22c55e')
                ax.set_xlabel('Importance (%)')
                ax.grid(True, alpha=0.3, axis='x')
                
                st.pyplot(fig)
        
        st.divider()
        
        # Class Distribution
        st.markdown("### 📊 Situation Class Distribution")
        
        class_dist = analysis_data.get('classDistribution', {})
        
        if class_dist:
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.metric("🟢 Low", class_dist.get('Low', 0))
            
            with col6:
                st.metric("🟡 Normal", class_dist.get('Normal', 0))
            
            with col7:
                st.metric("🟠 Heavy", class_dist.get('Heavy', 0))
            
            with col8:
                st.metric("🔴 High", class_dist.get('High', 0))
            
            # Distribution chart
            fig, ax = plt.subplots(figsize=(10, 4))
            situations = list(class_dist.keys())
            counts = list(class_dist.values())
            colors = ['#22c55e', '#eab308', '#f97316', '#ef4444']
            
            bars = ax.bar(situations, counts, color=colors)
            ax.set_ylabel('Count')
            ax.grid(True, alpha=0.3, axis='y')
            
            st.pyplot(fig)
    
    else:
        st.error("Unable to fetch analytics data.")

# ============================================================================
# ALERTS PAGE
# ============================================================================

elif selected_page == "🚨 Alerts":
    st.title("🚨 Traffic Alerts")
    
    alerts = fetch_alerts()
    
    if alerts:
        # Alert stats
        critical = [a for a in alerts if a.get('severity') == 'critical']
        high = [a for a in alerts if a.get('severity') == 'high']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Alerts", len(alerts))
        
        with col2:
            st.metric("🔴 Critical", len(critical))
        
        with col3:
            st.metric("🟠 High", len(high))
        
        st.divider()
        
        # Filter by severity
        severity_filter = st.multiselect(
            "Filter by Severity",
            options=["critical", "high", "medium", "low"],
            default=["critical", "high", "medium", "low"]
        )
        
        filtered_alerts = [a for a in alerts if a.get('severity') in severity_filter]
        
        for alert in filtered_alerts:
            severity = alert.get('severity', 'low')
            severity_color = {
                'critical': 'red',
                'high': 'orange',
                'medium': 'yellow',
                'low': 'gray'
            }.get(severity, 'gray')
            
            with st.container():
                st.markdown(f"""
                #### {alert.get('location', 'Unknown Location')}
                
                - **Type:** {alert.get('type', 'unknown')}
                - **Severity:** :{severity_color}[{severity.upper()}]
                - **Score:** {alert.get('score', 0):.1f}
                - **Area:** {alert.get('area', 'N/A')}
                
                **Message:** {alert.get('message', '')}
                
                **Action:** {alert.get('action', '')}
                """)
                
                st.divider()
    else:
        st.success("No alerts at this time. Traffic is flowing smoothly!")

# ============================================================================
# SEGMENTS PAGE
# ============================================================================

elif selected_page == "🛣️ Segments":
    st.title("🛣️ Road Segments Analysis")
    
    traffic_data = fetch_traffic_data()
    
    if traffic_data:
        segments = traffic_data.get('segments', [])
        
        # Filter options
        col1, col2 = st.columns([1, 3])
        
        with col1:
            area_filter = st.multiselect(
                "Filter by Area",
                options=["OLD_CITY", "IT_CORRIDOR", "CENTRAL", "EAST", "SOUTH"],
                default=["OLD_CITY", "IT_CORRIDOR", "CENTRAL", "EAST", "SOUTH"]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                options=["Score (High to Low)", "Score (Low to High)", "Name", "Speed"]
            )
        
        # Apply filters
        filtered = [s for s in segments if s.get('area') in area_filter]
        
        if sort_by == "Score (High to Low)":
            filtered = sorted(filtered, key=lambda x: x.get('score', 0), reverse=True)
        elif sort_by == "Score (Low to High)":
            filtered = sorted(filtered, key=lambda x: x.get('score', 0))
        elif sort_by == "Name":
            filtered = sorted(filtered, key=lambda x: x.get('name', ''))
        elif sort_by == "Speed":
            filtered = sorted(filtered, key=lambda x: x.get('speed', 0), reverse=True)
        
        # Display segments
        for segment in filtered:
            score = segment.get('score', 0)
            situation = segment.get('situation', 'Normal')
            
            color = {
                'Low': 'green',
                'Normal': 'yellow',
                'Heavy': 'orange',
                'High': 'red'
            }.get(situation, 'gray')
            
            with st.container():
                cols = st.columns([3, 1, 1, 1, 1, 1])
                
                with cols[0]:
                    st.markdown(f"**{segment.get('name', 'Unknown') }**")
                    st.caption(f"{segment.get('area', '').replace('_', ' ')} • {segment.get('lanes', 0)} lanes • {segment.get('distance', 0)} km")
                
                with cols[1]:
                    st.metric("Score", f"{score:.1f}")
                
                with cols[2]:
                    st.metric("Speed", f"{segment.get('speed', 0):.1f}")
                
                with cols[3]:
                    st.metric("Status", situation, delta=get_situation_color(situation))
                
                with cols[4]:
                    green = "✓" if segment.get('greenWave') else "✗"
                    st.markdown(f"Green Wave: {green}")
                
                with cols[5]:
                    hotspot = "🔥" if segment.get('hotspot') else ""
                    chronic = "⚠️" if segment.get('chronic') else ""
                    st.markdown(f"{hotspot} {chronic}")
                
                st.divider()

# ============================================================================
# SETTINGS PAGE
# ============================================================================

elif selected_page == "⚙️ Settings":
    st.title("⚙️ System Settings")
    
    st.markdown("### 🔌 API Configuration")
    
    api_url = st.text_input("Flask API URL", value=API_BASE)
    
    st.markdown("### 🎨 Display Settings")
    
    dark_mode = st.checkbox("Dark Mode", value=True)
    animations = st.checkbox("Enable Animations", value=False)
    
    st.markdown("### 📊 Data Settings")
    
    update_interval = st.slider("Update Interval (seconds)", 1, 30, 5)
    history_days = st.slider("Data History (days)", 1, 30, 7)
    
    st.markdown("### 🔐 Security")
    
    encryption_enabled = st.checkbox("Enable AES Encryption", value=True)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray;">
        CYBERABAD TRAFFIC NEXUS | Powered by Python, Streamlit, Pandas & ML
        <br>
        <small>Real-time traffic intelligence for Hyderabad</small>
    </div>
    """,
    unsafe_allow_html=True
)
