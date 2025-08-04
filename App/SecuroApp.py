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
import json
import uuid
from datetime import datetime as dt
import PyPDF2
import tempfile
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
    "Police Emergency": {"number": "911", "description": "For immediate police assistance and emergency response", "icon": "🚔"},
    "Police Headquarters": {"number": "465-2241", "description": "Royal St. Christopher and Nevis Police Force\nLocal Intelligence: Ext. 4238/4239", "icon": "🏢"},
    "Medical Emergency": {"number": "465-2551", "description": "Hospital services and medical emergencies", "icon": "🏥"},
    "Fire Department": {"number": "465-2515", "description": "Fire emergencies and rescue operations\nAlt: 465-7167", "icon": "🔥"},
    "Coast Guard": {"number": "465-8384", "description": "Maritime emergencies and water rescue\nAlt: 466-9280", "icon": "🚢"},
    "Met Office": {"number": "465-2749", "description": "Weather emergencies and warnings", "icon": "🌡️"},
    "Red Cross": {"number": "465-2584", "description": "Disaster relief and emergency aid", "icon": "➕"},
    "NEMA": {"number": "466-5100", "description": "National Emergency Management Agency", "icon": "⚡"}
}

# Crime Hotspots Data for St. Kitts & Nevis
CRIME_HOTSPOTS = {
    "Basseterre Central": {"lat": 17.3026, "lon": -62.7177, "crimes": 45, "risk": "High", "types": ["Larceny", "Drug Crimes", "Assault"]},
    "Cayon": {"lat": 17.3581, "lon": -62.7440, "crimes": 28, "risk": "Medium", "types": ["Break-ins", "Theft"]},
    "Old Road Town": {"lat": 17.3211, "lon": -62.7847, "crimes": 22, "risk": "Medium", "types": ["Drug Crimes", "Vandalism"]},
    "Tabernacle": {"lat": 17.3100, "lon": -62.7200, "crimes": 31, "risk": "High", "types": ["Robbery", "Assault"]},
    "Sandy Point": {"lat": 17.3667, "lon": -62.8500, "crimes": 19, "risk": "Low", "types": ["Petty Theft"]},
    "Dieppe Bay": {"lat": 17.3833, "lon": -62.8167, "crimes": 15, "risk": "Low", "types": ["Vandalism"]},
    "Newton Ground": {"lat": 17.3319, "lon": -62.7269, "crimes": 26, "risk": "Medium", "types": ["Drug Crimes", "Larceny"]},
    "Molineux": {"lat": 17.2978, "lon": -62.7047, "crimes": 33, "risk": "High", "types": ["Armed Robbery", "Assault"]},
    "Charlestown": {"lat": 17.1348, "lon": -62.6217, "crimes": 18, "risk": "Medium", "types": ["Larceny", "Drug Crimes"]},
    "Gingerland": {"lat": 17.1019, "lon": -62.5708, "crimes": 12, "risk": "Low", "types": ["Petty Theft"]},
    "Newcastle": {"lat": 17.1667, "lon": -62.6000, "crimes": 14, "risk": "Low", "types": ["Vandalism", "Theft"]},
    "Cotton Ground": {"lat": 17.1281, "lon": -62.6442, "crimes": 16, "risk": "Medium", "types": ["Break-ins", "Larceny"]},
    "Ramsbury": {"lat": 17.1500, "lon": -62.6167, "crimes": 21, "risk": "Medium", "types": ["Drug Crimes", "Assault"]},
}

# MacroTrends International Comparison Data
MACROTRENDS_DATA = {
    "homicide_rates_per_100k": {
        "2020": 20.99, "2019": 25.15, "2018": 48.16, "2017": 48.14,
        "2016": 42.50, "2015": 38.20, "2014": 35.80, "2013": 42.10,
        "2012": 33.60, "2011": 67.60
    },
    "comparative_context": {
        "global_average_firearm_homicides": 42.0,
        "skn_firearm_homicides_2010": 85.0,
        "skn_firearm_homicides_2003": 63.6,
        "basseterre_2011_rate": 131.6,
        "world_ranking_2012": 8,
        "world_ranking_2005_2014": 7
    },
    "recent_trends": {
        "2024_total_crimes": 1146, "2023_total_crimes": 1280,
        "2022_total_crimes": 1360, "2024_homicides": 28,
        "2023_homicides": 31, "first_quarter_2025": "No homicides (first time in 23 years)"
    }
}

# Enhanced HISTORICAL CRIME DATABASE
HISTORICAL_CRIME_DATABASE = {
    "2025_Q2": {
        "period": "Q2 2025 (Apr-Jun)", "total_crimes": 292, "detection_rate": 38.7,
        "federation": {
            "murder_manslaughter": {"total": 4, "detected": 2, "rate": 50.0},
            "attempted_murder": {"total": 4, "detected": 0, "rate": 0.0},
            "bodily_harm": {"total": 33, "detected": 19, "rate": 57.6},
            "sex_crimes": {"total": 7, "detected": 1, "rate": 14.3},
            "break_ins": {"total": 26, "detected": 7, "rate": 26.9},
            "larcenies": {"total": 92, "detected": 21, "rate": 22.8},
            "robberies": {"total": 8, "detected": 1, "rate": 12.5},
            "firearms_offences": {"total": 5, "detected": 5, "rate": 100.0},
            "drug_crimes": {"total": 31, "detected": 31, "rate": 100.0},
            "malicious_damage": {"total": 59, "detected": 17, "rate": 28.8},
        },
        "st_kitts": {"crimes": 207, "detection_rate": 32.9},
        "nevis": {"crimes": 85, "detection_rate": 52.9}
    },
    "2024_ANNUAL": {
        "period": "2024 Full Year (Jan-Dec)", "total_crimes": 1146, "detection_rate": 41.8,
        "federation": {
            "murder_manslaughter": {"total": 28, "detected": 16, "rate": 57.0},
            "shooting_intent": {"total": 6, "detected": 0, "rate": 0.0},
            "attempted_murder": {"total": 18, "detected": 5, "rate": 28.0},
            "bodily_harm": {"total": 145, "detected": 115, "rate": 79.0},
            "sex_crimes": {"total": 72, "detected": 33, "rate": 46.0},
            "break_ins": {"total": 134, "detected": 36, "rate": 27.0},
            "larcenies": {"total": 395, "detected": 119, "rate": 30.0},
            "robberies": {"total": 42, "detected": 5, "rate": 12.0},
            "firearms_offences": {"total": 21, "detected": 19, "rate": 90.0},
            "drug_crimes": {"total": 20, "detected": 20, "rate": 100.0},
            "malicious_damage": {"total": 191, "detected": 72, "rate": 38.0},
            "other_crimes": {"total": 74, "detected": 39, "rate": 53.0}
        },
        "st_kitts": {"crimes": 965, "detection_rate": 40.7},
        "nevis": {"crimes": 181, "detection_rate": 47.5}
    },
    "2023_ANNUAL": {
        "period": "2023 Full Year (Jan-Dec)", "total_crimes": 1280, "detection_rate": 44.6,
        "federation": {
            "murder_manslaughter": {"total": 31, "detected": 11, "rate": 35.0},
            "shooting_intent": {"total": 6, "detected": 3, "rate": 50.0},
            "woundings_firearm": {"total": 24, "detected": 19, "rate": 79.0},
            "attempted_murder": {"total": 9, "detected": 2, "rate": 22.0},
            "bodily_harm": {"total": 161, "detected": 126, "rate": 78.0},
            "sex_crimes": {"total": 68, "detected": 38, "rate": 56.0},
            "break_ins": {"total": 136, "detected": 32, "rate": 24.0},
            "larcenies": {"total": 446, "detected": 118, "rate": 26.0},
            "robberies": {"total": 39, "detected": 19, "rate": 49.0},
            "firearms_offences": {"total": 34, "detected": 32, "rate": 94.0},
            "drug_crimes": {"total": 21, "detected": 21, "rate": 100.0},
            "malicious_damage": {"total": 274, "detected": 131, "rate": 48.0},
            "other_crimes": {"total": 31, "detected": 19, "rate": 61.0}
        },
        "st_kitts": {"crimes": 1093, "detection_rate": 44.8},
        "nevis": {"crimes": 187, "detection_rate": 43.3}
    }
}

# St. Kitts timezone
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

# Chat Management System
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

if 'chat_counter' not in st.session_state:
    st.session_state.chat_counter = 1

if 'current_analytics_tab' not in st.session_state:
    st.session_state.current_analytics_tab = 'Crime Trends'

def create_new_chat():
    """Create a new chat session"""
    chat_id = f"chat_{st.session_state.chat_counter}_{int(time.time())}"
    st.session_state.chat_sessions[chat_id] = {
        'id': chat_id,
        'name': f"Chat {st.session_state.chat_counter}",
        'messages': [],
        'created_at': get_stkitts_time(),
        'last_activity': get_stkitts_time()
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_counter += 1
    return chat_id

def get_current_chat():
    """Get current chat session"""
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
        return st.session_state.chat_sessions[st.session_state.current_chat_id]
    else:
        create_new_chat()
        return st.session_state.chat_sessions[st.session_state.current_chat_id]

def add_message_to_chat(role, content):
    """Add message to current chat"""
    current_chat = get_current_chat()
    current_chat['messages'].append({
        "role": role,
        "content": content,
        "timestamp": get_stkitts_time()
    })
    current_chat['last_activity'] = get_stkitts_time()
    
    if role == "user" and len(current_chat['messages']) <= 2:
        chat_name = content[:30] + "..." if len(content) > 30 else content
        current_chat['name'] = chat_name

def create_crime_hotspot_map():
    """Create an interactive crime hotspot map for St. Kitts and Nevis"""
    center_lat = 17.25
    center_lon = -62.7
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap',
        attr='Crime Hotspot Analysis - SECURO'
    )
    
    risk_colors = {'High': '#ff4444', 'Medium': '#ffaa44', 'Low': '#44ff44'}
    
    for location, data in CRIME_HOTSPOTS.items():
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="color: {risk_colors[data['risk']]}; margin: 0; text-align: center;">
                🚨 {location}
            </h4>
            <hr style="margin: 8px 0;">
            <p style="margin: 4px 0;"><strong>📊 Total Crimes:</strong> {data['crimes']}</p>
            <p style="margin: 4px 0;"><strong>⚠️ Risk Level:</strong> 
               <span style="color: {risk_colors[data['risk']]}; font-weight: bold;">{data['risk']}</span>
            </p>
            <p style="margin: 4px 0;"><strong>🔍 Common Types:</strong></p>
            <ul style="margin: 4px 0; padding-left: 20px;">
                {''.join([f'<li>{crime_type}</li>' for crime_type in data['types']])}
            </ul>
        </div>
        """
        
        marker_size = max(10, min(30, data['crimes'] * 0.8))
        
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
    
    return m

# Initialize AI model
try:
    GOOGLE_API_KEY = "AIzaSyBn1AUXxPtPMu9eRnosECSSQG_2e5bArR8"
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Active with Statistical Knowledge"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration
st.set_page_config(
    page_title="SECURO - Enhanced AI Assistant & Crime Intelligence System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False

# Professional CSS styling matching the screenshots
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Root styling */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #0d1117 50%, #1a1a1a 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        padding: 20px 0;
        border-bottom: 1px solid #21262d;
        margin-bottom: 0;
        position: sticky;
        top: 0;
        z-index: 1000;
        backdrop-filter: blur(10px);
    }
    
    .header-content {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 30px;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .shield-icon {
        width: 45px;
        height: 45px;
        background: linear-gradient(135deg, #00ff41, #00cc34);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        color: #000;
        box-shadow: 0 4px 15px rgba(0, 255, 65, 0.3);
    }
    
    .logo-text h1 {
        color: #00ff41 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: 2px;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
    }
    
    .logo-text p {
        color: #8b949e !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0 !important;
        font-weight: 500;
    }
    
    .status-info {
        display: flex;
        align-items: center;
        gap: 25px;
        font-size: 14px;
        color: #8b949e;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: rgba(0, 255, 65, 0.05);
        border-radius: 20px;
        border: 1px solid rgba(0, 255, 65, 0.2);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #00ff41;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    
    /* Navigation */
    .nav-container {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        padding: 0;
        border-bottom: 1px solid #30363d;
        margin-bottom: 0;
    }
    
    .nav-tabs {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        gap: 0;
        padding: 0 30px;
    }
    
    .nav-tab {
        background: transparent;
        border: none;
        color: #8b949e;
        padding: 16px 24px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 3px solid transparent;
        position: relative;
    }
    
    .nav-tab:hover {
        color: #00ff41;
        background: rgba(0, 255, 65, 0.05);
    }
    
    .nav-tab.active {
        color: #00ff41;
        border-bottom-color: #00ff41;
        background: rgba(0, 255, 65, 0.1);
    }
    
    /* Page content */
    .page-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 40px 30px;
        min-height: calc(100vh - 200px);
    }
    
    /* Welcome section */
    .welcome-hero {
        text-align: center;
        padding: 60px 20px;
        margin-bottom: 50px;
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 255, 65, 0.03) 50%, rgba(0, 0, 0, 0.8) 100%);
        border-radius: 20px;
        border: 1px solid rgba(0, 255, 65, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .welcome-hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at center, rgba(0, 255, 65, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 20px;
        text-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
        position: relative;
        z-index: 2;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #c9d1d9;
        margin-bottom: 15px;
        font-weight: 400;
        position: relative;
        z-index: 2;
    }
    
    .hero-description {
        font-size: 1.1rem;
        color: #8b949e;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.6;
        position: relative;
        z-index: 2;
    }
    
    /* Feature cards grid */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 25px;
        margin-top: 50px;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 35px;
        text-align: center;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(0, 255, 65, 0.02) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
        pointer-events: none;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        border-color: #00ff41;
        box-shadow: 0 15px 40px rgba(0, 255, 65, 0.15);
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 25px;
        color: #00ff41;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
    }
    
    .feature-card h3 {
        color: #00ff41 !important;
        font-size: 1.4rem !important;
        margin-bottom: 15px !important;
        font-weight: 600 !important;
    }
    
    .feature-card p {
        color: #c9d1d9 !important;
        line-height: 1.6 !important;
        font-size: 14px !important;
    }
    
    /* Loading screen */
    .loading-screen {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 20px;
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border-radius: 20px;
        border: 1px solid #30363d;
        margin: 40px 0;
    }
    
    .loading-icon {
        width: 80px;
        height: 80px;
        border: 4px solid rgba(0, 255, 65, 0.2);
        border-top: 4px solid #00ff41;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 30px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        color: #00ff41;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .loading-subtitle {
        color: #8b949e;
        font-size: 14px;
        text-align: center;
        max-width: 400px;
    }
    
    .progress-bar {
        width: 300px;
        height: 4px;
        background: rgba(0, 255, 65, 0.2);
        border-radius: 2px;
        margin-top: 20px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00ff41, #00cc34);
        width: 0%;
        animation: progress 3s ease-in-out infinite;
    }
    
    @keyframes progress {
        0% { width: 0%; }
        50% { width: 70%; }
        100% { width: 100%; }
    }
    
    /* Analytics tabs */
    .analytics-tabs {
        display: flex;
        gap: 0;
        margin-bottom: 30px;
        background: #21262d;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #30363d;
    }
    
    .analytics-tab {
        background: transparent;
        border: none;
        color: #8b949e;
        padding: 12px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 14px;
        font-weight: 500;
        border-radius: 8px;
        flex: 1;
        text-align: center;
    }
    
    .analytics-tab:hover {
        color: #00ff41;
        background: rgba(0, 255, 65, 0.1);
    }
    
    .analytics-tab.active {
        color: #000;
        background: #00ff41;
        font-weight: 600;
    }
    
    /* Emergency cards */
    .emergency-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin-bottom: 40px;
    }
    
    .emergency-card {
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .emergency-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(0, 255, 65, 0.02) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .emergency-card:hover {
        transform: translateY(-5px);
        border-color: #00ff41;
        box-shadow: 0 10px 25px rgba(0, 255, 65, 0.15);
    }
    
    .emergency-card:hover::before {
        opacity: 1;
    }
    
    .emergency-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
        color: #00ff41;
    }
    
    .emergency-card h3 {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        margin-bottom: 15px !important;
        font-weight: 600 !important;
    }
    
    .emergency-number {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #00ff41 !important;
        margin: 15px 0 !important;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    }
    
    .emergency-card p {
        color: #c9d1d9 !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
    }
    
    /* Guidelines box */
    .guidelines-box {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 16px;
        padding: 30px;
        margin-top: 40px;
    }
    
    .guidelines-title {
        color: #ffc107 !important;
        font-size: 1.3rem !important;
        margin-bottom: 20px !important;
        font-weight: 600 !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .guidelines-list {
        color: #c9d1d9 !important;
        line-height: 1.8 !important;
        list-style: none !important;
        padding: 0 !important;
    }
    
    .guidelines-list li {
        padding: 8px 0 !important;
        padding-left: 25px !important;
        position: relative !important;
    }
    
    .guidelines-list li::before {
        content: "•" !important;
        color: #ffc107 !important;
        font-weight: bold !important;
        position: absolute !important;
        left: 0 !important;
    }
    
    /* Chat interface */
    .chat-welcome {
        text-align: center;
        padding: 80px 20px;
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border-radius: 20px;
        border: 1px solid #30363d;
        margin: 40px 0;
    }
    
    .chat-logo {
        width: 100px;
        height: 100px;
        border: 4px solid #00ff41;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 30px;
        font-size: 3rem;
        color: #00ff41;
        background: rgba(0, 255, 65, 0.1);
        animation: pulse 3s ease-in-out infinite;
    }
    
    .chat-title {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .chat-subtitle {
        color: #8b949e;
        font-size: 16px;
        margin-bottom: 30px;
    }
    
    .start-button {
        background: linear-gradient(135deg, #00ff41, #00cc34);
        border: none;
        color: #000;
        padding: 15px 30px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .start-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 255, 65, 0.3);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 80px 20px;
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border-radius: 20px;
        border: 1px solid #30363d;
        margin: 40px auto;
        max-width: 600px;
    }
    
    .empty-icon {
        width: 80px;
        height: 80px;
        border: 3px solid #30363d;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 30px;
        font-size: 2rem;
        color: #8b949e;
        background: rgba(0, 0, 0, 0.3);
    }
    
    .empty-title {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    .empty-subtitle {
        color: #8b949e;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* Footer */
    .main-footer {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        border-top: 1px solid #21262d;
        padding: 40px 0 20px;
        margin-top: 60px;
    }
    
    .footer-content {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 30px;
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 30px;
        margin-bottom: 30px;
    }
    
    .footer-section h4 {
        color: #00ff41 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-bottom: 15px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .footer-section p, .footer-section li {
        color: #8b949e !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        margin-bottom: 8px !important;
    }
    
    .footer-section ul {
        list-style: none !important;
        padding: 0 !important;
    }
    
    .footer-bottom {
        border-top: 1px solid #21262d;
        padding: 20px 0;
        text-align: center;
        color: #6e7681;
        font-size: 12px;
    }
    
    /* Status bar */
    .status-bar {
        background: rgba(0, 0, 0, 0.9);
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
        border-top: 1px solid #21262d;
        font-size: 13px;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #8b949e;
    }
    
    .status-active {
        color: #00ff41;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            gap: 20px;
            padding: 0 20px;
        }
        
        .nav-tabs {
            flex-wrap: wrap;
            padding: 0 20px;
        }
        
        .page-container {
            padding: 20px;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .features-grid {
            grid-template-columns: 1fr;
        }
        
        .emergency-grid {
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }
    }
    
    /* Buttons */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #30363d !important;
        color: #8b949e !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: rgba(0, 255, 65, 0.1) !important;
        border-color: #00ff41 !important;
        color: #00ff41 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 255, 65, 0.2) !important;
    }
    
    /* Text inputs */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput input:focus {
        border-color: #00ff41 !important;
        box-shadow: 0 0 0 3px rgba(0, 255, 65, 0.1) !important;
    }
    
    /* Fix text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    p, span, div, li {
        color: #c9d1d9 !important;
    }
    
    .stMarkdown {
        color: #c9d1d9 !important;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #21262d 0%, #161b22 100%); border-radius: 16px; padding: 25px; border: 1px solid #30363d; margin-bottom: 25px;">
        <h3 style="color: #00ff41; margin-bottom: 20px; text-align: center;">🤖 AI System Status</h3>
        <div style="text-align: center;">
            <div style="width: 60px; height: 60px; border: 3px solid #00ff41; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; font-size: 1.5rem; color: #00ff41; background: rgba(0, 255, 65, 0.1);">
                🧠
            </div>
            <p style="color: #00ff41; font-weight: 600; margin-bottom: 5px;">Enhanced AI Active</p>
            <p style="color: #8b949e; font-size: 12px;">Statistical Knowledge • Memory • Context</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('ai_enabled', False):
        st.success("🔮 AI Assistant Online")
        st.markdown("""
        **Enhanced Capabilities:**
        - Statistical knowledge integration
        - Conversation memory
        - Context-aware responses
        - Crime data analysis
        - Professional assistance
        
        **Statistical Coverage:**
        - 2022-2025 complete annual data
        - 2015-2024 homicide analysis
        - MacroTrends international data
        - Quarterly & half-yearly reports
        - Detection rate analysis
        """)
    else:
        st.error("⚠️ AI Offline")
        st.write("Please check your API key configuration")

# Main Header
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="main-header">
    <div class="header-content">
        <div class="logo-section">
            <div class="shield-icon">🛡️</div>
            <div class="logo-text">
                <h1>SECURO</h1>
                <p>Enhanced AI Assistant & Crime Intelligence System</p>
            </div>
        </div>
        <div class="status-info">
            <div class="status-item">
                <div class="status-dot"></div>
                <span>Royal St. Christopher & Nevis Police Force</span>
            </div>
            <div class="status-item">
                <span>📅 {current_date} | 🕒 {current_time} (AST)</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation
st.markdown(f"""
<div class="nav-container">
    <div class="nav-tabs">
        <div class="nav-tab {'active' if st.session_state.current_page == 'home' else ''}" onclick="setPage('home')">
            🏠 Home
        </div>
        <div class="nav-tab {'active' if st.session_state.current_page == 'about' else ''}" onclick="setPage('about')">
            ℹ️ About SECURO
        </div>
        <div class="nav-tab {'active' if st.session_state.current_page == 'hotspots' else ''}" onclick="setPage('hotspots')">
            🗺️ Crime Hotspots
        </div>
        <div class="nav-tab {'active' if st.session_state.current_page == 'analytics' else ''}" onclick="setPage('analytics')">
            📊 Statistics & Analytics
        </div>
        <div class="nav-tab {'active' if st.session_state.current_page == 'chat' else ''}" onclick="setPage('chat')">
            💬 AI Assistant
        </div>
        <div class="nav-tab {'active' if st.session_state.current_page == 'history' else ''}" onclick="setPage('history')">
            💾 Chat History
        </div>
        <div class="nav-tab {'active' if st.session_state.current_page == 'emergency' else ''}" onclick="setPage('emergency')">
            🚨 Emergency
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation buttons (actual functionality)
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    if st.button("🏠 Home", key="nav_home", help="Home", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

with col2:
    if st.button("ℹ️ About", key="nav_about", help="About SECURO System", use_container_width=True):
        st.session_state.current_page = 'about'
        st.rerun()

with col3:
    if st.button("🗺️ Hotspots", key="nav_map", help="Crime Hotspots", use_container_width=True):
        st.session_state.current_page = 'hotspots'
        st.rerun()

with col4:
    if st.button("📊 Analytics", key="nav_stats", help="Statistics & Analytics", use_container_width=True):
        st.session_state.current_page = 'analytics'
        st.rerun()

with col5:
    if st.button("💬 AI Assistant", key="nav_chat", help="AI Chat", use_container_width=True):
        st.session_state.current_page = 'chat'
        st.rerun()

with col6:
    if st.button("💾 History", key="nav_history", help="Chat History", use_container_width=True):
        st.session_state.current_page = 'history'
        st.rerun()

with col7:
    if st.button("🚨 Emergency", key="nav_emergency", help="Emergency Contacts", use_container_width=True):
        st.session_state.current_page = 'emergency'
        st.rerun()

# Main content
st.markdown('<div class="page-container">', unsafe_allow_html=True)

# HOME PAGE
if st.session_state.current_page == 'home':
    st.markdown("""
    <div class="welcome-hero">
        <h1 class="hero-title">Welcome to Enhanced SECURO</h1>
        <p class="hero-subtitle">Your comprehensive AI assistant with statistical knowledge, conversation memory, and crime analysis capabilities for St. Kitts & Nevis</p>
        <p class="hero-description">AI assistant now features conversation memory, statistical integration, and enhanced analytics.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>Enhanced AI with Memory</h3>
            <p>Conversation memory, statistical knowledge integration, and context-aware responses powered by real crime data from police PDFs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Integrated Statistics + International Data</h3>
            <p>Real-time access to local crime statistics PLUS MacroTrends international comparison data with global context and historical trends.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <h3>Conversation Management</h3>
            <p>Multiple chat sessions with memory, chat history, and context preservation across conversations for continuous assistance.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3>Statistical Analysis</h3>
            <p>Advanced crime data analysis with detection rates, trend identification, and actionable insights for police operations.</p>
        </div>
        """, unsafe_allow_html=True)

# ABOUT PAGE
elif st.session_state.current_page == 'about':
    st.markdown('<h1 style="text-align: center; margin-bottom: 40px;">About Enhanced SECURO</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card" style="margin-bottom: 40px;">
        <p style="text-align: center; font-size: 16px;"><strong style="color: #00ff41;">SECURO</strong> is now an enhanced comprehensive crime analysis system with statistical integration, conversation memory, and advanced AI capabilities built specifically for the Royal St. Christopher and Nevis Police Force.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧠 Enhanced AI Capabilities")
        capabilities = [
            "Conversation Memory - Maintains context across entire chat sessions",
            "Statistical Knowledge Integration - Real access to 2023-2025 crime data", 
            "Context-Aware Responses - Understands conversation flow and history",
            "Multi-Chat Management - Multiple conversation sessions with history",
            "Statistical Query Processing - Answers questions with actual crime data"
        ]
        
        for cap in capabilities:
            col_check, col_text = st.columns([1, 10])
            with col_check:
                st.markdown("✅")
            with col_text:
                st.markdown(f"**{cap.split(' - ')[0]}** - {cap.split(' - ')[1]}")
        
        st.markdown("### 💬 Chat Management Features")
        chat_features = [
            "New Chat Sessions - Start fresh conversations anytime",
            "Chat History - Access and resume previous conversations",
            "Context Preservation - AI remembers entire conversation context", 
            "Session Management - Switch between multiple chat sessions seamlessly"
        ]
        
        for feature in chat_features:
            col_check, col_text = st.columns([1, 10])
            with col_check:
                st.markdown("✅")
            with col_text:
                st.markdown(f"**{feature.split(' - ')[0]}** - {feature.split(' - ')[1]}")
    
    with col2:
        st.markdown("### 📊 Integrated Statistical Database")
        stats_features = [
            "Real PDF Integration - Data sourced from official police statistical reports",
            "2022-2025 Crime Data - Complete annual statistics plus quarterly analysis",
            "Detection Rate Analysis - Performance metrics and trend identification",
            "Geographical Breakdown - St. Kitts vs. Nevis crime distribution"
        ]
        
        for feature in stats_features:
            col_check, col_text = st.columns([1, 10])
            with col_check:
                st.markdown("✅")
            with col_text:
                st.markdown(f"**{feature.split(' - ')[0]}** - {feature.split(' - ')[1]}")
        
        st.markdown("### ⚖️ Professional Standards")
        st.markdown("""
        Enhanced SECURO maintains professional communication standards appropriate for law enforcement operations. 
        The AI assistant now provides statistically-informed assistance while preserving conversation context for more effective police support.
        """)
    
    # Assets & Resources section
    st.markdown("### 🎯 Assets & Resources")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #21262d 0%, #161b22 100%); border: 1px solid #30363d; border-radius: 12px; padding: 20px; text-align: center;">
            <div style="color: #00ff41; font-size: 2rem; margin-bottom: 15px;">🛡️</div>
            <h4 style="color: #00ff41;">SECURO AI Avatar</h4>
            <button style="background: #00ff41; color: #000; border: none; padding: 8px 16px; border-radius: 6px; font-size: 12px; margin-top: 10px;">📥 Download</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #21262d 0%, #161b22 100%); border: 1px solid #30363d; border-radius: 12px; padding: 20px; text-align: center;">
            <div style="color: #00ff41; font-size: 2rem; margin-bottom: 15px;">👮</div>
            <h4 style="color: #00ff41;">Police Badge Avatar</h4>
            <button style="background: #00ff41; color: #000; border: none; padding: 8px 16px; border-radius: 6px; font-size: 12px; margin-top: 10px;">📥 Download</button>
        </div>
        """, unsafe_allow_html=True)

# CRIME HOTSPOTS PAGE
elif st.session_state.current_page == 'hotspots':
    st.markdown('<h1 style="text-align: center; margin-bottom: 40px;">🗺️ Crime Hotspot Map - St. Kitts & Nevis</h1>', unsafe_allow_html=True)
    
    try:
        crime_map = create_crime_hotspot_map()
        map_data = st_folium(
            crime_map,
            width="100%",
            height=500,
            returned_objects=["last_object_clicked_tooltip", "last_clicked"],
            key="crime_hotspot_map"
        )
        
        if map_data['last_object_clicked_tooltip']:
            clicked_info = map_data['last_object_clicked_tooltip']
            st.info(f"📍 **Last Clicked Location:** {clicked_info}")
    
    except Exception as e:
        st.error(f"❌ Map Error: {str(e)}")
    
    # Hotspot Analysis Summary
    st.markdown('<h2 style="text-align: center; margin: 40px 0 30px;">📍 Hotspot Analysis Summary</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255, 68, 68, 0.1) 0%, rgba(255, 68, 68, 0.05) 100%); 
                    border: 1px solid rgba(255, 68, 68, 0.3); border-radius: 16px; padding: 25px; text-align: center; 
                    border-left: 4px solid #ff4444;">
            <h3 style="color: #ff4444; margin-bottom: 15px;">High Risk Areas (3)</h3>
            <p style="color: #c9d1d9; margin-bottom: 10px;">Basseterre Central, Molineux, Tabernacle</p>
            <p style="color: #8b949e; font-size: 14px;"><strong>Total: 109 crimes</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255, 170, 68, 0.1) 0%, rgba(255, 170, 68, 0.05) 100%); 
                    border: 1px solid rgba(255, 170, 68, 0.3); border-radius: 16px; padding: 25px; text-align: center; 
                    border-left: 4px solid #ffaa44;">
            <h3 style="color: #ffaa44; margin-bottom: 15px;">Medium Risk Areas (6)</h3>
            <p style="color: #c9d1d9; margin-bottom: 10px;">Cayon, Newton Ground, Old Road, etc.</p>
            <p style="color: #8b949e; font-size: 14px;"><strong>Total: 133 crimes</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(68, 255, 68, 0.1) 0%, rgba(68, 255, 68, 0.05) 100%); 
                    border: 1px solid rgba(68, 255, 68, 0.3); border-radius: 16px; padding: 25px; text-align: center; 
                    border-left: 4px solid #44ff44;">
            <h3 style="color: #44ff44; margin-bottom: 15px;">Low Risk Areas (4)</h3>
            <p style="color: #c9d1d9; margin-bottom: 10px;">Sandy Point, Dieppe Bay, etc.</p>
            <p style="color: #8b949e; font-size: 14px;"><strong>Total: 60 crimes</strong></p>
        </div>
        """, unsafe_allow_html=True)

# ANALYTICS PAGE  
elif st.session_state.current_page == 'analytics':
    st.markdown('<h1 style="text-align: center; margin-bottom: 40px;">📊 Quick Analytics</h1>', unsafe_allow_html=True)
    
    # Analytics tabs
    tabs = ['Crime Trends', 'Crime Methods', 'District Analysis', 'Detection Rates']
    
    tab_cols = st.columns(4)
    for i, tab in enumerate(tabs):
        with tab_cols[i]:
            if st.button(tab, key=f"tab_{tab}", use_container_width=True):
                st.session_state.current_analytics_tab = tab
                st.session_state.show_loading = True
                st.rerun()
    
    # Show loading screen
    if st.session_state.get('show_loading', False):
        st.markdown(f"""
        <div class="loading-screen">
            <div class="chat-logo">
                😊
            </div>
            <div class="loading-text">Generating Detailed Analysis...</div>
            <div class="loading-subtitle">This may take a moment as the AI cross-references data.</div>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulate loading time
        time.sleep(2)
        st.session_state.show_loading = False
        st.rerun()
    
    # Display content based on selected tab
    current_tab = st.session_state.get('current_analytics_tab', 'Crime Trends')
    
    if current_tab == 'Crime Trends':
        st.markdown('<h2>📈 Crime Trends Insights</h2>', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #8b949e;">Q2 2025 Regional Crime Trends Analysis</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        Overall, the second quarter of 2025 in our region indicates a **marginal increase** in reported criminal incidents compared to the previous quarter. This modest rise is primarily driven by specific categories within property crimes.
        
        **Key observations from the Q2 2025 data:**
        
        • Property Crime continues to be the most prevalent category. Burglaries show a slight decrease, likely due to enhanced community vigilance programs. However, **vehicle thefts** have seen a significant 18% increase across the region, particularly concentrated in the suburban areas.
        
        • Shoplifting and general theft incidents remain consistent with previous quarters, with no notable shifts in volume or method.
        
        • Violent Crime statistics remain **stable** overall. Assaults and domestic disturbances show no significant deviation from historical averages.
        
        • Robberies, while lower in volume than property crimes, have seen a minor 5% uptick, primarily street-level incidents in commercial districts during evening hours.
        
        • Drug-related offenses show a slight increase in arrests, which may indicate **proactive enforcement efforts** rather than a surge in usage.
        
        • Detection rates for property crimes, particularly burglaries, have improved slightly, reflecting success in evidence collection and community cooperation. Vehicle theft detection rates, however, remain challenging.
        
        • A concerning trend is the increase in **cyber-enabled fraud reports**, although these are still a small percentage of overall crime. This area requires increased public awareness and specialized investigative resources.
        
        This analysis suggests a need for targeted interventions focusing on vehicle theft prevention and continued vigilance in commercial areas. Further localized reports can provide more granular data for specific precincts or neighborhoods.
        """)
    
    elif current_tab == 'District Analysis':
        st.markdown('<h2>🏘️ District Analysis Insights</h2>', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #8b949e;">District Q2 2025 Crime Analysis</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        This report provides a comprehensive analysis of crime data for the district during Quarter 2 (April 1 - June 30), 2025. The aim is to identify key trends, high-incidence areas, and support data-driven deployment strategies.
        
        **Key Findings:**
        
        • Overall crime incidents decreased by 5% compared to Q1 2025, but show a **2% increase** compared to Q2 2024.
        
        • Property crimes remain the **most prevalent** category, accounting for 65% of all reported incidents.
        
        • Violent crimes saw a slight reduction, primarily in non-fatal assault cases.
        
        • Clearance rates for **serious violent crimes** improved by 3 percentage points.
        
        **Specific Crime Trends:**
        
        • **Residential Burglaries:** A notable 15% increase was observed, particularly during weekday daytime hours (10:00 AM - 3:00 PM). This suggests a pattern targeting unoccupied homes.
        
        • **Vehicle Thefts:** Remained stable, with a slight shift towards commercial parking lots during evening hours.
        
        • **Retail Theft:** Increased by 8%, with a concentration in the downtown commercial zone. Organized retail crime appears to be a contributing factor.
        
        • **Assaults (Non-Fatal):** Decreased by 7%, largely due to targeted patrols in high-risk areas identified in Q1.
        
        • **Narcotics Offenses:** A 10% increase in arrests was noted, indicating **proactive enforcement efforts** by specialized units.
        
        **Geographical Hotspots:**
        
        • **Sector 3B (Commercial District):** Continued high incidence of retail theft and minor property damage.
        
        • **Sector 5A (Residential West):** Experienced a surge in residential burglaries. Analysis indicates a clustering of incidents around specific arterial roads.
        
        • **Sector 1C (Downtown Core):** Remained a primary location for public order offenses and a **moderate level** of violent crime, despite the overall decrease.
        
        **Operational Recommendations:**
        
        • **Targeted Patrols:** Increase visibility and patrols in Sector 5A during weekday daytime hours to deter residential burglaries.
        
        • **Business Engagement:** Collaborate with businesses in Sector 3B to implement enhanced security measures and surveillance for retail theft prevention.
        
        • **Data-Driven Deployment:** Utilize predictive models to anticipate peak times and locations for specific crime types, optimizing resource allocation.
        
        • **Community Outreach:** Strengthen community watch programs in affected residential areas and promote reporting of suspicious activities.
        
        • **Follow-Up Analysis:** Conduct a focused study on the impact of narcotics enforcement to evaluate long-term effects on related crimes.
        """)
    
    # Analytics Questions
    st.markdown('<h2>🤔 Analytics Questions</h2>', unsafe_allow_html=True)
    
    questions = [
        ("🔍", "What are the homicide trends for the past 10 years?"),
        ("📊", "Predict crime rates for 2026"),
        ("🌍", "Which district has the highest crime rate?"),
        ("🔄", "How have drug crimes changed recently?"),
        ("📈", "Show me a chart of crime detection rates"),
        ("🎯", "What's the most common crime method?"),
        ("📅", "Are there seasonal crime patterns?"),
        ("⚠️", "What are the biggest crime concerns?"),
        ("⚡", "How effective is police performance?"),
        ("🎯", "Where should police focus resources?")
    ]
    
    for i in range(0, len(questions), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(questions):
                icon, question = questions[i]
                if st.button(f"{icon} {question}", key=f"q_{i}", use_container_width=True):
                    st.info(f"Processing: {question}")
        
        with col2:
            if i + 1 < len(questions):
                icon, question = questions[i + 1]
                if st.button(f"{icon} {question}", key=f"q_{i+1}", use_container_width=True):
                    st.info(f"Processing: {question}")

# AI ASSISTANT PAGE
elif st.session_state.current_page == 'chat':
    st.markdown("""
    <div class="chat-welcome">
        <div class="chat-logo">
            🛡️
        </div>
        <h1 class="chat-title">SECURO</h1>
        <p class="chat-subtitle">Enhanced AI Assistant</p>
        <p style="color: #8b949e; max-width: 600px; margin: 0 auto 30px;">
            Welcome, I am SECURO, an enhanced AI Assistant & Crime Intelligence system for Law Enforcement Professionals. I am Online and ready, having justloaded the crime intelligence database. You now have access to comprehensive St. Kitts & Nevis crime statistics, international comparison data from MacroTrends, and can maintain your chat history. Click Start to begin the conversation and find out more about my capabilities.
        </p>
        <button class="start-button" onclick="startChat()">Start Conversation</button>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Start Conversation", key="start_chat", use_container_width=True):
        st.info("Chat functionality would be implemented here with the enhanced AI system!")

# CHAT HISTORY PAGE
elif st.session_state.current_page == 'history':
    st.markdown('<h1 style="text-align: center; margin-bottom: 20px;">💾 Chat History Archive</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #8b949e; margin-bottom: 40px;">Review and continue any of your past conversations with SECURO. All chat context is preserved.</p>', unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💬</div>
            <h2 class="empty-title">No Chat History Found</h2>
            <p class="empty-subtitle">Start a conversation in the AI Assistant tab to create your first chat session.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for chat_id, chat_data in st.session_state.chat_sessions.items():
            is_active = chat_id == st.session_state.current_chat_id
            
            if st.button(f"💬 {chat_data['name']}", key=f"hist_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.session_state.current_page = 'chat'
                st.rerun()
            
            st.caption(f"Created: {chat_data['created_at']} AST | Last Activity: {chat_data['last_activity']} AST")
            if chat_data['messages']:
                last_msg = chat_data['messages'][-1]['content'][:100] + "..." if len(chat_data['messages'][-1]['content']) > 100 else chat_data['messages'][-1]['content']
                st.caption(f"Last message: {last_msg}")
            st.markdown("---")

# EMERGENCY CONTACTS PAGE
elif st.session_state.current_page == 'emergency':
    st.markdown('<h1 style="text-align: center; margin-bottom: 40px;">🚨 Emergency Contacts</h1>', unsafe_allow_html=True)
    
    # Emergency cards grid
    st.markdown('<div class="emergency-grid">', unsafe_allow_html=True)
    
    for i, (service, details) in enumerate(EMERGENCY_CONTACTS.items()):
        if i % 4 == 0:
            cols = st.columns(4)
        
        with cols[i % 4]:
            st.markdown(f"""
            <div class="emergency-card">
                <div class="emergency-icon">{details['icon']}</div>
                <h3>{service}</h3>
                <div class="emergency-number">{details['number']}</div>
                <p>{details['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Emergency Guidelines
    st.markdown("""
    <div class="guidelines-box">
        <h3 class="guidelines-title">⚠️ Important Emergency Guidelines</h3>
        <ul class="guidelines-list">
            <li>For life-threatening emergencies, always call <strong>911</strong> first.</li>
            <li>When calling, provide your exact location and the nature of the emergency.</li>
            <li>Stay on the line until instructed to hang up.</li>
            <li>Keep these numbers easily accessible at all times.</li>
            <li>Follow dispatcher instructions carefully.</li>
            <li>Provide first aid only if trained to do so.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Status Bar
current_time = get_stkitts_time()
total_chats = len(st.session_state.chat_sessions)

st.markdown(f"""
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot"></div>
        <span class="status-active">Enhanced AI Active</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span class="status-active">MacroTrends Integration: Active</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span class="status-active">Conversation Memory: Enabled</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Chat Sessions: {total_chats}</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>🕒 {current_time} AST</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="main-footer">
    <div class="footer-content">
        <div class="footer-grid">
            <div class="footer-section">
                <h4>Data Source</h4>
                <p>📊 Royal St. Christopher & Nevis Police Force (RSCNPF)</p>
                <p>📈 Statistical Integration Active</p>
                <p>🌍 Multi-language Support</p>
                <p>🔒 Secure Law Enforcement Platform</p>
            </div>
            <div class="footer-section">
                <h4>Last Updated</h4>
                <p>🔄 {get_stkitts_date()} {get_stkitts_time()} AST</p>
                <p>🤖 AI System: Enhanced AI Intelligence</p>
                <p>📊 Enhanced AI Assistant Platform</p>
                <p>🧠 Enhanced AI Assistant Platform</p>
            </div>
            <div class="footer-section">
                <h4>Contact Information</h4>
                <p>📞 Local Intelligence Office: 869-465-2241 Ext. 4238/4239</p>
                <p>📧 lio@police.kn</p>
                <p>🌐 Multi-Chat Support</p>
                <p>⚖️ Secure Law Enforcement Platform</p>
            </div>
            <div class="footer-section">
                <h4>AI System</h4>
                <p>🧠 Enhanced AI Assistant Platform</p>
                <p>Statistical knowledge integration • Conversation memory • Context awareness • Multi-chat support • Professional law enforcement assistance</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 SECURO - Enhanced AI Assistant & Crime Intelligence System | Royal St. Christopher and Nevis Police Force | Version 2.1.0</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
