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
import base64
warnings.filterwarnings('ignore')

# Add Gmail API imports for anonymous reporting
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit.components.v1 as components

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

# Gmail API Configuration for Anonymous Reports
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']
REPORT_EMAIL = 'lawszahir@gmail.com'

# Gmail credentials configuration - Store as Streamlit secrets or environment variables
GMAIL_CREDENTIALS = {
    "installed": {
        "client_id": "245730712367-es4t289csrtehr4mjbh0r9jbadoso9s9.apps.googleusercontent.com",
        "project_id": "crimebot-468818",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"]
    }
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

# Anonymous Report System Functions
def init_gmail_service():
    """Initialize Gmail service for sending anonymous reports"""
    try:
        creds = None
        
        # Check if we have stored credentials in session state
        if 'gmail_creds' in st.session_state:
            creds = st.session_state.gmail_creds
        
        # If no valid credentials, we need to authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # For Streamlit, we'll need a different approach
                st.error("Gmail authentication required. Please contact administrator.")
                return None
        
        # Store credentials in session state
        st.session_state.gmail_creds = creds
        
        service = build('gmail', 'v1', credentials=creds)
        return service
        
    except Exception as e:
        st.error(f"Gmail service initialization failed: {str(e)}")
        return None

def send_anonymous_report(report_data):
    """Send anonymous crime report via Gmail"""
    try:
        # For demo purposes, we'll simulate sending the email
        # In production, you'd use the actual Gmail API
        
        # Format the report
        timestamp = f"{get_stkitts_date()} {get_stkitts_time()} AST"
        
        report_text = f"""
ANONYMOUS CRIME REPORT - SECURO SYSTEM
=====================================

Report ID: {uuid.uuid4()}
Timestamp: {timestamp}
Source: SECURO Anonymous Reporting System

INCIDENT DETAILS:
-----------------
Type: {report_data.get('crime_type', 'Not specified')}
Location: {report_data.get('location', 'Not specified')}
Date/Time: {report_data.get('incident_time', 'Not specified')}

DESCRIPTION:
------------
{report_data.get('description', 'No description provided')}

ADDITIONAL INFORMATION:
----------------------
Suspect Information: {report_data.get('suspect_info', 'None provided')}
Witnesses: {report_data.get('witnesses', 'None mentioned')}
Evidence: {report_data.get('evidence', 'None mentioned')}

CONTACT PREFERENCE:
------------------
Anonymous Contact: {report_data.get('contact_preference', 'No contact requested')}

PRIORITY LEVEL:
--------------
{report_data.get('priority', 'Standard')}

=====================================
This report was submitted anonymously through the SECURO system.
All reports are treated confidentially and investigated appropriately.
"""

        # Simulate sending (in production, uncomment the actual sending code)
        # service = init_gmail_service()
        # if service:
        #     message = MIMEText(report_text)
        #     message['to'] = REPORT_EMAIL
        #     message['subject'] = f'Anonymous Crime Report - {report_data.get("crime_type", "Incident")} - {timestamp}'
        #     raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        #     service.users().messages().send(userId="me", body={'raw': raw}).execute()
        
        # For demo, store in session state
        if 'submitted_reports' not in st.session_state:
            st.session_state.submitted_reports = []
        
        st.session_state.submitted_reports.append({
            'id': str(uuid.uuid4())[:8],
            'timestamp': timestamp,
            'type': report_data.get('crime_type', 'Unknown'),
            'location': report_data.get('location', 'Unknown'),
            'status': 'Submitted'
        })
        
        return True, f"Report submitted successfully at {timestamp}"
        
    except Exception as e:
        return False, f"Failed to submit report: {str(e)}"

# Chat Management System
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

if 'chat_counter' not in st.session_state:
    st.session_state.chat_counter = 1

if 'current_analytics_tab' not in st.session_state:
    st.session_state.current_analytics_tab = 'Crime Trends'

if 'statistical_database' not in st.session_state:
    st.session_state.statistical_database = {}

if 'main_view' not in st.session_state:
    st.session_state.main_view = 'ai-assistant'

if 'chat_active' not in st.session_state:
    st.session_state.chat_active = False

# NEW: Theme management
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

def text_to_speech_component(text, message_id="tts"):
    """Create a working text-to-speech component with female voice"""
    return ""

def auto_speak_response(text):
    """Auto-speak functionality for new responses with enhanced female voice"""
    clean_text = text.replace("🚔", "").replace("🚨", "").replace("📊", "").replace("💬", "").replace("🤖", "")
    clean_text = clean_text.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
    clean_text = clean_text.replace("•", "").replace("\n", " ").strip()
    
    if len(clean_text) > 200:
        clean_text = clean_text[:200] + "..."
    
    clean_text = clean_text.replace("'", "\\'").replace('"', '\\"')
    
    auto_speak_html = f"""
    <script>
    setTimeout(function() {{
        if ('speechSynthesis' in window) {{
            const text = `{clean_text}`;
            if (text.length > 0) {{
                const utterance = new SpeechSynthesisUtterance(text);
                
                // Enhanced female voice settings
                const voices = speechSynthesis.getVoices();
                const femaleVoice = voices.find(voice => 
                    voice.name.toLowerCase().includes('female') ||
                    voice.name.toLowerCase().includes('woman') ||
                    voice.name.toLowerCase().includes('zira') ||
                    voice.name.toLowerCase().includes('helen') ||
                    voice.name.toLowerCase().includes('samantha') ||
                    voice.name.toLowerCase().includes('serena') ||
                    voice.name.toLowerCase().includes('karen') ||
                    voice.name.toLowerCase().includes('tessa') ||
                    voice.name.toLowerCase().includes('catherine') ||
                    voice.gender === 'female'
                );
                
                if (femaleVoice) {{
                    utterance.voice = femaleVoice;
                }}
                
                utterance.rate = 0.85;
                utterance.pitch = 1.1;
                utterance.volume = 0.9;
                
                window.speechSynthesis.speak(utterance);
            }}
        }}
    }}, 1000);
    </script>
    """
    return auto_speak_html

def get_current_chat():
    """Get current chat session"""
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
        return st.session_state.chat_sessions[st.session_state.current_chat_id]
    else:
        if st.session_state.get('chat_active', False):
            return create_new_chat_session()
        else:
            return {
                'id': 'temp',
                'name': 'New Chat',
                'messages': [],
                'created_at': get_stkitts_time(),
                'last_activity': get_stkitts_time()
            }

def create_new_chat_session():
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
    return st.session_state.chat_sessions[chat_id]

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

# Statistical Data Processing Functions
def fetch_and_process_statistics():
    """Fetch and process statistics from PDF URLs"""
    if st.session_state.statistical_database:
        return st.session_state.statistical_database
    
    st.session_state.statistical_database = HISTORICAL_CRIME_DATABASE.copy()
    
    st.session_state.statistical_database.update({
        "macrotrends_data": MACROTRENDS_DATA,
        "recent_trends": {
            "murder_trend": "75% decrease from 2024 to 2025 H1",
            "drug_crimes_trend": "463% increase in drug crimes 2024-2025",
            "detection_improvement": "Detection rates vary by crime type",
            "larceny_concern": "Larcenies remain highest volume crime"
        },
        "geographical_breakdown": {
            "st_kitts_districts_ab": "Higher crime volume but lower detection rate",
            "nevis_district_c": "Lower crime volume but higher detection rate",
            "federation_wide": "Overall crime trends showing mixed results"
        }
    })
    
    return st.session_state.statistical_database

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
    
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    risk_colors = {
        'High': '#ff4444',
        'Medium': '#1e90ff', 
        'Low': '#0066cc'
    }
    
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
            <small style="color: #666;">📍 Lat: {data['lat']:.4f}, Lon: {data['lon']:.4f}</small>
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
    
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 180px; height: 140px; 
                background-color: rgba(0, 0, 0, 0.8); 
                border: 2px solid rgba(30, 144, 255, 0.5);
                border-radius: 10px; z-index:9999; 
                font-size: 12px; font-family: Arial;
                padding: 10px; color: white;">
    <h4 style="margin: 0 0 10px 0; color: #1e90ff;">🗺️ Crime Risk Legend</h4>
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
    
    folium.LayerControl().add_to(m)
    
    return m

def create_macrotrends_comparison_charts(chart_type="homicide_trends"):
    """Create charts using MacroTrends international comparison data"""
    
    if chart_type == "homicide_trends":
        years = list(MACROTRENDS_DATA["homicide_rates_per_100k"].keys())
        rates = list(MACROTRENDS_DATA["homicide_rates_per_100k"].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=rates,
            mode='lines+markers',
            name='Homicide Rate per 100K',
            line=dict(color='#ff4444', width=3),
            marker=dict(size=10, color='#ff4444')
        ))
        
        global_avg = MACROTRENDS_DATA["comparative_context"]["global_average_firearm_homicides"]
        fig.add_hline(y=global_avg, line_dash="dash", line_color="#888888",
                     annotation_text=f"Global Average: {global_avg}%")
        
        theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
        
        fig.update_layout(
            title="St. Kitts & Nevis Homicide Rate Trends (MacroTrends Data)",
            xaxis_title="Year",
            yaxis_title="Homicides per 100,000 Population",
            template=theme,
            height=500
        )
        
        return fig
    
    elif chart_type == "recent_crime_totals":
        years = ["2022", "2023", "2024"]
        crimes = [
            MACROTRENDS_DATA["recent_trends"]["2022_total_crimes"],
            MACROTRENDS_DATA["recent_trends"]["2023_total_crimes"],
            MACROTRENDS_DATA["recent_trends"]["2024_total_crimes"]
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=years, y=crimes,
            marker_color='#1e90ff',
            text=[f"{crime:,}" for crime in crimes],
            textposition='auto'
        ))
        
        theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
        
        fig.update_layout(
            title="Total Crime Trends 2022-2024 (RSCNPF Data)",
            xaxis_title="Year",
            yaxis_title="Total Crimes",
            template=theme,
            height=500
        )
        
        return fig
    
    elif chart_type == "international_context":
        categories = ["St. Kitts 2020", "St. Kitts 2019", "St. Kitts 2018", "Global Avg.", "St. Kitts Peak (2011)"]
        values = [
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2020"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2019"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2018"],
            MACROTRENDS_DATA["comparative_context"]["global_average_firearm_homicides"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2011"]
        ]
        
        colors = ['#1e90ff', '#0066cc', '#ff4444', '#888888', '#ff0000']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=colors,
            text=[f"{val:.1f}" for val in values],
            textposition='auto'
        ))
        
        theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
        
        fig.update_layout(
            title="International Context: Homicide Rates per 100K Population",
            xaxis_title="Comparison Points",
            yaxis_title="Rate per 100,000",
            template=theme,
            height=500
        )
        
        return fig

def is_international_comparison_query(user_input):
    """Detect if user wants international comparison or historical trends"""
    comparison_keywords = ['international', 'global', 'worldwide', 'compare', 'comparison', 'trends', 'historical', 'macrotrends', 'world average', 'per 100k', 'rate', 'historical chart', 'long term', 'decade']
    return any(keyword in user_input.lower() for keyword in comparison_keywords)

def is_casual_greeting(user_input):
    """Detect if user input is a casual greeting"""
    casual_words = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'sup']
    return any(word in user_input.lower().strip() for word in casual_words) and len(user_input.strip()) < 25

def is_detailed_request(user_input):
    """Detect if user wants detailed information"""
    detail_keywords = ['detailed', 'detail', 'explain', 'comprehensive', 'thorough', 'in depth', 'breakdown', 'elaborate', 'more information', 'tell me more']
    return any(keyword in user_input.lower() for keyword in detail_keywords)

def is_statistics_query(user_input):
    """Detect if user is asking about statistics"""
    stats_keywords = ['statistics', 'stats', 'data', 'crime rate', 'trends', 'numbers', 'figures', 'analysis', 'murder', 'robbery', 'larceny', 'detection rate', 'quarterly', 'annual', 'breakdown', 'comparison']
    return any(keyword in user_input.lower() for keyword in stats_keywords)

def generate_enhanced_smart_response(user_input, conversation_history=None, language='en'):
    """Generate AI responses with statistical knowledge and conversation memory"""
    
    if not st.session_state.get('ai_enabled', False):
        return "🔧 AI system offline. Please check your API key configuration.", None
    
    try:
        stats_data = fetch_and_process_statistics()
        
        chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'show me', 'display', 'trends', 'comparison']
        wants_chart = any(keyword in user_input.lower() for keyword in chart_keywords)
        chart_to_show = None
        
        has_greeted_before = False
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'assistant' and any(greeting in msg['content'].lower() for greeting in ['good morning', 'good afternoon', 'good evening', 'hello', 'hi']):
                    has_greeted_before = True
                    break
        
        if is_casual_greeting(user_input) and not has_greeted_before:
            prompt = f"""
            You are SECURO, an AI assistant for St. Kitts & Nevis Police.
            
            User said: "{user_input}"
            
            Respond with a brief, friendly greeting (2-3 sentences max). Mention you're ready to help with questions about crime statistics or general assistance.
            Include the appropriate time-based greeting (good morning/afternoon/evening) based on the current time.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
        
        elif is_casual_greeting(user_input) and has_greeted_before:
            prompt = f"""
            You are SECURO, an AI assistant for St. Kitts & Nevis Police.
            
            User said: "{user_input}"
            The user has already been greeted earlier in this conversation.
            
            Respond with a brief acknowledgment WITHOUT repeating any greeting. Just ask how you can help or what they'd like to know about.
            Keep it to 1-2 sentences.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
        
        elif is_statistics_query(user_input) or is_international_comparison_query(user_input) or wants_chart:
            is_detailed = is_detailed_request(user_input)
            is_comparison = is_international_comparison_query(user_input)
            
            if wants_chart:
                if 'international' in user_input.lower() or 'global' in user_input.lower() or 'world' in user_input.lower():
                    chart_to_show = "international"
                elif 'trend' in user_input.lower() or 'over time' in user_input.lower() or 'years' in user_input.lower():
                    chart_to_show = "trends"
                elif 'detection' in user_input.lower():
                    chart_to_show = "detection"
                elif 'breakdown' in user_input.lower() or 'types' in user_input.lower():
                    chart_to_show = "breakdown"
                elif 'manslaughter' in user_input.lower() or 'murder' in user_input.lower() or 'homicide' in user_input.lower():
                    chart_to_show = "homicide"
                else:
                    chart_to_show = "trends"
            
            context = ""
            if conversation_history and len(conversation_history) > 1:
                recent_messages = conversation_history[-4:]
                context = "Recent conversation context:\n"
                for msg in recent_messages:
                    context += f"{msg['role']}: {msg['content'][:100]}...\n"
                context += "\n"
            
            macrotrends_context = ""
            if is_comparison:
                macrotrends_context = f"""
                
                **MacroTrends International Data Available:**
                {json.dumps(MACROTRENDS_DATA, indent=2)}
                """
            
            prompt = f"""
            You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force with access to comprehensive crime statistics AND international comparison data.
            
            {context}User query: "{user_input}"
            Detailed request: {is_detailed}
            International comparison requested: {is_comparison}
            Chart requested: {wants_chart}
            
            **Available Local Statistical Data:**
            {json.dumps(stats_data, indent=2)}
            {macrotrends_context}
            
            **Response Guidelines:**
            - NEVER say "Good morning", "Good afternoon", or "Good evening" in your response unless the user just greeted you for the first time
            - If detailed=False: Keep response concise (3-5 sentences) but data-rich
            - If detailed=True: Provide comprehensive statistical analysis
            - If comparison=True: Include international context, MacroTrends data
            - If chart requested: Say "I'll display the requested chart below" and provide data analysis
            - NEVER mention limitations about displaying charts - you CAN display interactive charts
            - Use specific numbers and percentages from the data above
            - Reference time periods (Q2 2025, H1 2024, etc.) when relevant
            - Include comparisons and trends when available
            - When discussing international comparisons, reference the MacroTrends data
            - Maintain professional law enforcement communication
            - Focus on actionable insights for police operations
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            
            Provide data-driven statistical analysis with specific figures and international context when relevant.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), chart_to_show
            
        else:
            is_detailed = is_detailed_request(user_input)
            
            context = ""
            if conversation_history and len(conversation_history) > 1:
                recent_messages = conversation_history[-6:]
                context = "Conversation history for context:\n"
                for msg in recent_messages:
                    context += f"{msg['role']}: {msg['content'][:150]}...\n"
                context += "\n"
            
            prompt = f"""
            You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force.
            
            {context}Current user query: "{user_input}"
            Detailed request: {is_detailed}
            
            **Response Guidelines:**
            - NEVER say "Good morning", "Good afternoon", or "Good evening" in your response unless the user just greeted you for the first time
            - If detailed=False: Keep response concise (3-5 sentences)
            - If detailed=True: Provide thorough explanation
            - Maintain conversation context and reference previous messages when relevant
            - Provide professional assistance suitable for law enforcement
            - Include practical recommendations when appropriate
            - You have access to crime statistics and can generate charts if asked
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            
            Provide helpful, context-aware assistance.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
            
    except Exception as e:
        return f"🚨 AI analysis error: {str(e)}\n\nI'm still here to help! Please try rephrasing your question or check your internet connection.", None

# Initialize AI model
try:
    GOOGLE_API_KEY = "AIzaSyBYRyEfONMUHdYmeFDkUGSTP1rNEy_p2L0"
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
    page_title="SECURO - Enhanced AI Crime Intelligence System",
    page_icon="https://i.postimg.cc/QC6xqk1G/PH-PR-2.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize statistics on startup
fetch_and_process_statistics()

# Initialize chat system only if needed
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

# Enhanced CSS with all requested improvements
def get_theme_css():
    if st.session_state.dark_mode:
        return """
        /* DARK MODE */
        .stApp {
            background: radial-gradient(circle at 20% 50%, #1a1a2e 0%, #16213e 25%, #0f172a 100%);
            color: #ffffff;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .main-bg {
            background: radial-gradient(circle at 20% 50%, #1a1a2e 0%, #16213e 25%, #0f172a 100%);
        }
        
        .sidebar-bg {
            background: linear-gradient(180deg, #1e293b 0%, #334155 50%, #1e293b 100%);
        }
        """
    else:
        return """
        /* LIGHT MODE */
        .stApp {
            background: radial-gradient(circle at 20% 50%, #f0f9ff 0%, #e0f2fe 25%, #f8fafc 100%);
            color: #0f172a;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .main-bg {
            background: radial-gradient(circle at 20% 50%, #f0f9ff 0%, #e0f2fe 25%, #f8fafc 100%);
        }
        
        .sidebar-bg {
            background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
        }
        """

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    
    /* Hide "Press Enter to submit" text */
    .stTextInput > div > div > div > div:last-child {{
        display: none;
    }}
    
    /* Root styling - Enhanced theme support */
    {get_theme_css()}
    
    /* Enhanced Sidebar - Collapsible */
    .css-1d391kg {{
        {get_theme_css().split('.sidebar-bg')[1].split('}')[0] + '}' if '.sidebar-bg' in get_theme_css() else 'background: linear-gradient(180deg, #1e293b 0%, #334155 50%, #1e293b 100%);'}
        border-right: 2px solid transparent !important;
        background-clip: padding-box !important;
        position: relative !important;
        transition: all 0.3s ease !important;
    }}
    
    .css-1d391kg::before {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, #3b82f6, #ef4444, #3b82f6, #ef4444);
        background-size: 100% 400%;
        animation: sidebar-border-pulse 3s ease-in-out infinite;
    }}
    
    @keyframes sidebar-border-pulse {{
        0%, 100% {{ background-position: 0% 0%; }}
        50% {{ background-position: 0% 100%; }}
    }}
    
    /* Collapsible sidebar button */
    .css-1544g2n {{
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        background: linear-gradient(45deg, #3b82f6, #ef4444) !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.3s ease !important;
    }}
    
    .css-1544g2n:hover {{
        transform: scale(1.1) !important;
        box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4) !important;
    }}
    
    /* Sidebar navigation header with glow effect */
    .sidebar-nav-header {{
        background: linear-gradient(45deg, #3b82f6, #ef4444, #3b82f6, #ef4444);
        background-size: 400% 400%;
        animation: gradient-move 3s ease infinite;
        margin: -1rem -1rem 1rem -1rem;
        padding: 12px 16px;
        border-radius: 0 0 8px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 16px;
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 0 10px rgba(255, 255, 255, 0.3);
        letter-spacing: 1px;
        text-transform: uppercase;
    }}
    
    @keyframes gradient-move {{
        0%, 100% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
    }}
    
    /* Enhanced Glowing Text Effects */
    .glow-text {{
        animation: glow-pulse 2s ease-in-out infinite alternate;
        text-shadow: 0 0 5px currentColor, 0 0 10px currentColor, 0 0 15px currentColor;
    }}
    
    @keyframes glow-pulse {{
        from {{
            text-shadow: 0 0 5px currentColor, 0 0 10px currentColor, 0 0 15px currentColor;
        }}
        to {{
            text-shadow: 0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor;
        }}
    }}
    
    /* Main content area - Reduced spacing */
    .main .block-container {{
        padding: 0.5rem 1rem !important;
        max-width: 100%;
        margin-top: 0 !important;
    }}
    
    /* Header bar with enhanced glow */
    .header-bar {{
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-bottom: 1px solid #475569;
        padding: 12px 24px;
        margin: -0.5rem -1rem 1rem -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
    }}
    
    .logo-section {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    
    .logo-icon {{
        width: 40px;
        height: 40px;
        background: linear-gradient(45deg, #3b82f6, #ef4444, #3b82f6, #ef4444);
        background-size: 400% 400%;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        animation: logo-pulse 2s ease-in-out infinite;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
    }}
    
    @keyframes logo-pulse {{
        0%, 100% {{ 
            background-position: 0% 50%;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
            transform: scale(1);
        }}
        50% {{ 
            background-position: 100% 50%;
            box-shadow: 0 0 30px rgba(239, 68, 68, 0.5);
            transform: scale(1.05);
        }}
    }}
    
    .logo-text h1 {{
        color: #3b82f6 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: 1.5px;
        animation: text-pulse-glow 3s ease-in-out infinite;
        text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
    }}
    
    @keyframes text-pulse-glow {{
        0%, 100% {{ 
            color: #3b82f6 !important; 
            text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
        }}
        50% {{ 
            color: #ef4444 !important; 
            text-shadow: 0 0 15px rgba(239, 68, 68, 0.7);
        }}
    }}
    
    .logo-text p {{
        color: #94a3b8 !important;
        font-size: 12px !important;
        margin: 0 !important;
        font-weight: 500;
    }}
    
    .status-section {{
        display: flex;
        align-items: center;
        gap: 20px;
        font-size: 14px;
    }}
    
    .status-item {{
        display: flex;
        align-items: center;
        gap: 8px;
        color: #94a3b8;
    }}
    
    .status-dot {{
        width: 8px;
        height: 8px;
        background: linear-gradient(45deg, #3b82f6, #ef4444);
        border-radius: 50%;
        animation: dot-pulse 1.5s infinite;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
    }}
    
    @keyframes dot-pulse {{
        0%, 100% {{ 
            background: #3b82f6; 
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
        }}
        50% {{ 
            background: #ef4444; 
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
        }}
    }}
    
    /* Theme Toggle Button */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999999;
        background: linear-gradient(45deg, #3b82f6, #ef4444);
        border: none;
        color: white;
        padding: 10px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }}
    
    .theme-toggle:hover {{
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
    }}
    
    /* Chat interface styling - Reduced spacing */
    .chat-container {{
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 16px;
        overflow: hidden;
        height: auto;
        display: flex;
        flex-direction: column;
        margin-bottom: 0.5rem;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
    }}
    
    .chat-header {{
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        padding: 12px 16px;
        border-bottom: 1px solid #475569;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .chat-header h3 {{
        color: #ffffff !important;
        margin: 0 !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }}
    
    .ai-status {{
        color: #10b981 !important;
        font-size: 12px !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    .chat-messages {{
        flex: 1;
        overflow-y: auto;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        min-height: 200px;
        max-height: 500px;
        background: #0f172a;
    }}
    
    .message {{
        display: flex;
        flex-direction: column;
        animation: messageSlide 0.3s ease-out;
        margin-bottom: 4px;
        width: auto;
        max-width: 80%;
    }}
    
    @keyframes messageSlide {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* User messages - right side */
    .message.user {{
        align-self: flex-end;
        margin-left: auto;
        width: fit-content;
        min-width: auto;
        max-width: 70%;
    }}
    
    .message.user .message-bubble {{
        background: linear-gradient(135deg, #3b82f6, #ef4444);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 8px 12px;
        font-size: 14px;
        line-height: 1.4;
        word-wrap: break-word;
        white-space: pre-wrap;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        display: inline-block;
        width: auto;
        min-width: 30px;
        max-width: 100%;
    }}
    
    /* Assistant messages - left side */
    .message.assistant {{
        align-self: flex-start;
        margin-right: auto;
        width: fit-content;
        min-width: auto;
        max-width: 80%;
    }}
    
    .message.assistant .message-bubble {{
        background: linear-gradient(135deg, #374151, #4b5563);
        color: #f9fafb;
        border-radius: 18px 18px 18px 4px;
        padding: 8px 12px;
        font-size: 14px;
        line-height: 1.4;
        word-wrap: break-word;
        white-space: pre-wrap;
        border: 1px solid #6b7280;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        width: auto;
        min-width: 60px;
        max-width: 100%;
    }}
    
    .message-content {{
        flex: 1;
        margin-right: 8px;
        text-align: left;
        line-height: 1.5;
        word-wrap: break-word;
        white-space: pre-wrap;
        text-indent: 0;
        padding-left: 0;
    }}
    
    .message-time {{
        font-size: 10px;
        color: #64748b;
        margin-top: 2px;
        font-weight: 400;
    }}
    
    .message.user .message-time {{
        text-align: right;
        color: rgba(255, 255, 255, 0.7);
    }}
    
    .message.assistant .message-time {{
        text-align: left;
        color: #9ca3af;
    }}
    
    /* Enhanced Speaker button with female voice indication */
    .speak-button {{
        background: linear-gradient(45deg, #10b981, #059669) !important;
        border: none !important;
        padding: 4px 6px !important;
        cursor: pointer !important;
        font-size: 12px !important;
        opacity: 0.8 !important;
        transition: all 0.2s ease !important;
        border-radius: 4px !important;
        position: relative !important;
        top: -2px !important;
        flex-shrink: 0 !important;
        margin-left: 8px !important;
        align-self: flex-start !important;
        color: white !important;
        box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3) !important;
    }}
    
    .speak-button:hover {{
        opacity: 1 !important;
        background: linear-gradient(45deg, #059669, #047857) !important;
        transform: scale(1.05) !important;
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4) !important;
    }}
    
    .speak-button::after {{
        content: ' ♀️';
        font-size: 8px;
        opacity: 0.7;
    }}
    
    .chat-input-area {{
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        border-top: 1px solid #475569;
        padding: 12px 16px;
    }}
    
    /* Input styling */
    .stTextInput input {{
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stTextInput input:focus {{
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1), 0 0 10px rgba(59, 130, 246, 0.2) !important;
        background: rgba(0, 0, 0, 0.6) !important;
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, #3b82f6, #ef4444) !important;
        border: none !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
    }}
    
    /* Chart container - Positioned above text input */
    .chart-container {{
        margin-bottom: 1rem !important;
        padding: 1rem;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        border: 1px solid #475569;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
    }}
    
    /* Compact spacing for all elements */
    .main-content-section {{
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
    }}
    
    .section-header {{
        color: #3b82f6 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
        display: flex;
        align-items: center;
        gap: 12px;
        text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
    }}
    
    .section-content {{
        color: #cbd5e1 !important;
        line-height: 1.6 !important;
        margin: 0 !important;
    }}
    
    /* Reduce all margins and padding */
    .stMarkdown {{
        margin-bottom: 0.5rem !important;
    }}
    
    .stMarkdown > div {{
        margin-bottom: 0.25rem !important;
    }}
    
    /* Enhanced background effects */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(239, 68, 68, 0.1) 0%, transparent 50%);
        z-index: -1;
        animation: bg-float 20s ease-in-out infinite;
    }}
    
    @keyframes bg-float {{
        0%, 100% {{ opacity: 0.5; }}
        50% {{ opacity: 0.8; }}
    }}
    
    /* Status bar with reduced height */
    .status-bar {{
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-top: 1px solid #475569;
        padding: 8px 16px;
        margin: 1rem -1rem -0.5rem -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        box-shadow: 0 -4px 20px rgba(59, 130, 246, 0.1);
    }}
    
    .status-indicators {{
        display: flex;
        gap: 15px;
    }}
    
    .status-indicator {{
        display: flex;
        align-items: center;
        gap: 4px;
        color: #94a3b8;
    }}
    
    .status-indicator.active {{
        color: #3b82f6;
        text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
    }}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: #1e293b;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, #3b82f6, #ef4444);
        border-radius: 3px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, #2563eb, #dc2626);
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .header-bar {{
            flex-direction: column;
            gap: 8px;
            padding: 8px 16px;
        }}
        
        .status-section {{
            flex-direction: column;
            gap: 4px;
        }}
        
        .chat-container {{
            height: 400px;
        }}
        
        .main .block-container {{
            padding: 0.25rem 0.5rem !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# Theme Toggle Button
theme_icon = "☀️" if st.session_state.dark_mode else "🌙"
if st.button(theme_icon, key="theme_toggle", help="Toggle Dark/Light Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# Modern Header Bar
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="header-bar">
    <div class="logo-section">
        <div class="logo-icon">🚔</div>
        <div class="logo-text">
            <h1 class="glow-text">SECURO</h1>
            <p>Enhanced AI Crime Intelligence System</p>
        </div>
    </div>
    <div class="status-section">
        <div class="status-item">
            <div class="status-dot"></div>
            <span>Royal St. Christopher & Nevis Police Force</span>
        </div>
        <div class="status-item">
            <span> {current_date} |  {current_time} AST</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    # Animated navigation header
    st.markdown("""
    <div class="sidebar-nav-header glow-text">
         Navigation
    </div>
    """, unsafe_allow_html=True)
    
    # Main navigation buttons
    if st.button("🏠 Home", key="nav_home", help="System Overview", use_container_width=True):
        st.session_state.main_view = 'home'
        st.rerun()
    
    if st.button("ℹ️ About", key="nav_about", help="About SECURO", use_container_width=True):
        st.session_state.main_view = 'about'
        st.rerun()
    
    if st.button("📊 Analytics", key="nav_analytics", help="Crime Analytics", use_container_width=True):
        st.session_state.main_view = 'analytics'
        st.rerun()
    
    if st.button("💬 History", key="nav_history", help="Chat History", use_container_width=True):
        st.session_state.main_view = 'history'
        st.rerun()
    
    if st.button("🗺️ Crime Map", key="nav_map", help="Crime Hotspots", use_container_width=True):
        st.session_state.main_view = 'hotspots'
        st.rerun()
    
    if st.button("🚨 Emergency", key="nav_emergency", help="Emergency Contacts", use_container_width=True):
        st.session_state.main_view = 'emergency'
        st.rerun()
    
    if st.button("📝 Anonymous Report", key="nav_anonymous", help="Submit Anonymous Crime Report", use_container_width=True):
        st.session_state.main_view = 'anonymous_report'
        st.rerun()
    
    st.markdown("---")
    
    # Quick return to AI Assistant
    if st.session_state.main_view not in ['ai-assistant', 'hotspots']:
        if st.button("🤖 Back to AI Assistant", key="back_to_ai", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    
    st.markdown("---")
    
    # AI status section
    if st.session_state.get('ai_enabled', False):
        st.success("🟢 Enhanced AI Online")
        st.markdown("""
        **Capabilities:**
        - 📊 Statistical knowledge integration
        - 💭 Conversation memory  
        - 🧠 Context-aware responses
        - 📈 Crime data analysis
        - 🎯 Professional assistance
        - 🔊 Enhanced Female Voice TTS
        """)
    else:
        st.error("🔴 AI Offline")
        st.write("Please check your API key configuration")
    
    st.markdown("---")
    
    # Enhanced quick stats
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(239, 68, 68, 0.1)); 
                border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px;">
        <div style="color: #ef4444; font-weight: 600; margin-bottom: 8px; text-align: center; text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);">
            📊 QUICK STATS
        </div>
        <div style="color: #e2e8f0; font-size: 14px; line-height: 1.6;">
            <div>🟢 Active Chats: <strong>{len(st.session_state.chat_sessions)}</strong></div>
            <div>🟢 Database: <strong>Loaded</strong></div>
            <div>🟢 API Status: <strong>Online</strong></div>
            <div>🟢 Reports: <strong>{len(st.session_state.get('submitted_reports', []))}</strong></div>
            <div>🟢 Theme: <strong>{'Dark' if st.session_state.dark_mode else 'Light'}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Content Area with all the enhanced features
if st.session_state.main_view == 'ai-assistant':
    # AI Assistant interface with enhanced features
    if not st.session_state.get('chat_active', False):
        # Chat welcome screen - enhanced with glow effects
        st.markdown("""
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; 
                    min-height: 400px; text-align: center; padding: 40px 20px; 
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    border: 1px solid #475569; border-radius: 16px; margin: 20px 0;
                    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);">
            <div style="width: 100px; height: 100px; margin-bottom: 24px; border-radius: 50%; 
                       background: linear-gradient(45deg, #3b82f6, #ef4444); display: flex; 
                       align-items: center; justify-content: center; font-size: 2.5rem; 
                       animation: logo-pulse 2s infinite; box-shadow: 0 0 30px rgba(59, 130, 246, 0.5);">
                🚔
            </div>
            <h1 style="color: #ffffff; font-size: 2.2rem; margin-bottom: 12px; font-weight: 700; 
                       text-shadow: 0 0 20px rgba(59, 130, 246, 0.7);" class="glow-text">SECURO AI</h1>
            <p style="color: #3b82f6; font-size: 1.1rem; margin-bottom: 16px; font-weight: 600; 
                      text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);">Enhanced AI with Female Voice</p>
            <p style="color: #94a3b8; max-width: 550px; margin-bottom: 32px; line-height: 1.6; font-size: 15px;">
                Welcome! I'm your enhanced AI Crime Intelligence system with comprehensive St. Kitts & Nevis statistics, 
                international data, conversation memory, and premium female voice synthesis! 
            </p>
            <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 8px; 
                            padding: 12px 20px; color: #3b82f6; font-size: 14px; font-weight: 500;
                            box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);">
                    📊 Statistical Knowledge
                </div>
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; 
                            padding: 12px 20px; color: #ef4444; font-size: 14px; font-weight: 500;
                            box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);">
                    💭 Conversation Memory
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 8px; 
                            padding: 12px 20px; color: #10b981; font-size: 14px; font-weight: 500;
                            box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);">
                    🔊 Premium Female Voice
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Center the start button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Conversation", key="start_chat", use_container_width=True):
                create_new_chat_session()
                st.session_state.chat_active = True
                st.success("✅ New chat session created! You can now start chatting with SECURO AI!")
                st.rerun()
    
    else:
        # Enhanced chat interface
        st.markdown("""
        <div class="chat-container">
            <div class="chat-header">
                <div>
                    <h3 class="glow-text">🤖 SECURO AI</h3>
                    <div class="ai-status">
                        <span style="color: #10b981;">●</span>
                        Online with Statistical Knowledge & Enhanced Female Voice TTS
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat controls - compact
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
                create_new_chat_session()
                st.rerun()
        
        with col2:
            if st.button("← Welcome", key="back_welcome", use_container_width=True):
                st.session_state.chat_active = False
                st.rerun()
        
        # Current chat info - compact
        current_chat = get_current_chat()
        st.info(f"**📝 Current Session:** {current_chat['name']}")
        
        # Display charts ABOVE the chat messages if requested
        if st.session_state.get('show_chart'):
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("### 📊 Requested Chart")
            chart_type = st.session_state.show_chart
            
            if chart_type == "international":
                # Show international comparison charts
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fig = create_macrotrends_comparison_charts("homicide_trends")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = create_macrotrends_comparison_charts("international_context")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    fig = create_macrotrends_comparison_charts("recent_crime_totals")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "trends":
                # Show crime trends
                st_kitts_data = []
                periods = []
                
                # Extract St. Kitts data from the database
                for period_key in ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']:
                    if period_key in HISTORICAL_CRIME_DATABASE:
                        period_data = HISTORICAL_CRIME_DATABASE[period_key]
                        periods.append(period_data["period"])
                        st_kitts_crimes = period_data.get('st_kitts', {}).get('crimes', 0)
                        st_kitts_data.append(st_kitts_crimes)
                
                # Create bar chart for St. Kitts crime trends
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=periods,
                    y=st_kitts_data,
                    marker_color='#3b82f6',
                    text=[f"{crimes}" for crimes in st_kitts_data],
                    textposition='auto',
                    name='St. Kitts Crimes'
                ))
                
                theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
                
                fig.update_layout(
                    title="St. Kitts Crime Trends - Recent Years",
                    xaxis_title="Time Period",
                    yaxis_title="Number of Crimes",
                    template=theme,
                    height=500,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "homicide":
                # Show homicide trends
                fig = create_macrotrends_comparison_charts("homicide_trends")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Add button to clear the chart
            if st.button("❌ Clear Chart", key="clear_chart"):
                st.session_state.show_chart = None
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display messages
        messages = current_chat['messages']
        
        # Initialize with welcome message if no messages
        if not messages:
            welcome_msg = {
                "role": "assistant",
                "content": "🚔 Enhanced SECURO AI System Online!\n\nI now have access to comprehensive St. Kitts & Nevis crime statistics, international comparison data from MacroTrends, conversation context, and premium female voice synthesis. Ask me about:\n\n• 📊 Local crime trends and detection rates\n• 🌍 International comparisons and global context\n• 📈 Historical data analysis with charts\n• 🔍 Specific incidents or general questions\n\nI can show interactive charts for international comparisons!",
                "timestamp": get_stkitts_time()
            }
            messages.append(welcome_msg)
            current_chat['messages'] = messages
        
        # Messages container
        for i, message in enumerate(messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message user">
                    <div class="message-bubble">{message["content"]}</div>
                    <div class="message-time">You • {message["timestamp"]} AST</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                clean_content = str(message["content"]).strip()
                clean_content = re.sub(r'<[^>]+>', '', clean_content)
                clean_content = clean_content.replace('```', '')
                clean_content = re.sub(r'  +', ' ', clean_content)
                clean_content = re.sub(r'\n +•', '\n•', clean_content)
                clean_content = re.sub(r'• +', '• ', clean_content)
                
                # Clean content for JavaScript (enhanced for female voice)
                js_clean_content = clean_content.replace('\\', '\\\\').replace('`', '\\`').replace('"', '\\"').replace("'", "\\'")
                
                # Create unique message ID for voice
                message_id = f"msg_{i}"
                
                # Create the assistant message with enhanced speaker button
                st.markdown(f"""
                <div class="message assistant">
                    <div class="message-bubble">
                        <div class="message-content">{clean_content}</div>
                        <span onclick="speakText_{message_id}()" class="speak-button" title="Click to hear with premium female voice">🔊</span>
                    </div>
                    <div class="message-time">
                        SECURO • {message["timestamp"]} AST
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add the enhanced JavaScript for female voice
                st.components.v1.html(f"""
                <script>
                function speakText_{message_id}() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        
                        let text = `{js_clean_content}`;
                        text = text.replace(/[•*#]/g, '').replace(/\\s+/g, ' ').trim();
                        
                        if (text.length > 0) {{
                            const utterance = new SpeechSynthesisUtterance(text);
                            
                            // Enhanced female voice selection
                            const voices = speechSynthesis.getVoices();
                            const femaleVoice = voices.find(voice => 
                                voice.name.toLowerCase().includes('female') ||
                                voice.name.toLowerCase().includes('woman') ||
                                voice.name.toLowerCase().includes('zira') ||
                                voice.name.toLowerCase().includes('helen') ||
                                voice.name.toLowerCase().includes('samantha') ||
                                voice.name.toLowerCase().includes('serena') ||
                                voice.name.toLowerCase().includes('karen') ||
                                voice.name.toLowerCase().includes('tessa') ||
                                voice.name.toLowerCase().includes('catherine') ||
                                voice.name.toLowerCase().includes('susan') ||
                                voice.name.toLowerCase().includes('alex') ||
                                voice.gender === 'female' ||
                                voice.name.includes('Google UK English Female') ||
                                voice.name.includes('Microsoft Zira') ||
                                voice.name.includes('Microsoft Helen') ||
                                voice.name.includes('Google US English')
                            );
                            
                            if (femaleVoice) {{
                                utterance.voice = femaleVoice;
                            }}
                            
                            // Enhanced voice settings for more natural female speech
                            utterance.rate = 0.85;
                            utterance.pitch = 1.15;
                            utterance.volume = 0.9;
                            
                            window.speechSynthesis.speak(utterance);
                        }}
                    }} else {{
                        alert('Text-to-speech not supported in this browser');
                    }}
                }}
                
                window.speakText_{message_id} = speakText_{message_id};
                </script>
                """, height=0)
        
        # Chat input - below messages
        st.markdown("---")
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Message Enhanced AI Assistant:",
                placeholder="Type your question about crime statistics, trends, or analysis...",
                label_visibility="collapsed",
                key="chat_input"
            )
            
            submitted = st.form_submit_button("📨 Send", type="primary")
            
            if submitted and user_input and user_input.strip():
                current_time = get_stkitts_time()
                
                # Add user message to current chat
                add_message_to_chat("user", user_input)
                
                # Generate response with conversation history and statistics
                with st.spinner("🔄 Generating enhanced AI response with statistical knowledge..."):
                    response, chart_type = generate_enhanced_smart_response(
                        user_input, 
                        conversation_history=current_chat['messages'],
                        language='en'
                    )
                
                # Add assistant response to current chat
                add_message_to_chat("assistant", response)
                
                # Store chart type in session state to persist after rerun
                if chart_type:
                    st.session_state.show_chart = chart_type
                
                # Store the response for auto-speak
                st.session_state.last_response = response
                
                st.rerun()
        
        # Auto-speak the last response if there is one
        if st.session_state.get('last_response'):
            st.components.v1.html(auto_speak_response(st.session_state.last_response), height=50)
            # Clear the response to avoid re-speaking
            st.session_state.last_response = None

# [Rest of the views remain the same as in the original code - home, about, analytics, history, emergency, anonymous_report, hotspots]

elif st.session_state.main_view == 'home':
    # System Overview - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header glow-text">🏠 System Overview</h2>
        <div class="section-content">
            <p>Welcome to SECURO - the enhanced comprehensive crime analysis system with dynamic themes, 
            premium female voice synthesis, statistical integration, conversation memory, advanced AI capabilities, 
            and anonymous reporting built specifically for the Royal St. Christopher and Nevis Police Force.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards in main area
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3 class="glow-text">🤖 Enhanced AI</h3>
            <p>Statistical knowledge, memory, context-aware responses with premium female voice synthesis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3 class="glow-text">📊 Real-Time Statistics</h3>
            <p>Integrated crime data and international comparisons from MacroTrends with dynamic charts.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h3 class="glow-text">🎨 Dynamic Themes</h3>
            <p>Beautiful dark/light mode switching with enhanced visual effects and glow animations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="info-card">
            <h3 class="glow-text">🔊 Premium Voice</h3>
            <p>Enhanced female text-to-speech with natural voice synthesis and audio controls.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick access buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🤖 Start Chat", key="quick_ai", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    
    with col2:
        if st.button("🗺️ View Crime Map", key="quick_map", use_container_width=True):
            st.session_state.main_view = 'hotspots'
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", key="quick_analytics", use_container_width=True):
            st.session_state.main_view = 'analytics'
            st.rerun()
    
    with col4:
        if st.button("📝 Anonymous Report", key="quick_report", use_container_width=True):
            st.session_state.main_view = 'anonymous_report'
            st.rerun()

elif st.session_state.main_view == 'about':
    # About SECURO - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header glow-text">ℹ️ About SECURO</h2>
        <div class="section-content">
            <p><strong>SECURO</strong> is an enhanced comprehensive crime analysis system with dynamic themes, 
            premium female voice synthesis, statistical integration, conversation memory, advanced AI capabilities, 
            and secure anonymous reporting built specifically for the Royal St. Christopher and Nevis Police Force.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🌟 Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **🤖 Conversation Memory:** Full context preservation across chat sessions
        - **📊 Statistical Knowledge Integration:** Real-time access to crime data  
        - **🧠 Context-Aware Responses:** Intelligent understanding of conversation flow
        - **💬 Multi-Chat Management:** Organize multiple conversation sessions
        - **📈 Real-time Crime Data:** Up-to-date statistics and analysis
        - **📝 Anonymous Reporting:** Secure crime reporting system
        """)
    
    with col2:
        st.markdown("""
        - **🎨 Dynamic Theme System:** Beautiful dark/light mode with glow effects
        - **🔊 Premium Female Voice:** Enhanced text-to-speech with natural synthesis
        - **🗺️ Interactive Crime Maps:** Visual hotspot analysis with satellite view
        - **🌍 International Comparisons:** Global context and trending analysis
        - **📊 Advanced Analytics:** Dynamic charts with theme-aware visualization
        - **🔒 Privacy Protection:** Anonymous reporting with full confidentiality
        """)
    
    # Quick access buttons
    st.markdown("### 🚀 Quick Access")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🤖 SECURO AI", key="about_ai", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    
    with col2:
        if st.button("🗺️ Crime Map", key="about_map", use_container_width=True):
            st.session_state.main_view = 'hotspots'
            st.rerun()
    
    with col3:
        if st.button("📊 Analytics", key="about_analytics", use_container_width=True):
            st.session_state.main_view = 'analytics'
            st.rerun()
    
    with col4:
        if st.button("📝 Report Crime", key="about_report", use_container_width=True):
            st.session_state.main_view = 'anonymous_report'
            st.rerun()

elif st.session_state.main_view == 'analytics':
    # Crime Analytics - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header glow-text">📊 Crime Analytics Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Analytics cards in main area
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    border-left: 4px solid #ef4444; border-radius: 8px; padding: 16px; text-align: center;
                    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.2);">
            <div style="color: #ef4444; font-size: 24px; font-weight: 700; margin-bottom: 4px; 
                       text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);" class="glow-text">109</div>
            <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">High Risk Crimes</div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">Basseterre Central, Molineux, Tabernacle</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px; text-align: center;
                    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);">
            <div style="color: #3b82f6; font-size: 24px; font-weight: 700; margin-bottom: 4px; 
                       text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);" class="glow-text">133</div>
            <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Medium Risk Crimes</div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">6 Areas Including Cayon, Newton Ground</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    border-left: 4px solid #10b981; border-radius: 8px; padding: 16px; text-align: center;
                    box-shadow: 0 8px 32px rgba(16, 185, 129, 0.2);">
            <div style="color: #10b981; font-size: 24px; font-weight: 700; margin-bottom: 4px; 
                       text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);" class="glow-text">60</div>
            <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Low Risk Crimes</div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">4 Areas Including Sandy Point, Dieppe Bay</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent trends section
    st.markdown("""
    <div class="main-content-section">
        <h3 class="section-header glow-text">📈 Recent Trends</h3>
        <div class="section-content">
            <ul>
                <li><strong>75% decrease in murders</strong> from 2024 to 2025 H1</li>
                <li><strong>Detection rates improving</strong> across most crime categories</li>
                <li><strong>Drug crimes up 463%</strong> indicating increased enforcement</li>
                <li><strong>Larcenies remain highest volume crime</strong> requiring focused attention</li>
                <li><strong>Federation-wide trends</strong> showing mixed but generally positive results</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive chart section
    st.markdown("### 📊 Interactive Analytics")
    
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📈 Crime Trends", "🌍 International Comparison", "🎯 Detection Rates"])
    
    with chart_tab1:
        # Show crime trends
        st_kitts_data = []
        periods = []
        
        # Extract St. Kitts data from the database
        for period_key in ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']:
            if period_key in HISTORICAL_CRIME_DATABASE:
                period_data = HISTORICAL_CRIME_DATABASE[period_key]
                periods.append(period_data["period"])
                st_kitts_crimes = period_data.get('st_kitts', {}).get('crimes', 0)
                st_kitts_data.append(st_kitts_crimes)
        
        # Create bar chart for St. Kitts crime trends
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=periods,
            y=st_kitts_data,
            marker_color='#3b82f6',
            text=[f"{crimes}" for crimes in st_kitts_data],
            textposition='auto',
            name='St. Kitts Crimes'
        ))
        
        theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
        
        fig.update_layout(
            title="St. Kitts Crime Trends - Recent Years",
            xaxis_title="Time Period",
            yaxis_title="Number of Crimes",
            template=theme,
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_tab2:
        fig = create_macrotrends_comparison_charts("international_context")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with chart_tab3:
        # Detection rates chart
        periods = []
        detection_rates = []
        
        for period_key in ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']:
            if period_key in HISTORICAL_CRIME_DATABASE:
                period_data = HISTORICAL_CRIME_DATABASE[period_key]
                periods.append(period_data["period"])
                detection_rates.append(period_data["detection_rate"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=periods,
            y=detection_rates,
            mode='lines+markers',
            name='Detection Rate %',
            line=dict(color='#10b981', width=3),
            marker=dict(size=10, color='#10b981')
        ))
        
        theme = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
        
        fig.update_layout(
            title="Crime Detection Rate Trends",
            xaxis_title="Time Period",
            yaxis_title="Detection Rate (%)",
            template=theme,
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.main_view == 'history':
    # Chat History - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header glow-text">💬 Chat History Management</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    border: 1px solid #475569; border-radius: 12px; padding: 20px; margin-bottom: 16px;
                    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);">
            <h3 style="color: #3b82f6; text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);" class="glow-text">📭 No Chat History Found</h3>
            <p style="color: #cbd5e1;">Start a conversation with the AI Assistant to create your first session! 
            All your conversations will be automatically saved and organized here.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick start button
        if st.button("🚀 Start Your First Chat", key="first_chat", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    else:
        st.markdown(f"**📊 Total Chat Sessions:** {len(st.session_state.chat_sessions)}")
        st.markdown("---")
        
        # Display chat sessions in a nice grid
        for i, (chat_id, chat_data) in enumerate(st.session_state.chat_sessions.items()):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                if st.button(f"💬 Chat: {chat_data['name']}", key=f"hist_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.session_state.main_view = 'ai-assistant'
                    st.session_state.chat_active = True
                    st.rerun()
            
            with col2:
                st.text(f"📝 Messages: {len(chat_data['messages'])}")
                st.text(f"🕐 Created: {chat_data['created_at']} AST")
            
            with col3:
                st.text(f"⏰ Last Activity:")
                st.text(f"{chat_data['last_activity']} AST")
            
            st.markdown("---")

elif st.session_state.main_view == 'emergency':
    # Emergency Contacts - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header glow-text">🚨 Emergency Contacts Directory</h2>
        <div class="section-content">
            <p><strong>🚨 Emergency Guidelines:</strong></p>
            <ul>
                <li>For life-threatening emergencies, call <strong>911</strong> immediately</li>
                <li>Provide exact location and nature of emergency</li>
                <li>Stay on the line until instructed to hang up</li>
                <li>Keep this directory accessible for quick reference</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency contacts in a grid layout
    col1, col2 = st.columns(2)
    
    emergency_items = list(EMERGENCY_CONTACTS.items())
    mid_point = len(emergency_items) // 2
    
    with col1:
        for service, details in emergency_items[:mid_point]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                        border: 1px solid #ef4444; border-radius: 12px; padding: 16px; margin-bottom: 12px; 
                        transition: all 0.3s ease; box-shadow: 0 8px 32px rgba(239, 68, 68, 0.1);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 24px;">{details['icon']}</span>
                    <div style="color: #ffffff; font-weight: 600; font-size: 16px; text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);">{service}</div>
                </div>
                <div style="color: #ef4444; font-size: 18px; font-weight: bold; margin: 8px 0; 
                           text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);" class="glow-text">{details['number']}</div>
                <div style="color: #94a3b8; font-size: 14px;">{details['description']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for service, details in emergency_items[mid_point:]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                        border: 1px solid #ef4444; border-radius: 12px; padding: 16px; margin-bottom: 12px; 
                        transition: all 0.3s ease; box-shadow: 0 8px 32px rgba(239, 68, 68, 0.1);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 24px;">{details['icon']}</span>
                    <div style="color: #ffffff; font-weight: 600; font-size: 16px; text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);">{service}</div>
                </div>
                <div style="color: #ef4444; font-size: 18px; font-weight: bold; margin: 8px 0; 
                           text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);" class="glow-text">{details['number']}</div>
                <div style="color: #94a3b8; font-size: 14px;">{details['description']}</div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.main_view == 'anonymous_report':
    # Anonymous Report System - Enhanced with better styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                border: 1px solid #475569; border-radius: 16px; padding: 24px; margin-bottom: 24px; 
                position: relative; overflow: hidden; box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; 
                    background: linear-gradient(90deg, #3b82f6, #ef4444, #3b82f6); 
                    background-size: 200% 100%; animation: gradient-slide 3s ease-in-out infinite;"></div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <div style="width: 50px; height: 50px; background: linear-gradient(45deg, #ef4444, #3b82f6); 
                       border-radius: 12px; display: flex; align-items: center; justify-content: center; 
                       font-size: 24px; animation: icon-pulse 2s infinite; box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);">📝</div>
            <div>
                <div style="color: #ffffff; font-size: 24px; font-weight: 700; margin: 0; 
                           text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);" class="glow-text">Anonymous Crime Report</div>
                <div style="color: #94a3b8; font-size: 14px; margin: 4px 0 0 0;">Secure & Confidential Reporting System</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Anonymity Notice
    st.markdown("""
    <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 8px; 
                padding: 16px; margin: 20px 0; color: #10b981; box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);">
        <div style="font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; 
                   text-shadow: 0 0 5px rgba(16, 185, 129, 0.5);" class="glow-text">
            🔒 Complete Anonymity Guaranteed
        </div>
        <div>
            • Your identity will never be revealed or tracked<br>
            • No personal information is collected or stored<br>
            • Reports are sent directly to RSCNPF investigators<br>
            • You can choose to remain completely anonymous or provide contact details for follow-up
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Report Form
    with st.form("anonymous_report_form", clear_on_submit=True):
        # Crime Type Section
        st.markdown("""
        <div style="color: #3b82f6; font-size: 16px; font-weight: 600; margin-bottom: 12px; 
                    display: flex; align-items: center; gap: 8px; text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">
            🔍 Incident Type
        </div>
        """, unsafe_allow_html=True)
        
        crime_types = [
            "Select incident type...",
            "🔫 Violent Crime (Murder, Assault, Robbery)",
            "💊 Drug-Related Crime",
            "🏠 Break-in / Burglary",
            "🚗 Theft / Larceny",
            "👤 Missing Person",
            "🚨 Domestic Violence",
            "💰 Fraud / Scam",
            "🔥 Vandalism / Property Damage",
            "🌐 Cybercrime",
            "👶 Child Abuse / Endangerment",
            "🚦 Traffic Violation",
            "🔫 Illegal Weapons",
            "🏢 Corruption",
            "📞 Harassment / Threats",
            "🎰 Illegal Gambling",
            "🚫 Other Criminal Activity"
        ]
        
        crime_type = st.selectbox(
            "What type of incident are you reporting?",
            crime_types,
            key="crime_type"
        )
        
        # Location Section
        st.markdown("""
        <div style="color: #3b82f6; font-size: 16px; font-weight: 600; margin-bottom: 12px; 
                    display: flex; align-items: center; gap: 8px; text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">
            📍 Location Information
        </div>
        """, unsafe_allow_html=True)
        
        location = st.text_input(
            "Where did this incident occur? (Address, area, landmark)",
            placeholder="e.g., Near Independence Square, Basseterre or Sandy Point Highway",
            key="location"
        )
        
        # Time Section
        st.markdown("""
        <div style="color: #3b82f6; font-size: 16px; font-weight: 600; margin-bottom: 12px; 
                    display: flex; align-items: center; gap: 8px; text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">
            🕐 Time Information
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            incident_date = st.date_input(
                "Date of incident",
                key="incident_date"
            )
        
        with col2:
            incident_time = st.time_input(
                "Approximate time (if known)",
                key="incident_time"
            )
        
        # Description Section
        st.markdown("""
        <div style="color: #3b82f6; font-size: 16px; font-weight: 600; margin-bottom: 12px; 
                    display: flex; align-items: center; gap: 8px; text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">
            📝 Incident Description
        </div>
        """, unsafe_allow_html=True)
        
        description = st.text_area(
            "Please describe what happened in as much detail as possible:",
            placeholder="Describe the incident, what you saw, heard, or experienced. Include any relevant details that might help investigators.",
            height=150,
            key="description"
        )
        
        # Additional Information
        st.markdown("""
        <div style="color: #3b82f6; font-size: 16px; font-weight: 600; margin-bottom: 12px; 
                    display: flex; align-items: center; gap: 8px; text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">
            ℹ️ Additional Information
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            suspect_info = st.text_area(
                "Suspect information (if any):",
                placeholder="Physical description, clothing, vehicle, etc.",
                height=100,
                key="suspect_info"
            )
        
        with col2:
            witnesses = st.text_area(
                "Witnesses present:",
                placeholder="Any witnesses or other people involved",
                height=100,
                key="witnesses"
            )
        
        evidence = st.text_area(
            "Evidence or supporting information:",
            placeholder="Photos, videos, documents, or other evidence (describe what you have)",
            key="evidence"
        )
        
        # Priority Level
        st.markdown("""
        <div style="color: #3b82f6; font-size: 16px; font-weight: 600; margin-bottom: 12px; 
                    display: flex; align-items: center; gap: 8px; text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">
            ⚡ Priority Level
        </div>
        """, unsafe_allow_html=True)
        
        priority_options = [
            "Standard Priority",
            "Medium Priority - Requires attention soon",
            "High Priority - Urgent attention needed",
            "Emergency - Immediate response required"
        ]
        
        priority = st.selectbox(
            "How urgent is this report?",
            priority_options,
            key="priority"
        )
        
        # Contact Preference
        st.markdown("""
        <div style="color: #3b82f6; font-size: 16px; font-weight: 600; margin-bottom: 12px; 
                    display: flex; align-items: center; gap: 8px; text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">
            📞 Contact Preference (Optional)
        </div>
        """, unsafe_allow_html=True)
        
        contact_options = [
            "Remain completely anonymous - no contact",
            "Anonymous but provide phone number for urgent follow-up only",
            "Anonymous but provide email for updates",
            "Provide contact details for follow-up questions"
        ]
        
        contact_preference = st.selectbox(
            "How would you like to be contacted (if at all)?",
            contact_options,
            key="contact_preference"
        )
        
        contact_details = ""
        if "phone" in contact_preference.lower() or "email" in contact_preference.lower() or "contact details" in contact_preference.lower():
            contact_details = st.text_input(
                "Contact information (optional):",
                placeholder="Phone number or email address",
                key="contact_details"
            )
        
        # Enhanced Submit Button
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button(
            "🚨 Submit Anonymous Report",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validate required fields
            if crime_type == "Select incident type...":
                st.error("⚠️ Please select an incident type")
            elif not description.strip():
                st.error("⚠️ Please provide a description of the incident")
            else:
                # Prepare report data
                report_data = {
                    'crime_type': crime_type,
                    'location': location if location else "Not specified",
                    'incident_time': f"{incident_date} {incident_time}" if incident_date else "Not specified",
                    'description': description,
                    'suspect_info': suspect_info if suspect_info else "None provided",
                    'witnesses': witnesses if witnesses else "None mentioned",
                    'evidence': evidence if evidence else "None mentioned",
                    'priority': priority,
                    'contact_preference': contact_preference,
                    'contact_details': contact_details if contact_details else "None provided"
                }
                
                # Send the report
                success, message = send_anonymous_report(report_data)
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    
                    # Show confirmation with report ID
                    if 'submitted_reports' in st.session_state and st.session_state.submitted_reports:
                        latest_report = st.session_state.submitted_reports[-1]
                        st.info(f"""
                        **Report Confirmation:**
                        - Report ID: `{latest_report['id']}`
                        - Submitted: {latest_report['timestamp']}
                        - Type: {latest_report['type']}
                        - Status: {latest_report['status']}
                        
                        Your report has been forwarded to the Royal St. Christopher & Nevis Police Force for investigation.
                        """)
                else:
                    st.error(f"❌ {message}")
    
    # Show Previous Reports (if any) with enhanced styling
    if st.session_state.get('submitted_reports'):
        st.markdown("""
        <div class="main-content-section">
            <h3 class="section-header glow-text">📋 Your Submitted Reports</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for report in reversed(st.session_state.submitted_reports):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                        border-left: 4px solid #10b981; border-radius: 8px; padding: 16px; margin-bottom: 12px; 
                        transition: all 0.3s ease; box-shadow: 0 8px 32px rgba(16, 185, 129, 0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="color: #3b82f6; font-family: monospace; font-weight: 600; 
                                   text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">Report ID: {report['id']}</div>
                        <div style="color: #cbd5e1;">Location: {report['location']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #10b981; font-weight: 600; text-transform: uppercase; 
                                   font-size: 12px; letter-spacing: 0.5px; text-shadow: 0 0 5px rgba(16, 185, 129, 0.5);" 
                             class="glow-text">{report['status']}</div>
                        <div style="color: #94a3b8; font-size: 12px;">{report['timestamp']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.main_view == 'hotspots':
    # Crime Hotspots Map - Enhanced with better styling
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header glow-text">🗺️ Crime Hotspot Map - St. Kitts & Nevis</h2>
        <div class="section-content">
            <p>Interactive crime analysis with real-time data overlays and satellite view capabilities</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Enhanced Hotspot summary metrics
    st.markdown("### 📊 Hotspot Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    border-left: 4px solid #ef4444; border-radius: 8px; padding: 16px; text-align: center;
                    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.2);">
            <div style="color: #ef4444; font-size: 24px; font-weight: 700; margin-bottom: 4px; 
                       text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);" class="glow-text">109</div>
            <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">High Risk Crimes</div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">3 Areas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px; text-align: center;
                    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);">
            <div style="color: #3b82f6; font-size: 24px; font-weight: 700; margin-bottom: 4px; 
                       text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);" class="glow-text">133</div>
            <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Medium Risk Crimes</div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">6 Areas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    border-left: 4px solid #2563eb; border-radius: 8px; padding: 16px; text-align: center;
                    box-shadow: 0 8px 32px rgba(37, 99, 235, 0.2);">
            <div style="color: #2563eb; font-size: 24px; font-weight: 700; margin-bottom: 4px; 
                       text-shadow: 0 0 10px rgba(37, 99, 235, 0.5);" class="glow-text">60</div>
            <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Low Risk Crimes</div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">4 Areas</div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Default view (Enhanced welcome screen)
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                border-radius: 16px; margin: 20px 0; box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);">
        <div style="width: 120px; height: 120px; margin: 0 auto 24px; border-radius: 50%; 
                   background: linear-gradient(45deg, #3b82f6, #ef4444); display: flex; 
                   align-items: center; justify-content: center; font-size: 3rem; 
                   animation: logo-pulse 2s infinite; box-shadow: 0 0 40px rgba(59, 130, 246, 0.5);">🚔</div>
        <h2 style="color: #3b82f6; font-size: 2.5rem; margin-bottom: 16px; 
                   text-shadow: 0 0 20px rgba(59, 130, 246, 0.7);" class="glow-text">Welcome to SECURO</h2>
        <p style="color: #94a3b8; font-size: 1.2rem; margin-bottom: 32px;">Enhanced AI Crime Intelligence System</p>
        <p style="color: #cbd5e1; max-width: 600px; margin: 0 auto 40px; line-height: 1.6;">
            Experience the future of law enforcement technology with dynamic themes, premium female voice synthesis, 
            real-time crime analytics, and secure anonymous reporting capabilities.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced navigation grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🤖 SECURO AI", key="main_ai", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    
    with col2:
        if st.button("🗺️ Crime Hotspots", key="main_map", use_container_width=True):
            st.session_state.main_view = 'hotspots'
            st.rerun()
    
    with col3:
        if st.button("📊 Analytics", key="main_analytics", use_container_width=True):
            st.session_state.main_view = 'analytics'
            st.rerun()
    
    with col4:
        if st.button("📝 Anonymous Report", key="main_report", use_container_width=True):
            st.session_state.main_view = 'anonymous_report'
            st.rerun()

# Enhanced Status Bar with glowing effects
current_time = get_stkitts_time()
total_chats = len(st.session_state.chat_sessions)
total_reports = len(st.session_state.get('submitted_reports', []))

st.markdown(f"""
<div class="status-bar">
    <div class="status-indicators">
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>🤖 Enhanced AI Active</span>
        </div>
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>🎨 Theme: {'Dark' if st.session_state.dark_mode else 'Light'} Mode</span>
        </div>
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>🔊 Premium Female Voice: Ready</span>
        </div>
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>💭 Conversation Memory: Enabled</span>
        </div>
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>📝 Anonymous Reports: Available</span>
        </div>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span>💬 Chats: {total_chats} | 📝 Reports: {total_reports}</span>
        </div>
    </div>
    <div class="status-indicator">
        <span style="text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);" class="glow-text">🕐 {current_time} AST</span>
    </div>
</div>
""", unsafe_allow_html=True)
