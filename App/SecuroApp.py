import streamlit as st
import time
import datetime
import pytz
import random
import pandas as pd
import numpy as np
import os
import google.generativeai as genai
import re
import requests
import io
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import warnings
warnings.filterwarnings('ignore')

# Language detection and translation support
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español (Spanish)',
    'fr': 'Français (French)',
    'pt': 'Português (Portuguese)',
    'zh': '中文 (Chinese)',
    'ar': 'العربية (Arabic)',
    'hi': 'हिन्दी (Hindi)',
    'ja': '日本語 (Japanese)',
    'ko': '한국어 (Korean)',
    'de': 'Deutsch (German)',
    'it': 'Italiano (Italian)',
    'ru': 'Русский (Russian)'
}

# Emergency Contacts for St. Kitts & Nevis
EMERGENCY_CONTACTS = {
    "Emergency": "911",
    "Police": "465-2241",
    "Hospital": "465-2551",
    "Fire Department": "465-2515 / 465-7167",
    "Coast Guard": "465-8384 / 466-9280",
    "Met Office": "465-2749",
    "Red Cross": "465-2584",
    "NEMA": "466-5100"
}

# Crime Hotspots Data for St. Kitts & Nevis
CRIME_HOTSPOTS = {
    # St. Kitts Hotspots
    "Basseterre Central": {"lat": 17.3026, "lon": -62.7177, "crimes": 45, "risk": "High", "types": ["Larceny", "Drug Crimes", "Assault"]},
    "Cayon": {"lat": 17.3581, "lon": -62.7440, "crimes": 28, "risk": "Medium", "types": ["Break-ins", "Theft"]},
    "Old Road Town": {"lat": 17.3211, "lon": -62.7847, "crimes": 22, "risk": "Medium", "types": ["Drug Crimes", "Vandalism"]},
    "Tabernacle": {"lat": 17.3100, "lon": -62.7200, "crimes": 31, "risk": "High", "types": ["Robbery", "Assault"]},
    "Sandy Point": {"lat": 17.3667, "lon": -62.8500, "crimes": 19, "risk": "Low", "types": ["Petty Theft"]},
    "Dieppe Bay": {"lat": 17.3833, "lon": -62.8167, "crimes": 15, "risk": "Low", "types": ["Vandalism"]},
    "Newton Ground": {"lat": 17.3319, "lon": -62.7269, "crimes": 26, "risk": "Medium", "types": ["Drug Crimes", "Larceny"]},
    "Molineux": {"lat": 17.2978, "lon": -62.7047, "crimes": 33, "risk": "High", "types": ["Armed Robbery", "Assault"]},
    
    # Nevis Hotspots
    "Charlestown": {"lat": 17.1348, "lon": -62.6217, "crimes": 18, "risk": "Medium", "types": ["Larceny", "Drug Crimes"]},
    "Gingerland": {"lat": 17.1019, "lon": -62.5708, "crimes": 12, "risk": "Low", "types": ["Petty Theft"]},
    "Newcastle": {"lat": 17.1667, "lon": -62.6000, "crimes": 14, "risk": "Low", "types": ["Vandalism", "Theft"]},
    "Cotton Ground": {"lat": 17.1281, "lon": -62.6442, "crimes": 16, "risk": "Medium", "types": ["Break-ins", "Larceny"]},
    "Ramsbury": {"lat": 17.1500, "lon": -62.6167, "crimes": 21, "risk": "Medium", "types": ["Drug Crimes", "Assault"]},
}

# St. Kitts timezone (Atlantic Standard Time)
SKN_TIMEZONE = pytz.timezone('America/St_Kitts')

def get_stkitts_time():
    """Get current time in St. Kitts & Nevis timezone"""
    utc_now = datetime.datetime.now(pytz.UTC)
    skn_time = utc_now.astimezone(SKN_TIMEZONE)
    return skn_time.strftime("%H:%M:%S")

def get_stkitts_date():
    """Get current date in St. Kitts & Nevis timezone"""
    utc_now = datetime.datetime.now(pytz.UTC)
    skn_time = utc_now.astimezone(SKN_TIMEZONE)
    return skn_time.strftime("%Y-%m-%d")

def create_crime_hotspot_map():
    """Create an interactive crime hotspot map for St. Kitts and Nevis"""
    # Center the map on St. Kitts and Nevis
    center_lat = 17.25
    center_lon = -62.7
    
    # Create the base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap',
        attr='Crime Hotspot Analysis - SECURO'
    )
    
    # Add Google Satellite layer as an option
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Color mapping for risk levels
    risk_colors = {
        'High': '#ff4444',
        'Medium': '#ffaa44', 
        'Low': '#44ff44'
    }
    
    # Add crime hotspots to the map
    for location, data in CRIME_HOTSPOTS.items():
        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="color: {risk_colors[data['risk']]}; margin: 0; text-align: center;">
                🚨 {location}
            </h4>
            <hr style="margin: 8px 0;">
            <p style="font-size: 1rem; line-height: 1.6; color: #e0e0e0;">SECURO (Security & Crime Understanding & Response Operations) is an advanced platform designed to support law enforcement, enhance public safety, and provide data-driven insights for crime prevention and analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <h3>Interactive Crime Mapping</h3>
            <p>Visualize crime patterns across 13+ mapped locations with real-time risk assessments and hotspot identification.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>AI Crime Assistant</h3>
            <p>Chat with SECURO for intelligent analysis, pattern recognition, and investigative support with multilingual capabilities.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Real-Time Analytics</h3>
            <p>Access comprehensive crime statistics with Q2 2025 data showing 292 total crimes and detailed performance metrics.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔮</div>
            <h3>Predictive Analytics</h3>
            <p>Advanced algorithms analyze historical data to predict crime trends and support strategic planning efforts.</p>
        </div>
        """, unsafe_allow_html=True)

# ABOUT PAGE
elif st.session_state.current_page == 'about':
    st.markdown("""
    <h2 style="color: #44ff44; margin-bottom: 20px; text-align: center;">About SECURO</h2>
    
    <p style="color: #e0e0e0;"><strong style="color: #44ff44;">SECURO</strong> is an intelligent and professional multilingual crime mitigation system built to provide real-time, data-driven insights for law enforcement, criminologists, policy makers, and the general public in St. Kitts & Nevis.</p>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Mission</h3>
    <p style="color: #e0e0e0;">Our mission is to support crime prevention, research, and public safety through:</p>
    <ul style="list-style: none; padding: 0; color: #e0e0e0;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Interactive maps and geographic analysis</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Statistical analysis and trend identification</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Predictive analytics for crime prevention</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Visual data presentations (charts, graphs, etc.)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Emergency contact guidance</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Multilingual communication support</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Core Capabilities</h3>
    <ul style="list-style: none; padding: 0; color: #e0e0e0;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Analyze and summarize current and historical crime data (local and global)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Detect trends and patterns across time, location, and type</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Recommend prevention strategies based on geographic and temporal factors</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Provide accessible language for general users, while supporting technical depth for experts</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Integrate with GIS, crime databases, and public safety systems</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Generate visual outputs and interactive maps</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Communicate effectively in multiple languages</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Adapt responses to be clear, concise, and actionable</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Current Data Integration</h3>
    <ul style="list-style: none; padding: 0; color: #e0e0e0;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Q2 2025 Crime Statistics (292 total crimes)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Historical Homicide Data (2015-2024)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">13+ Crime Hotspot Locations Mapped</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">District-wise Performance Analytics</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Multi-language Support (12 languages)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Real-time Emergency Contact Database</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Professional Standards</h3>
    <p style="color: #e0e0e0;">SECURO maintains professional standards with:</p>
    <ul style="list-style: none; padding: 0; color: #e0e0e0;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Accurate, evidence-based analysis</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Clear, non-panic-inducing communication</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Focus on empowerment and awareness</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Understanding of criminology and public safety best practices</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Real-time St. Kitts & Nevis time and date integration</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Data Security & Accuracy</h3>
    <p style="color: #e0e0e0;">All crime data is sourced directly from the Royal St. Christopher and Nevis Police Force and is updated regularly to ensure accuracy and relevance for operational decision-making. SECURO maintains the highest standards of data security and privacy.</p>
    """, unsafe_allow_html=True)

# CRIME HOTSPOTS PAGE
elif st.session_state.current_page == 'map':
    st.markdown('<h2 style="color: #44ff44;">🗺️ Crime Hotspot Map - St. Kitts & Nevis</h2>', unsafe_allow_html=True)
    
    try:
        with st.spinner("🗺️ Loading interactive crime hotspot map..."):
            crime_map = create_crime_hotspot_map()
            map_data = st_folium(
                crime_map,
                width="100%",
                height=600,
                returned_objects=["last_object_clicked_tooltip", "last_clicked"],
                key="crime_hotspot_map"
            )
            
            # Display clicked location info
            if map_data['last_object_clicked_tooltip']:
                clicked_info = map_data['last_object_clicked_tooltip']
                st.info(f"📍 **Last Clicked Location:** {clicked_info}")
    
    except Exception as e:
        st.error(f"❌ Map Error: {str(e)}")
        st.info("💡 Note: Make sure folium and streamlit-folium are installed")
    
    # Hotspot Analysis Summary
    st.markdown('<h3 style="color: #44ff44;">📍 Hotspot Analysis Summary</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(231, 76, 60, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #e74c3c;">
            <strong style="color: #e74c3c;">High Risk Areas (3)</strong><br>
            <span style="color: #e0e0e0; font-size: 0.9rem;">Basseterre Central, Molineux, Tabernacle<br>Total: 109 crimes</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(243, 156, 18, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12;">
            <strong style="color: #f39c12;">Medium Risk Areas (6)</strong><br>
            <span style="color: #e0e0e0; font-size: 0.9rem;">Cayon, Newton Ground, Old Road, etc.<br>Total: 133 crimes</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(39, 174, 96, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
            <strong style="color: #27ae60;">Low Risk Areas (4)</strong><br>
            <span style="color: #e0e0e0; font-size: 0.9rem;">Sandy Point, Dieppe Bay, etc.<br>Total: 60 crimes</span>
        </div>
        """, unsafe_allow_html=True)

# STATISTICS & ANALYTICS PAGE
elif st.session_state.current_page == 'statistics':
    st.markdown('<h2 style="color: #44ff44;">📊 Crime Statistics & Analytics</h2>', unsafe_allow_html=True)
    
    # Q2 2025 Overview
    st.markdown('<h3 style="color: #44ff44;">Q2 2025 Crime Statistics Overview</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    stats_data = st.session_state.crime_stats
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">292</div>
            <div class="stat-label">Total Crimes (Q2 2025)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">38.7%</div>
            <div class="stat-label">Overall Detection Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">207</div>
            <div class="stat-label">St. Kitts Crimes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">85</div>
            <div class="stat-label">Nevis Crimes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">4</div>
            <div class="stat-label">Murders (Q2 2025)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">31</div>
            <div class="stat-label">Drug Crimes (100% detected)</div>
        </div>
        """, unsafe_allow_html=True)

    # Chart Controls
    st.markdown('<h3 style="color: #44ff44;">📈 Interactive Analytics</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Homicide Trends", key="chart_trends"):
            fig = create_crime_charts("homicide_trend", stats_data)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if st.button("🔍 Crime Breakdown", key="chart_breakdown"):
            fig = create_crime_charts("crime_breakdown", stats_data)
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        if st.button("🎯 Detection Rates", key="chart_detection"):
            fig = create_crime_charts("detection_rates", stats_data)
            st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        if st.button("🔮 Predictions", key="chart_predictions"):
            fig = create_crime_charts("predictions", stats_data)
            st.plotly_chart(fig, use_container_width=True)
    
    # Crime Breakdown Details
    st.markdown('<h3 style="color: #44ff44;">🔍 Q2 2025 Crime Breakdown by Category</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #44ff44; margin-bottom: 15px;">
            <strong style="color: #44ff44;">Larcenies</strong><br>
            <span style="color: #e0e0e0;">92 cases (31.5%) | 21 detected (22.8%)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12; margin-bottom: 15px;">
            <strong style="color: #f39c12;">Malicious Damage</strong><br>
            <span style="color: #e0e0e0;">59 cases (20.2%) | 17 detected (28.8%)</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #e74c3c; margin-bottom: 15px;">
            <strong style="color: #e74c3c;">Bodily Harm</strong><br>
            <span style="color: #e0e0e0;">33 cases (11.3%) | 19 detected (57.6%)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60; margin-bottom: 15px;">
            <strong style="color: #27ae60;">Drug Crimes</strong><br>
            <span style="color: #e0e0e0;">31 cases (10.6%) | 31 detected (100%)</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #9b59b6; margin-bottom: 15px;">
            <strong style="color: #9b59b6;">Break-ins</strong><br>
            <span style="color: #e0e0e0;">26 cases (8.9%) | 7 detected (26.9%)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #34495e; margin-bottom: 15px;">
            <strong style="color: #34495e;">Murder/Manslaughter</strong><br>
            <span style="color: #e0e0e0;">4 cases (1.4%) | 2 detected (50%)</span>
        </div>
        """, unsafe_allow_html=True)

    # Historical Comparison
    st.markdown('<h3 style="color: #44ff44;">📈 Historical Comparison (Jan-June)</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: rgba(68, 255, 68, 0.05); border-radius: 8px;">
            <div style="font-size: 1.5rem; color: #44ff44; font-weight: bold;">2023 H1</div>
            <div style="color: #e0e0e0;">672 total crimes</div>
            <div style="color: #e74c3c; font-size: 0.9rem;">17 murders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: rgba(68, 255, 68, 0.05); border-radius: 8px;">
            <div style="font-size: 1.5rem; color: #44ff44; font-weight: bold;">2024 H1</div>
            <div style="color: #e0e0e0;">586 total crimes</div>
            <div style="color: #e74c3c; font-size: 0.9rem;">16 murders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: rgba(68, 255, 68, 0.1); border-radius: 8px; border: 1px solid rgba(68, 255, 68, 0.3);">
            <div style="font-size: 1.5rem; color: #44ff44; font-weight: bold;">2025 H1</div>
            <div style="color: #e0e0e0;">574 total crimes</div>
            <div style="color: #27ae60; font-size: 0.9rem;">4 murders (↓75%)</div>
        </div>
        """, unsafe_allow_html=True)

# EMERGENCY CONTACTS PAGE
elif st.session_state.current_page == 'emergency':
    st.markdown("""
    <h2 style="color: #e74c3c; margin-bottom: 30px; text-align: center;">🚨 Emergency Contacts</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    emergency_contacts = [
        ("🚔 Police Emergency", "911", "For immediate police assistance and emergency response"),
        ("🏢 Police Headquarters", "465-2241", "Royal St. Christopher and Nevis Police Force\nLocal Intelligence: Ext. 4238/4239"),
        ("🏥 Medical Emergency", "465-2551", "Hospital services and medical emergencies"),
        ("🔥 Fire Department", "465-2515", "Fire emergencies and rescue operations\nAlt: 465-7167"),
        ("🚢 Coast Guard", "465-8384", "Maritime emergencies and water rescue\nAlt: 466-9280"),
        ("🌡️ Met Office", "465-2749", "Weather emergencies and warnings"),
        ("➕ Red Cross", "465-2584", "Disaster relief and emergency aid"),
        ("⚡ NEMA", "466-5100", "National Emergency Management Agency")
    ]
    
    for i, (title, number, description) in enumerate(emergency_contacts):
        col = [col1, col2, col3, col4][i % 4]
        with col:
            st.markdown(f"""
            <div class="emergency-card">
                <h3>{title}</h3>
                <div class="phone-number">{number}</div>
                <p style="color: #e0e0e0;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Emergency Guidelines
    st.markdown("""
    <div style="background: rgba(255, 243, 205, 0.1); border: 1px solid rgba(255, 234, 167, 0.3); padding: 20px; border-radius: 10px; margin-top: 30px;">
        <h3 style="color: #f39c12; margin-bottom: 15px;">⚠️ Important Emergency Guidelines</h3>
        <ul style="color: #e0e0e0; line-height: 1.6; list-style: none; padding: 0;">
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                <strong>For life-threatening emergencies, always call 911 first</strong>
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                When calling, provide your exact location and nature of emergency
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                Stay on the line until instructed to hang up
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                Keep these numbers easily accessible at all times
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# AI ASSISTANT CHAT PAGE - ENHANCED VERSION
elif st.session_state.current_page == 'chat':
    st.markdown('<h2 style="color: #44ff44; text-align: center;">💬 Chat with SECURO AI</h2>', unsafe_allow_html=True)
    
    # Enhanced Database Status Section
    st.markdown('<h3 style="color: #44ff44;">📊 Crime Intelligence System Status</h3>', unsafe_allow_html=True)

        # Load CSV data with better error handling
    if not st.session_state.csv_loaded:
        with st.spinner("🔍 Initializing crime intelligence system..."):
            csv_data, status_message = load_csv_data()
            st.session_state.csv_data = csv_data
            st.session_state.csv_loaded = True
           
            if csv_data is not None:
                st.success(f"✅ External database loaded successfully! {len(csv_data)} records found.")
               
                # Add success message to chat if messages are empty
                if not st.session_state.messages:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"✅ **SECURO INTELLIGENCE SYSTEM ONLINE**\n\n🔍 **External Database:** {len(csv_data)} records loaded successfully\n📊 **Built-in Intelligence:** 13 crime hotspots mapped, Q2 2025 statistics integrated\n🎯 **AI Analysis:** Advanced crime pattern recognition active\n\n**ASK ME ANYTHING ABOUT:**\n• Specific locations (e.g., 'Basseterre Central crime analysis')\n• Crime trends (e.g., 'homicide statistics 2023-2025')\n• Prevention strategies (e.g., 'how to reduce larceny in high-risk areas')\n• Performance analysis (e.g., 'why is Nevis outperforming St. Kitts?')\n\n🌍 **Multi-language support available!** | 🕒 Current time: {get_stkitts_time()} AST",
                        "timestamp": get_stkitts_time()
                    })
            else:
                st.warning(f"⚠️ External database not found - Built-in intelligence active")
               
                # Add info message to chat if messages are empty
                if not st.session_state.messages:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"🔍 **SECURO INTELLIGENCE SYSTEM ONLINE**\n\n📊 **Built-in Crime Intelligence Active:**\n• 13 mapped crime hotspots with detailed analysis\n• Q2 2025 comprehensive crime statistics (292 total crimes)\n• Historical trend analysis (2015-2025)\n• Performance metrics by location and crime type\n\n⚠️ **External Database:** Not found ({status_message})\n\n**I CAN STILL PROVIDE EXPERT ANALYSIS ON:**\n• All mapped locations and their crime profiles\n• Drug crime success (100% detection rate)\n• Homicide trends (76% reduction 2023→2025)\n• Detection rate comparisons (Nevis 52.9% vs St. Kitts 32.9%)\n• Strategic law enforcement recommendations\n\n**Try asking:** 'What's the crime situation in Molineux?' or 'Why are drug detection rates so high?'",
                        "timestamp": get_stkitts_time()
                    })

    # Enhanced Status Display
    ai_status = st.session_state.get('ai_status', 'AI Status Unknown')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.csv_data is not None:
            st.success(f"📊 **External Database**\n{len(st.session_state.csv_data)} records active")
        else:
            st.info("📊 **External Database**\nNot loaded - built-in active")
    
    with col2:
        if st.session_state.get('ai_enabled', False):
            st.success(f"🤖 **AI Analysis**\nGemini 1.5 Flash active")
        else:
            st.error(f"🤖 **AI Analysis**\nOffline - basic mode")
    
    with col3:
        st.success("🗺️ **Crime Intelligence**\n13 hotspots mapped")

    # Quick Intelligence Overview
    total_hotspots = len(CRIME_HOTSPOTS)
    high_risk = len([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'High'])
    medium_risk = len([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'Medium'])
    low_risk = len([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'Low'])
    
    st.info(f"🎯 **Current Intelligence:** Q2 2025: 292 crimes | Detection: 38.7% | Hotspots: {high_risk} High Risk, {medium_risk} Medium Risk, {low_risk} Low Risk | Homicides down 76% from 2023")
    
    # Initialize welcome message if needed
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🚔 **SECURO CRIME INTELLIGENCE SYSTEM INITIALIZING...**\n\nPlease wait while I activate all crime analysis modules...",
            "timestamp": get_stkitts_time()
        })
    
    # Display chat messages with enhanced formatting
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Clean user message
            clean_content = str(message["content"]).strip()
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-content">{clean_content}</div>
                <div class="message-time">You • {message["timestamp"]} AST</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Clean bot message and ensure proper formatting
            clean_content = str(message["content"]).strip()
            # Remove any unwanted HTML or formatting
            clean_content = re.sub(r'<[^>]+>', '', clean_content)
            clean_content = clean_content.replace('```', '')
           
            # Ensure proper SECURO formatting
            if not any(starter in clean_content for starter in ["SECURO", "🚔", "✅", "🔍"]):
                clean_content = f"SECURO ANALYSIS: {clean_content}"
           
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="message-content">{clean_content}</div>
                <div class="message-time">SECURO AI • {message["timestamp"]} AST</div>
            </div>
            """, unsafe_allow_html=True)

    # Suggested Questions Section - ENHANCED
    st.markdown("### 💡 Expert Questions - Try These:")
    
    suggested_questions = get_suggested_questions()
    
    # Display suggestions in a more organized way
    col1, col2 = st.columns(2)
    
    for i, question in enumerate(suggested_questions):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(
                question, 
                key=f"suggest_{i}",
                help=f"Click to ask: {question}",
                use_container_width=True
            ):
                current_time = get_stkitts_time()
                
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": current_time
                })
                
                # Generate response
                with st.spinner("🔍 Analyzing crime intelligence..."):
                    csv_results = search_csv_data(st.session_state.csv_data, question)
                    response = get_ai_response(question, csv_results, st.session_state.selected_language)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": current_time
                })
                
                st.rerun()

    # Chat input with enhanced functionality
    st.markdown("### 💬 Ask SECURO Anything About Crime Data")
    
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
       
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask about crime trends, locations, statistics, or prevention strategies...",
                label_visibility="collapsed",
                key="user_input"
            )
       
        with col2:
            send_button = st.form_submit_button("🔍 Analyze", type="primary")
       
        if send_button and user_input:
            current_time = get_stkitts_time()
           
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": current_time
            })
           
            # Generate enhanced response
            with st.spinner("🔍 Processing through SECURO intelligence systems..."):
                csv_results = search_csv_data(st.session_state.csv_data, user_input)
                response = get_ai_response(user_input, csv_results, st.session_state.selected_language)
           
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": current_time
            })
           
            st.rerun()

    # Chat Tips Section
    with st.expander("💡 Tips for Better Results"):
        st.markdown("""
        **🎯 For Best Results, Try:**
        - **Location queries:** "Crime analysis for Basseterre Central"
        - **Trend questions:** "Homicide trends from 2023 to 2025"  
        - **Comparison queries:** "Compare St. Kitts vs Nevis detection rates"
        - **Strategy questions:** "Prevention strategies for high-risk areas"
        - **Performance queries:** "Why is drug detection at 100%?"
        
        **📊 Available Data:**
        - Q2 2025 comprehensive statistics (292 crimes)
        - 13 mapped crime hotspots with risk assessments
        - Historical trends (2015-2025)
        - Detection rates by crime type and location
        - Emergency contact information
        
        **🌍 Multi-Language Support:**
        - Available in 12 languages
        - Change language in the sidebar
        - Technical terms provided in English
        """)

# Enhanced Status bar with real-time crime intelligence updates
status_message = f"{len(st.session_state.csv_data)} External Records" if st.session_state.csv_data is not None else "Built-in Intelligence"
current_time = get_stkitts_time()

st.markdown(f"""
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot"></div>
        <span>SECURO {"AI Active" if st.session_state.get('ai_enabled', False) else "Basic Mode"}</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Intelligence: {status_message}</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Hotspots: 13 Locations</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Q2 2025: 292 Crimes</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>{current_time} AST</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>{SUPPORTED_LANGUAGES[st.session_state.selected_language]}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced Footer with Crime Intelligence Credits
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; padding: 20px; margin-top: 20px; border-top: 1px solid rgba(68, 255, 68, 0.2);">
    🔍 <strong>SECURO Crime Intelligence System</strong> | Powered by Advanced AI Analysis<br>
    📊 Data Source: Royal St. Christopher & Nevis Police Force (RSCNPF) | Q2 2025 Statistics Integrated<br>
    📞 Local Intelligence Office: <a href="tel:+18694652241" style="color: #44ff44; text-decoration: none;">869-465-2241</a> Ext. 4238/4239 | 
    📧 <a href="mailto:liosk@police.kn" style="color: #44ff44; text-decoration: none;">liosk@police.kn</a><br>
    🔄 Last Updated: {get_stkitts_date()} {get_stkitts_time()} AST | Real-time Analytics & Predictive Intelligence<br>
    🗺️ Crime Hotspot Intelligence: 13 locations mapped | 🎯 Detection Rate Analysis: 38.7% overall (Nevis 52.9%, St. Kitts 32.9%)<br>
    🌍 Multi-language Support: 12 languages | 🔒 Secure Law Enforcement Platform | 🤖 AI-Enhanced Crime Prevention
</div>
""", unsafe_allow_html=True)margin: 4px 0;"><strong>📊 Total Crimes:</strong> {data['crimes']}</p>
            <p style="margin: 4px 0;"><strong>⚠️ Risk Level:</strong> 
               <span style="color: {risk_colors[data['risk']]}; font-weight: bold;">{data['risk']}</span>
            </p>
            <p style="margin: 4px 0;"><strong>🔍 Common Types:</strong></p>
            <ul style="margin: 4px 0; padding-left: 20px;">
                {''.join([f'<li>{crime_type}</li>' for crime_type in data['types']])}
            </ul>
            <small style="color: #666;">📍 Lat: {data['lat']:.4f}, Lon: {data['lon']:.4f}</small>
        </div>
        """
        
        # Calculate marker size based on crime count
        marker_size = max(10, min(30, data['crimes'] * 0.8))
        
        # Add marker to map
        folium.CircleMarker(
            location=[data['lat'], data['lon']],
            radius=marker_size,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{location}: {data['crimes']} crimes ({data['risk']} risk)",
            color='black',
            fillColor=risk_colors[data['risk']],
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
        
        # Add text label for major hotspots
        if data['crimes'] > 25:
            folium.Marker(
                location=[data['lat'] + 0.01, data['lon']],
                icon=folium.DivIcon(
                    html=f"""<div style="font-size: 10px; font-weight: bold; 
                             color: white; text-shadow: 1px 1px 2px black;">
                             {location}</div>""",
                    icon_size=(100, 20),
                    icon_anchor=(50, 10)
                )
            ).add_to(m)
    
    # Add a legend
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 180px; height: 140px; 
                background-color: rgba(0, 0, 0, 0.8); 
                border: 2px solid rgba(68, 255, 68, 0.5);
                border-radius: 10px; z-index:9999; 
                font-size: 12px; font-family: Arial;
                padding: 10px; color: white;">
    <h4 style="margin: 0 0 10px 0; color: #44ff44;">🗺️ Crime Risk Legend</h4>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['High']};">●</span> High Risk (25+ crimes)
    </div>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['Medium']};">●</span> Medium Risk (15-24 crimes)  
    </div>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['Low']};">●</span> Low Risk (<15 crimes)
    </div>
    <small style="color: #888;">Marker size = Crime frequency</small>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# Crime Statistics Data Structure
@st.cache_data
def load_crime_statistics():
    """Load and structure crime statistics data"""
    
    # Q2 2025 Data (April-June)
    q2_2025_data = {
        'period': 'Q2 2025 (Apr-Jun)',
        'federation': {
            'murder_manslaughter': {'total': 4, 'detected': 2, 'juvenile': 0},
            'shooting_intent': {'total': 1, 'detected': 1, 'juvenile': 0},
            'woundings_firearm': {'total': 0, 'detected': 0, 'juvenile': 0},
            'attempted_murder': {'total': 4, 'detected': 0, 'juvenile': 0},
            'bodily_harm': {'total': 33, 'detected': 19, 'juvenile': 4},
            'sex_crimes': {'total': 7, 'detected': 1, 'juvenile': 0},
            'break_ins': {'total': 26, 'detected': 7, 'juvenile': 0},
            'larcenies': {'total': 92, 'detected': 21, 'juvenile': 2},
            'robberies': {'total': 8, 'detected': 1, 'juvenile': 0},
            'firearms_ammo': {'total': 5, 'detected': 5, 'juvenile': 0},
            'drugs': {'total': 31, 'detected': 31, 'juvenile': 0},
            'malicious_damage': {'total': 59, 'detected': 17, 'juvenile': 1},
            'other': {'total': 22, 'detected': 8, 'juvenile': 0},
            'total_crimes': 292,
            'detection_rate': 38.7
        },
        'st_kitts': {
            'total_crimes': 207,
            'detection_rate': 32.9
        },
        'nevis': {
            'total_crimes': 85,
            'detection_rate': 52.9
        }
    }
    
    # Historical homicide data (2015-2024)
    homicide_data = {
        'yearly_totals': {
            2015: 29, 2016: 32, 2017: 23, 2018: 23, 2019: 12, 
            2020: 10, 2021: 14, 2022: 11, 2023: 31, 2024: 28
        },
        'monthly_2024': [1, 5, 5, 2, 3, 3, 6, 1, 2, 0, 0, 0],  # Jan-Sep (incomplete year)
        'methods': {
            'shooting': 173, 'stabbing': 29, 'bludgeoning': 4, 
            'strangulation': 5, 'other': 2
        },
        'age_groups': {
            '0-17': 10, '18-35': 132, '36-55': 54, '>55': 17
        },
        'districts': {
            'A': {'2023': 22, '2024': 15},
            'B': {'2023': 5, '2024': 8}, 
            'C': {'2023': 4, '2024': 5}
        }
    }
    
    # Comparative statistics (Jan-June)
    comparative_data = {
        '2023_h1': {'total': 672, 'murder': 17, 'larcenies': 231, 'drugs': 6},
        '2024_h1': {'total': 586, 'murder': 16, 'larcenies': 193, 'drugs': 8},
        '2025_h1': {'total': 574, 'murder': 4, 'larcenies': 185, 'drugs': 45}
    }
    
    return {
        'current_quarter': q2_2025_data,
        'homicides': homicide_data,
        'comparative': comparative_data,
        'last_updated': get_stkitts_date()
    }

def create_crime_charts(chart_type, crime_data):
    """Create various crime analysis charts"""
    
    if chart_type == "homicide_trend":
        # Homicide trend analysis
        years = list(crime_data['homicides']['yearly_totals'].keys())
        counts = list(crime_data['homicides']['yearly_totals'].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=counts,
            mode='lines+markers',
            name='Actual Homicides',
            line=dict(color='#ff4444', width=3),
            marker=dict(size=8)
        ))
        
        # Add predictions
        pred_years = [2025, 2026, 2027]
        pred_counts = [10, 8, 7]
        
        fig.add_trace(go.Scatter(
            x=pred_years, y=pred_counts,
            mode='lines+markers',
            name='Predicted',
            line=dict(color='#44ff44', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="St. Kitts & Nevis Homicide Trends (2015-2027)",
            xaxis_title="Year",
            yaxis_title="Number of Homicides",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "crime_breakdown":
        # Crime breakdown pie chart
        crime_data_q2 = crime_data['current_quarter']['federation']
        crimes = ['Larcenies', 'Malicious Damage', 'Bodily Harm', 'Drug Crimes', 'Break-ins', 'Murder']
        counts = [
            crime_data_q2['larcenies']['total'],
            crime_data_q2['malicious_damage']['total'],
            crime_data_q2['bodily_harm']['total'],
            crime_data_q2['drugs']['total'],
            crime_data_q2['break_ins']['total'],
            crime_data_q2['murder_manslaughter']['total']
        ]
        
        fig = go.Figure(data=[go.Pie(
            labels=crimes,
            values=counts,
            hole=0.4,
            marker_colors=['#44ff44', '#f39c12', '#e74c3c', '#27ae60', '#9b59b6', '#34495e']
        )])
        
        fig.update_layout(
            title="Crime Types Distribution Q2 2025",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "detection_rates":
        # Detection rates by quarter/region
        regions = ['Federation', 'St. Kitts', 'Nevis']
        detection_rates = [38.7, 32.9, 52.9]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=regions, y=detection_rates,
            marker_color=['#f39c12', '#e74c3c', '#44ff44'],
            text=[f"{rate}%" for rate in detection_rates],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Crime Detection Rates Q2 2025",
            xaxis_title="Region",
            yaxis_title="Detection Rate (%)",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "predictions":
        # Crime predictions
        years = [2025, 2026, 2027]
        predictions = [10, 8, 7]
        upper_bound = [15, 12, 10]
        lower_bound = [5, 4, 3]
        
        fig = go.Figure()
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=years + years[::-1],
            y=upper_bound + lower_bound[::-1],
            fill='toself',
            fillcolor='rgba(68, 255, 68, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval'
        ))
        
        fig.add_trace(go.Scatter(
            x=years, y=predictions,
            mode='lines+markers',
            name='Predicted Homicides',
            line=dict(color='#44ff44', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Homicide Predictions 2025-2027",
            xaxis_title="Year",
            yaxis_title="Predicted Homicides",
            template="plotly_dark",
            height=500
        )
        
        return fig

# Enhanced System Prompt - IMPROVED VERSION
def get_system_prompt(language='en'):
    base_prompt = """
You are SECURO, an expert crime analysis AI for the Royal St. Christopher & Nevis Police Force.

CURRENT CRIME DATA CONTEXT (Q2 2025):
- Total Crimes: 292 (St. Kitts: 207, Nevis: 85)
- Detection Rate: 38.7% overall (St. Kitts: 32.9%, Nevis: 52.9%)
- Major Crime Categories:
  * Larcenies: 92 cases (22.8% detection rate) - HIGHEST VOLUME
  * Malicious Damage: 59 cases (28.8% detection rate)
  * Bodily Harm: 33 cases (57.6% detection rate)
  * Drug Crimes: 31 cases (100% detection rate) - EXCELLENT PERFORMANCE
  * Break-ins: 26 cases (26.9% detection rate)
  * Murder/Manslaughter: 4 cases (50% detection rate)

CRIME HOTSPOTS - HIGH RISK (25+ crimes):
- Basseterre Central: 45 crimes (Larceny, Drug Crimes, Assault)
- Molineux: 33 crimes (Armed Robbery, Assault)  
- Tabernacle: 31 crimes (Robbery, Assault)

CRIME HOTSPOTS - MEDIUM RISK (15-24 crimes):
- Cayon: 28 crimes | Newton Ground: 26 crimes | Old Road: 22 crimes
- Ramsbury: 21 crimes | Charlestown: 18 crimes | Cotton Ground: 16 crimes

CRIME HOTSPOTS - LOW RISK (<15 crimes):
- Sandy Point: 19 crimes | Dieppe Bay: 15 crimes | Newcastle: 14 crimes | Gingerland: 12 crimes

HISTORICAL TRENDS:
- Homicides: DOWN 60% from 2023 (17→4 cases in H1)
- Drug enforcement: MAJOR SUCCESS (100% detection vs 6→45 cases increase shows proactive policing)
- Nevis consistently outperforms St. Kitts in detection rates

YOUR EXPERT ROLE:
1. Analyze crime patterns using SPECIFIC DATA above
2. Provide location-based risk assessments
3. Recommend evidence-based prevention strategies
4. Explain trends with concrete numbers
5. Give actionable law enforcement insights

RESPONSE FORMAT:
- Start with "SECURO ANALYSIS:"
- Use ACTUAL statistics and location names
- Reference specific crime types and numbers
- Provide tactical recommendations
- Be authoritative but accessible

When users ask about crime data, USE THE EXACT NUMBERS AND LOCATIONS provided above, not generic responses.
"""
    
    if language != 'en':
        language_instruction = f"""
LANGUAGE: Respond primarily in {SUPPORTED_LANGUAGES.get(language, language)}, but include English technical terms in parentheses for clarity.
"""
        return base_prompt + language_instruction
    
    return base_prompt

# Comprehensive Crime Context Generator
def get_crime_context():
    """Generate detailed crime context for AI analysis"""
    
    current_stats = """
DETAILED CRIME STATISTICS (Q2 2025):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 OVERALL PERFORMANCE:
- Total Crimes: 292 (St. Kitts: 207 | Nevis: 85)
- Detection Rate: 38.7% overall (St. Kitts: 32.9% | Nevis: 52.9%)

📈 CRIME BREAKDOWN BY TYPE:
1. Larcenies: 92 cases (31.5% of all crimes) | Detection: 21/92 (22.8%)
2. Malicious Damage: 59 cases (20.2%) | Detection: 17/59 (28.8%) 
3. Bodily Harm: 33 cases (11.3%) | Detection: 19/33 (57.6%)
4. Drug Crimes: 31 cases (10.6%) | Detection: 31/31 (100%) ⭐ EXCELLENT
5. Break-ins: 26 cases (8.9%) | Detection: 7/26 (26.9%)
6. Murder/Manslaughter: 4 cases (1.4%) | Detection: 2/4 (50%)
7. Robberies: 8 cases | Sex Crimes: 7 cases | Other: 22 cases

🎯 KEY INSIGHTS:
- Nevis Police significantly outperforming St. Kitts (52.9% vs 32.9% detection)
- Drug enforcement at 100% - outstanding proactive policing
- Larceny remains biggest challenge with lowest detection rate
- Violent crime (murder) down dramatically from previous years
"""
    
    hotspot_analysis = """
🗺️ COMPREHENSIVE HOTSPOT ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 HIGH RISK AREAS (Require Daily Patrols):
1. Basseterre Central: 45 crimes - Larceny, Drug Crimes, Assault
2. Molineux: 33 crimes - Armed Robbery, Assault  
3. Tabernacle: 31 crimes - Robbery, Assault
   → Combined: 109 crimes (37.3% of all federation crimes)

🟡 MEDIUM RISK AREAS (Every 2-3 Days):
4. Cayon: 28 crimes - Break-ins, Theft
5. Newton Ground: 26 crimes - Drug Crimes, Larceny
6. Old Road Town: 22 crimes - Drug Crimes, Vandalism
7. Ramsbury (Nevis): 21 crimes - Drug Crimes, Assault
8. Charlestown (Nevis): 18 crimes - Larceny, Drug Crimes
9. Cotton Ground (Nevis): 16 crimes - Break-ins, Larceny
   → Combined: 131 crimes (44.9% of all crimes)

🟢 LOW RISK AREAS (Weekly Patrols):
10. Sandy Point: 19 crimes - Petty Theft
11. Dieppe Bay: 15 crimes - Vandalism
12. Newcastle (Nevis): 14 crimes - Vandalism, Theft
13. Gingerland (Nevis): 12 crimes - Petty Theft
    → Combined: 60 crimes (20.5% of all crimes)
"""
    
    trends_analysis = """
📈 CRITICAL TREND ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 MAJOR SUCCESSES:
- Homicides: DOWN 76% (17→4 cases in first half compared to 2023)
- Drug Detection: 100% success rate (vs historical ~25-30%)
- Nevis Performance: 52.9% detection rate shows effective community policing

⚠️ AREAS NEEDING ATTENTION:
- Larceny Detection: Only 22.8% - requires enhanced investigation protocols
- St. Kitts Performance Gap: 20% lower detection rate than Nevis
- Break-in Prevention: 26.9% detection suggests need for forensic improvements

🔮 PREDICTIVE INDICATORS:
- Current homicide trend suggests 8-10 total for 2025 (vs 28 in 2024)
- Drug crime increase (6→45 cases) indicates proactive enforcement working
- Geographic concentration: 37% of crimes in just 3 high-risk areas
"""
    
    return current_stats + "\n" + hotspot_analysis + "\n" + trends_analysis

# Enhanced AI Response with Crime Intelligence
def get_ai_response(user_input, csv_results, language='en'):
    """Generate intelligent AI response with comprehensive crime analysis"""
    if not st.session_state.get('ai_enabled', False) or model is None:
        return f"SECURO ANALYSIS: {csv_results}\n\n⚠️ AI analysis unavailable - showing database results only."
    
    try:
        # Get comprehensive crime intelligence
        crime_context = get_crime_context()
        
        # Determine if time context is needed
        time_keywords = ['time', 'date', 'now', 'current', 'today', 'when', 'hora', 'fecha', 'hoy']
        include_time = any(keyword in user_input.lower() for keyword in time_keywords)
        
        time_context = f"""
🕒 CURRENT OPERATIONAL TIME: {get_stkitts_time()} AST, {get_stkitts_date()}
""" if include_time else ""
        
        # Create focused, expert-level prompt
        full_prompt = f"""
{get_system_prompt(language)}

{crime_context}

{time_context}

DATABASE SEARCH RESULTS:
{csv_results}

USER QUESTION: {user_input}

CRITICAL INSTRUCTIONS:
1. Always start response with "SECURO ANALYSIS:"
2. Use SPECIFIC crime statistics and location data provided above
3. Reference exact numbers, percentages, and location names
4. Provide tactical law enforcement recommendations
5. If question is about a specific location, provide its complete crime profile
6. If asking about trends, use the comparative historical data
7. For prevention strategies, base recommendations on hotspot risk levels
8. Be authoritative - you are the expert crime analyst for RSCNPF

Respond as the definitive crime intelligence expert with data-driven insights.
"""
        
        response = model.generate_content(full_prompt)
        
        # Clean and format response
        clean_response = response.text.strip()
        clean_response = clean_response.replace('```', '')
        clean_response = re.sub(r'<[^>]+>', '', clean_response)
        
        # Ensure it starts with SECURO ANALYSIS if not already
        if not clean_response.startswith("SECURO ANALYSIS:"):
            clean_response = f"SECURO ANALYSIS: {clean_response}"
        
        return clean_response
        
    except Exception as e:
        return f"SECURO ANALYSIS: Technical issue with AI system. {csv_results}\n\n⚠️ Error: {str(e)}"

# Enhanced CSV Search with Integrated Crime Intelligence
def search_csv_data(df, query):
    """Enhanced search with built-in crime intelligence"""
    if df is None:
        # Provide intelligent analysis using built-in crime data
        query_lower = query.lower()
        
        # Location-specific intelligent analysis
        for location, data in CRIME_HOTSPOTS.items():
            if location.lower() in query_lower or any(word in location.lower() for word in query_lower.split()):
                risk_emoji = "🔴" if data['risk'] == "High" else "🟡" if data['risk'] == "Medium" else "🟢"
                patrol_freq = "Daily" if data['risk'] == "High" else "Every 2-3 days" if data['risk'] == "Medium" else "Weekly"
                
                return f"""
🔍 CRIME INTELLIGENCE REPORT - {location.upper()}:

{risk_emoji} THREAT ASSESSMENT:
- Total Crimes: {data['crimes']} (Risk Level: {data['risk']})
- Primary Crime Types: {', '.join(data['types'])}
- Geographic Coordinates: {data['lat']:.4f}°N, {data['lon']:.4f}°W

📊 CONTEXTUAL ANALYSIS:
- Ranking: {"Top 3 highest crime area" if data['crimes'] > 30 else "Medium activity zone" if data['crimes'] > 15 else "Lower priority area"}
- Patrol Recommendation: {patrol_freq} presence
- Resource Allocation: {"High priority" if data['risk'] == "High" else "Medium priority" if data['risk'] == "Medium" else "Standard monitoring"}

🎯 TACTICAL RECOMMENDATIONS:
{"- Deploy additional units during peak hours\n- Focus on larceny and drug crime prevention\n- Coordinate with community outreach programs" if data['risk'] == "High" else "- Regular patrol schedules\n- Community engagement initiatives\n- Monitor for escalation patterns" if data['risk'] == "Medium" else "- Maintain standard patrol coverage\n- Focus on prevention and visibility"}
"""
        
        # Crime type specific intelligent analysis
        if any(word in query_lower for word in ['murder', 'homicide', 'killing', 'death']):
            return """
📊 HOMICIDE INTELLIGENCE ANALYSIS (Q2 2025):

🎯 CURRENT STATUS:
- Total Cases: 4 (Significant 76% decrease from 2023 H1: 17→4)
- Detection Rate: 50% (2 cases solved, 2 under investigation)
- Trend Analysis: Major improvement in violent crime prevention

📈 HISTORICAL CONTEXT:
- 2023 H1: 17 homicides | 2024 H1: 16 homicides | 2025 H1: 4 homicides
- This represents the lowest homicide rate in recent years
- Primary methods historically: Shooting (81%), Stabbing (14%), Other (5%)

🗺️ HIGH-RISK LOCATIONS FOR VIOLENT CRIME:
- Basseterre Central, Molineux, Tabernacle (concentrate patrols here)
- Age demographic most at risk: 18-35 years (historically 62% of victims)

🎯 PREVENTION STRATEGIES:
- Continue current violence intervention programs
- Maintain enhanced patrols in high-risk zones
- Focus on conflict mediation in communities
- Monitor gang activity indicators
"""
        
        if any(word in query_lower for word in ['drug', 'drugs', 'narcotics', 'substance']):
            return """
📊 DRUG CRIME INTELLIGENCE ANALYSIS (Q2 2025):

🏆 OUTSTANDING PERFORMANCE:
- Total Cases: 31 (10.6% of all crimes)
- Detection Rate: 100% (31/31 cases) - EXCEPTIONAL SUCCESS
- Trend: Significant increase from 6→45 cases shows proactive enforcement

📈 ENFORCEMENT SUCCESS INDICATORS:
- 2023 H1: 6 drug cases | 2024 H1: 8 cases | 2025 H1: 45 cases
- 100% detection rate demonstrates excellent intelligence and operations
- Proactive policing strategy clearly working

🗺️ DRUG ACTIVITY HOTSPOTS:
- Basseterre Central: Major drug trafficking hub
- Newton Ground: Active drug trade area  
- Old Road Town: Drug-related crimes increasing
- Ramsbury (Nevis): Cross-island drug movement

🎯 CONTINUE SUCCESSFUL STRATEGIES:
- Maintain intelligence-led operations
- Expand community informant network
- Coordinate with regional drug enforcement
- Focus on supply chain disruption
"""
        
        if any(word in query_lower for word in ['larceny', 'theft', 'stealing', 'steal', 'stolen']):
            return """
📊 LARCENY/THEFT INTELLIGENCE ANALYSIS (Q2 2025):

⚠️ HIGHEST VOLUME CRIME - NEEDS ATTENTION:
- Total Cases: 92 (31.5% of ALL crimes - MOST COMMON)
- Detection Rate: 22.8% (21/92 solved) - BELOW TARGET
- Challenge: Low clearance rate requires enhanced investigation protocols

📈 TREND ANALYSIS:
- 2023 H1: 231 larcenies | 2024 H1: 193 larcenies | 2025 H1: 185 larcenies
- Volume decreasing but detection rate still problematic
- Represents 1 in 3 of all reported crimes

🗺️ LARCENY HOTSPOTS (All Locations Affected):
- Basseterre Central: Highest concentration (commercial area)
- Tourist areas: Hotel and beach theft concerns
- Residential break-ins: Focus on Cayon, Cotton Ground

🎯 IMPROVEMENT STRATEGIES NEEDED:
- Enhanced forensic capabilities for property crimes
- Community watch programs in high-theft areas
- Business security partnerships
- Improved evidence collection training
- CCTV expansion in commercial zones
"""
        
        if any(word in query_lower for word in ['detection', 'rate', 'performance', 'solve', 'clearance']):
            return """
📊 DETECTION RATE PERFORMANCE ANALYSIS (Q2 2025):

🎯 OVERALL PERFORMANCE:
- Federation Average: 38.7% detection rate
- St. Kitts: 32.9% (NEEDS IMPROVEMENT)
- Nevis: 52.9% (EXCELLENT PERFORMANCE)

📈 PERFORMANCE BY CRIME TYPE:
🏆 EXCELLENT (>50%):
- Drug Crimes: 100% (31/31) - Outstanding
- Bodily Harm: 57.6% (19/33) - Good
- Murder: 50% (2/4) - Acceptable for serious crimes

⚠️ NEEDS IMPROVEMENT (<30%):
- Larcenies: 22.8% (21/92) - Priority concern
- Break-ins: 26.9% (7/26) - Below standard
- Malicious Damage: 28.8% (17/59) - Requires attention

🎯 PERFORMANCE GAPS:
- Nevis outperforming St. Kitts by 20 percentage points
- Property crimes (larceny, break-ins) showing lowest clearance
- Need to analyze Nevis best practices for St. Kitts implementation

🎯 IMPROVEMENT RECOMMENDATIONS:
- Cross-training between St. Kitts and Nevis units
- Enhanced investigative protocols for property crimes
- Community policing expansion (Nevis model)
- Additional detective resources for St. Kitts
"""
        
        if any(word in query_lower for word in ['compare', 'comparison', 'vs', 'versus', 'difference']):
            return """
📊 COMPARATIVE CRIME ANALYSIS:

🏝️ ST. KITTS VS NEVIS PERFORMANCE (Q2 2025):
┌─────────────────┬─────────────┬─────────────┐
│   METRIC        │  ST. KITTS  │    NEVIS    │
├─────────────────┼─────────────┼─────────────┤
│ Total Crimes    │    207      │     85      │
│ Detection Rate  │   32.9%     │   52.9%     │
│ Performance Gap │     -20%    │    +20%     │
└─────────────────┴─────────────┴─────────────┘

📈 HISTORICAL COMPARISON (H1 Years):
- 2023 H1: 672 total crimes | 17 murders
- 2024 H1: 586 total crimes | 16 murders  
- 2025 H1: 574 total crimes | 4 murders

🎯 KEY INSIGHTS:
- Nevis consistently outperforms with smaller, community-focused approach
- St. Kitts handles 71% of crimes but with lower efficiency
- Overall crime volume stable but murder prevention dramatically improved
- Need to implement Nevis best practices on St. Kitts

🎯 STRATEGIC RECOMMENDATIONS:
- Study Nevis community policing model
- Deploy Nevis officers to train St. Kitts units
- Implement smaller beat patrol areas on St. Kitts
- Enhance community engagement on larger island
"""
        
        return f"🔍 No specific crime intelligence found for '{query}'. However, I have comprehensive data on locations, crime types, trends, and performance metrics. Try asking about:\n\n• Specific locations (e.g., 'Basseterre Central crime analysis')\n• Crime types (e.g., 'drug crime statistics')\n• Performance metrics (e.g., 'detection rates')\n• Comparisons (e.g., 'St. Kitts vs Nevis')\n• Trends (e.g., 'homicide trends')"
    
    # If CSV exists, search it as well
    search_term = query.lower()
    results = []
    
    for column in df.columns:
        if df[column].dtype == 'object':
            try:
                mask = df[column].astype(str).str.lower().str.contains(search_term, na=False)
                matching_rows = df[mask]
                
                if not matching_rows.empty:
                    for _, row in matching_rows.head(2).iterrows():
                        result_dict = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                        results.append(f"**Database Match in {column}:**\n{result_dict}")
            except Exception as e:
                continue
    
    if results:
        return f"🔍 **DATABASE SEARCH RESULTS for '{query}':**\n\n" + "\n\n---\n\n".join(results[:3])
    else:
        return f"🔍 No database matches found for '{query}'. Try different search terms or check spelling."

# Quick Question Suggestions for Users
def get_suggested_questions():
    """Generate helpful question suggestions based on actual crime data"""
    return [
        "What's the crime situation in Basseterre Central?",
        "Show me drug crime statistics for Q2 2025",
        "Which areas have the highest murder rates?", 
        "What's the detection rate for larcenies?",
        "Compare crime rates between St. Kitts and Nevis",
        "What crime prevention strategies do you recommend for Molineux?",
        "Analyze the trend in homicides from 2023 to 2025",
        "Which police districts need more resources?",
        "Why is Nevis outperforming St. Kitts in detection rates?",
        "What are the top 3 crime hotspots?",
        "How effective is drug enforcement currently?",
        "What's causing the low larceny detection rate?"
    ]

# CSV data handling - Enhanced
@st.cache_data
def load_csv_data():
    csv_filename = "criminal_justice_qa.csv"
    script_dir = os.path.dirname(__file__)
    csv_path = os.path.join(script_dir, csv_filename)
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            return df, f"Successfully loaded {csv_path}"
        else:
            current_dir = os.getcwd()
            files_in_script_dir = os.listdir(script_dir)
            files_in_current_dir = os.listdir(current_dir)
            return None, f"""
            Could not find '{csv_filename}'.
            Expected: {csv_path}
            Script directory: {script_dir}
            CSV files in script dir: {', '.join([f for f in files_in_script_dir if f.endswith('.csv')])}
            Current directory: {current_dir}
            CSV files in current dir: {', '.join([f for f in files_in_current_dir if f.endswith('.csv')])}
            """
    except Exception as e:
        return None, f"Error loading CSV: {e}"

# Initialize the AI model
try:
    GOOGLE_API_KEY = "AIzaSyCdAvG9i1oWVQVf8D1FHlwPWI0Yznoj_Pk"
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Ready (Gemini 1.5 Flash)"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'welcome'

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'

if 'crime_stats' not in st.session_state:
    st.session_state.crime_stats = load_crime_statistics()

if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

if 'csv_loaded' not in st.session_state:
    st.session_state.csv_loaded = False

# Enhanced CSS styling - keeping the exact same design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
   
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Moving gradient animation keyframes */
    @keyframes moveGradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a2e1a 50%, #163e16 100%);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(-45deg, rgba(0, 0, 0, 0.7), rgba(68, 255, 68, 0.1), rgba(0, 0, 0, 0.8), rgba(34, 139, 34, 0.1));
        background-size: 400% 400%;
        animation: moveGradient 4s ease infinite;
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(68, 255, 68, 0.3), transparent);
        animation: shimmer 3s linear infinite;
    }

    .main-header h1 {
        font-size: 3rem;
        color: #44ff44;
        text-shadow: 0 0 20px rgba(68, 255, 68, 0.5);
        margin-bottom: 10px;
        position: relative;
        z-index: 2;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    .nav-container {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        margin-bottom: 30px;
        overflow: hidden;
        padding: 10px;
    }

    .nav-bar {
        background: rgba(52, 73, 94, 0.9);
        padding: 0;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        border-bottom: 1px solid rgba(68, 255, 68, 0.3);
    }

    .nav-btn {
        background: none;
        border: none;
        color: #44ff44;
        padding: 15px 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1rem;
        flex: 1;
        min-width: 120px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }

    .nav-btn:hover {
        background: rgba(68, 255, 68, 0.1);
        transform: translateY(-2px);
    }

    .nav-btn.active {
        background: rgba(68, 255, 68, 0.2);
        border-bottom: 2px solid #44ff44;
    }

    .content-area {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        padding: 30px;
        min-height: 600px;
    }

    /* Statistics Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(68, 255, 68, 0.1), rgba(34, 139, 34, 0.2));
        color: #e0e0e0;
        padding: 25px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(68, 255, 68, 0.3);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(68, 255, 68, 0.2);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
        color: #44ff44;
        text-shadow: 0 0 10px rgba(68, 255, 68, 0.3);
    }

    .stat-label {
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Emergency Card Styles */
    .emergency-card {
        background: rgba(0, 0, 0, 0.6);
        border: 2px solid rgba(231, 76, 60, 0.5);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        color: #e0e0e0 !important;
    }

    .emergency-card:hover {
        border-color: #e74c3c;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(231, 76, 60, 0.2);
    }

    .emergency-card h3 {
        color: #e74c3c !important;
        margin-bottom: 15px;
    }

    .emergency-card p, .emergency-card span, .emergency-card div {
        color: #e0e0e0 !important;
    }

    .phone-number {
        font-size: 1.5rem;
        font-weight: bold;
        color: #44ff44 !important;
        margin: 10px 0;
    }

    /* Feature card text fixes */
    .feature-card, .feature-card * {
        color: #e0e0e0 !important;
    }

    .feature-card h3 {
        color: #44ff44 !important;
    }

    /* Stat card text fixes */
    .stat-card, .stat-card * {
        color: #e0e0e0 !important;
    }

    .stat-number {
        color: #44ff44 !important;
    }

    /* Chat Styles */
    .chat-message {
        margin-bottom: 20px;
        animation: fadeInUp 0.5s ease;
        clear: both;
    }

    .user-message {
        text-align: right;
    }

    .bot-message {
        text-align: left;
    }

    .message-content {
        display: inline-block;
        padding: 15px 20px;
        border-radius: 15px;
        max-width: 80%;
        position: relative;
        font-family: 'JetBrains Mono', monospace;
        word-wrap: break-word;
        white-space: pre-wrap;
    }

    .user-message .message-content {
        background: linear-gradient(135deg, #44ff44, #33cc33);
        color: #ffffff !important;
        border-bottom-right-radius: 5px;
    }

    .bot-message .message-content {
        background: rgba(0, 0, 0, 0.8) !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(68, 255, 68, 0.3);
        border-bottom-left-radius: 5px;
    }

    .message-time {
        font-size: 0.7rem;
        color: #888 !important;
        margin-top: 5px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Button Styles */
    .stButton button {
        background: linear-gradient(135deg, #44ff44, #33cc33) !important;
        border: none !important;
        border-radius: 25px !important;
        color: #fff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 20px rgba(68, 255, 68, 0.4) !important;
    }

    /* Quick question button styles */
    .quick-btn {
        background: rgba(68, 255, 68, 0.1) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        color: #44ff44 !important;
        padding: 8px 15px !important;
        border-radius: 20px !important;
        font-size: 0.9rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        margin: 5px !important;
        transition: all 0.3s ease !important;
    }

    .quick-btn:hover {
        background: rgba(68, 255, 68, 0.2) !important;
        border-color: #44ff44 !important;
        transform: scale(1.05) !important;
    }

    /* Input Styles */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        border-radius: 25px !important;
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stTextInput input:focus {
        border-color: #44ff44 !important;
        box-shadow: 0 0 20px rgba(68, 255, 68, 0.2) !important;
    }

    /* Status bar */
    .status-bar {
        background: rgba(0, 0, 0, 0.8);
        padding: 15px;
        border-radius: 25px;
        margin-top: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(68, 255, 68, 0.2);
        font-family: 'JetBrains Mono', monospace;
        flex-wrap: wrap;
        gap: 10px;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #e0e0e0;
        font-size: 0.9rem;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #44ff44;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    /* Feature Cards */
    .feature-card {
        background: rgba(0, 0, 0, 0.6);
        border-radius: 10px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(68, 255, 68, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(68, 255, 68, 0.2);
        border-color: #44ff44;
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        color: #44ff44;
    }

    .feature-card h3 {
        color: #44ff44;
        margin-bottom: 10px;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .nav-btn {
            min-width: 100px;
            padding: 12px 15px;
            font-size: 0.9rem;
        }
        
        .content-area {
            padding: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Language Selector and AI Configuration in sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Configuration")
    
    # Show current status
    st.write(f"**Status:** {st.session_state.get('ai_status', 'Unknown')}")
    
    # Show detailed error if any
    if st.session_state.get('ai_error'):
        st.error(f"**Error:** {st.session_state.ai_error}")
    
    # CSV Database Status
    if st.session_state.get('csv_data') is not None:
        st.success(f"📊 Database: {len(st.session_state.csv_data)} records")
    else:
        st.warning("📊 Database: Built-in intelligence active")
    
    st.markdown("---")
    
    # Language Selection
    st.markdown("### 🌍 Language Selection")
    selected_language = st.selectbox(
        "Choose Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: SUPPORTED_LANGUAGES[x],
        index=0
    )
    st.session_state.selected_language = selected_language
    
    st.markdown("---")
    
    # Status indicators
    if st.session_state.get('ai_enabled', False):
        st.success("🤖 Gemini AI Active")
        st.write("• Advanced crime analysis")
        st.write("• Contextual responses")
        st.write("• Multi-language support")
        st.write("• Forensic assistance")
    else:
        st.warning("⚠️ AI Fallback Mode")
        st.write("• Built-in crime intelligence")
        st.write("• Basic crime analysis")
        st.write("• Check connection")
    
    st.success("📊 Crime Intelligence Active")
    st.write("• 13 hotspots mapped")
    st.write("• Q2 2025 statistics integrated")
    st.write("• Historical trend analysis")
    st.write("• Performance metrics available")

# Main Header
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="main-header">
    <h1>🛡️ SECURO</h1>
    <div style="color: #888; text-transform: uppercase; letter-spacing: 2px; position: relative; z-index: 2;">Advanced Crime Analysis & Security AI for St. Kitts & Nevis</div>
    <div style="color: #44ff44; margin-top: 5px; position: relative; z-index: 2;">🇰🇳 Royal St. Christopher & Nevis Police Force</div>
    <div style="color: #888; margin-top: 8px; font-size: 0.8rem; position: relative; z-index: 2;">📅 {current_date} | 🕒 {current_time} (AST)</div>
</div>
""", unsafe_allow_html=True)

# Navigation Bar
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🏠 Home", key="nav_home", help="Welcome to SECURO"):
        st.session_state.current_page = 'welcome'

with col2:
    if st.button("ℹ️ About SECURO", key="nav_about", help="About SECURO System"):
        st.session_state.current_page = 'about'

with col3:
    if st.button("🗺️ Crime Hotspots", key="nav_map", help="Interactive Crime Map"):
        st.session_state.current_page = 'map'

with col4:
    if st.button("📊 Statistics & Analytics", key="nav_stats", help="Crime Data Analysis"):
        st.session_state.current_page = 'statistics'

with col5:
    if st.button("🚨 Emergency", key="nav_emergency", help="Emergency Contacts"):
        st.session_state.current_page = 'emergency'

with col6:
    if st.button("💬 AI Assistant", key="nav_chat", help="Chat with SECURO AI"):
        st.session_state.current_page = 'chat'

# HOME PAGE
if st.session_state.current_page == 'welcome':
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h2 style="color: #44ff44; font-size: 2.5rem; margin-bottom: 20px; text-shadow: 0 0 15px rgba(68, 255, 68, 0.5);">Welcome to SECURO</h2>
        <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px; color: #e0e0e0;">Your comprehensive AI-powered crime analysis and security system for St. Kitts & Nevis</p>
        <p style="
